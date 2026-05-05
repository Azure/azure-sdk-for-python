```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.support

    class azure.mgmt.support.MicrosoftSupport: implements ContextManager 
        chat_transcripts: ChatTranscriptsOperations
        chat_transcripts_no_subscription: ChatTranscriptsNoSubscriptionOperations
        communications: CommunicationsOperations
        communications_no_subscription: CommunicationsNoSubscriptionOperations
        file_workspaces: FileWorkspacesOperations
        file_workspaces_no_subscription: FileWorkspacesNoSubscriptionOperations
        files: FilesOperations
        files_no_subscription: FilesNoSubscriptionOperations
        operations: Operations
        problem_classifications: ProblemClassificationsOperations
        services: ServicesOperations
        support_tickets: SupportTicketsOperations
        support_tickets_no_subscription: SupportTicketsNoSubscriptionOperations

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


namespace azure.mgmt.support.aio

    class azure.mgmt.support.aio.MicrosoftSupport: implements AsyncContextManager 
        chat_transcripts: ChatTranscriptsOperations
        chat_transcripts_no_subscription: ChatTranscriptsNoSubscriptionOperations
        communications: CommunicationsOperations
        communications_no_subscription: CommunicationsNoSubscriptionOperations
        file_workspaces: FileWorkspacesOperations
        file_workspaces_no_subscription: FileWorkspacesNoSubscriptionOperations
        files: FilesOperations
        files_no_subscription: FilesNoSubscriptionOperations
        operations: Operations
        problem_classifications: ProblemClassificationsOperations
        services: ServicesOperations
        support_tickets: SupportTicketsOperations
        support_tickets_no_subscription: SupportTicketsNoSubscriptionOperations

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


namespace azure.mgmt.support.aio.operations

    class azure.mgmt.support.aio.operations.ChatTranscriptsNoSubscriptionOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                support_ticket_name: str, 
                chat_transcript_name: str, 
                **kwargs: Any
            ) -> ChatTranscriptDetails: ...

        @distributed_trace
        def list(
                self, 
                support_ticket_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[ChatTranscriptDetails]: ...


    class azure.mgmt.support.aio.operations.ChatTranscriptsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                support_ticket_name: str, 
                chat_transcript_name: str, 
                **kwargs: Any
            ) -> ChatTranscriptDetails: ...

        @distributed_trace
        def list(
                self, 
                support_ticket_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[ChatTranscriptDetails]: ...


    class azure.mgmt.support.aio.operations.CommunicationsNoSubscriptionOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                support_ticket_name: str, 
                communication_name: str, 
                create_communication_parameters: CommunicationDetails, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CommunicationDetails]: ...

        @overload
        async def begin_create(
                self, 
                support_ticket_name: str, 
                communication_name: str, 
                create_communication_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CommunicationDetails]: ...

        @overload
        async def check_name_availability(
                self, 
                support_ticket_name: str, 
                check_name_availability_input: CheckNameAvailabilityInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityOutput: ...

        @overload
        async def check_name_availability(
                self, 
                support_ticket_name: str, 
                check_name_availability_input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityOutput: ...

        @distributed_trace_async
        async def get(
                self, 
                support_ticket_name: str, 
                communication_name: str, 
                **kwargs: Any
            ) -> CommunicationDetails: ...

        @distributed_trace
        def list(
                self, 
                support_ticket_name: str, 
                top: Optional[int] = None, 
                filter: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncIterable[CommunicationDetails]: ...


    class azure.mgmt.support.aio.operations.CommunicationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                support_ticket_name: str, 
                communication_name: str, 
                create_communication_parameters: CommunicationDetails, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CommunicationDetails]: ...

        @overload
        async def begin_create(
                self, 
                support_ticket_name: str, 
                communication_name: str, 
                create_communication_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CommunicationDetails]: ...

        @overload
        async def check_name_availability(
                self, 
                support_ticket_name: str, 
                check_name_availability_input: CheckNameAvailabilityInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityOutput: ...

        @overload
        async def check_name_availability(
                self, 
                support_ticket_name: str, 
                check_name_availability_input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityOutput: ...

        @distributed_trace_async
        async def get(
                self, 
                support_ticket_name: str, 
                communication_name: str, 
                **kwargs: Any
            ) -> CommunicationDetails: ...

        @distributed_trace
        def list(
                self, 
                support_ticket_name: str, 
                top: Optional[int] = None, 
                filter: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncIterable[CommunicationDetails]: ...


    class azure.mgmt.support.aio.operations.FileWorkspacesNoSubscriptionOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def create(
                self, 
                file_workspace_name: str, 
                **kwargs: Any
            ) -> FileWorkspaceDetails: ...

        @distributed_trace_async
        async def get(
                self, 
                file_workspace_name: str, 
                **kwargs: Any
            ) -> FileWorkspaceDetails: ...


    class azure.mgmt.support.aio.operations.FileWorkspacesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def create(
                self, 
                file_workspace_name: str, 
                **kwargs: Any
            ) -> FileWorkspaceDetails: ...

        @distributed_trace_async
        async def get(
                self, 
                file_workspace_name: str, 
                **kwargs: Any
            ) -> FileWorkspaceDetails: ...


    class azure.mgmt.support.aio.operations.FilesNoSubscriptionOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create(
                self, 
                file_workspace_name: str, 
                file_name: str, 
                create_file_parameters: FileDetails, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FileDetails: ...

        @overload
        async def create(
                self, 
                file_workspace_name: str, 
                file_name: str, 
                create_file_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FileDetails: ...

        @distributed_trace_async
        async def get(
                self, 
                file_workspace_name: str, 
                file_name: str, 
                **kwargs: Any
            ) -> FileDetails: ...

        @distributed_trace
        def list(
                self, 
                file_workspace_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[FileDetails]: ...

        @overload
        async def upload(
                self, 
                file_workspace_name: str, 
                file_name: str, 
                upload_file: UploadFile, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def upload(
                self, 
                file_workspace_name: str, 
                file_name: str, 
                upload_file: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.support.aio.operations.FilesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create(
                self, 
                file_workspace_name: str, 
                file_name: str, 
                create_file_parameters: FileDetails, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FileDetails: ...

        @overload
        async def create(
                self, 
                file_workspace_name: str, 
                file_name: str, 
                create_file_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FileDetails: ...

        @distributed_trace_async
        async def get(
                self, 
                file_workspace_name: str, 
                file_name: str, 
                **kwargs: Any
            ) -> FileDetails: ...

        @distributed_trace
        def list(
                self, 
                file_workspace_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[FileDetails]: ...

        @overload
        async def upload(
                self, 
                file_workspace_name: str, 
                file_name: str, 
                upload_file: UploadFile, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def upload(
                self, 
                file_workspace_name: str, 
                file_name: str, 
                upload_file: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.support.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncIterable[Operation]: ...


    class azure.mgmt.support.aio.operations.ProblemClassificationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                service_name: str, 
                problem_classification_name: str, 
                **kwargs: Any
            ) -> ProblemClassification: ...

        @distributed_trace
        def list(
                self, 
                service_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[ProblemClassification]: ...


    class azure.mgmt.support.aio.operations.ServicesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                service_name: str, 
                **kwargs: Any
            ) -> Service: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncIterable[Service]: ...


    class azure.mgmt.support.aio.operations.SupportTicketsNoSubscriptionOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                support_ticket_name: str, 
                create_support_ticket_parameters: SupportTicketDetails, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SupportTicketDetails]: ...

        @overload
        async def begin_create(
                self, 
                support_ticket_name: str, 
                create_support_ticket_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SupportTicketDetails]: ...

        @overload
        async def check_name_availability(
                self, 
                check_name_availability_input: CheckNameAvailabilityInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityOutput: ...

        @overload
        async def check_name_availability(
                self, 
                check_name_availability_input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityOutput: ...

        @distributed_trace_async
        async def get(
                self, 
                support_ticket_name: str, 
                **kwargs: Any
            ) -> SupportTicketDetails: ...

        @distributed_trace
        def list(
                self, 
                top: Optional[int] = None, 
                filter: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncIterable[SupportTicketDetails]: ...

        @overload
        async def update(
                self, 
                support_ticket_name: str, 
                update_support_ticket: UpdateSupportTicket, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SupportTicketDetails: ...

        @overload
        async def update(
                self, 
                support_ticket_name: str, 
                update_support_ticket: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SupportTicketDetails: ...


    class azure.mgmt.support.aio.operations.SupportTicketsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                support_ticket_name: str, 
                create_support_ticket_parameters: SupportTicketDetails, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SupportTicketDetails]: ...

        @overload
        async def begin_create(
                self, 
                support_ticket_name: str, 
                create_support_ticket_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SupportTicketDetails]: ...

        @overload
        async def check_name_availability(
                self, 
                check_name_availability_input: CheckNameAvailabilityInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityOutput: ...

        @overload
        async def check_name_availability(
                self, 
                check_name_availability_input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityOutput: ...

        @distributed_trace_async
        async def get(
                self, 
                support_ticket_name: str, 
                **kwargs: Any
            ) -> SupportTicketDetails: ...

        @distributed_trace
        def list(
                self, 
                top: Optional[int] = None, 
                filter: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncIterable[SupportTicketDetails]: ...

        @overload
        async def update(
                self, 
                support_ticket_name: str, 
                update_support_ticket: UpdateSupportTicket, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SupportTicketDetails: ...

        @overload
        async def update(
                self, 
                support_ticket_name: str, 
                update_support_ticket: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SupportTicketDetails: ...


namespace azure.mgmt.support.models

    class azure.mgmt.support.models.ChatTranscriptDetails(ProxyResource):
        id: str
        messages: list[MessageProperties]
        name: str
        start_time: datetime
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                messages: Optional[List[MessageProperties]] = ..., 
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


    class azure.mgmt.support.models.ChatTranscriptsListResult(Model):
        next_link: str
        value: list[ChatTranscriptDetails]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[ChatTranscriptDetails]] = ..., 
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


    class azure.mgmt.support.models.CheckNameAvailabilityInput(Model):
        name: str
        type: Union[str, Type]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                name: str, 
                type: Union[str, Type], 
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


    class azure.mgmt.support.models.CheckNameAvailabilityOutput(Model):
        message: str
        name_available: bool
        reason: str

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


    class azure.mgmt.support.models.CommunicationDetails(Model):
        body: str
        communication_direction: Union[str, CommunicationDirection]
        communication_type: Union[str, CommunicationType]
        created_date: datetime
        id: str
        name: str
        sender: str
        subject: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                body: str, 
                sender: Optional[str] = ..., 
                subject: str, 
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


    class azure.mgmt.support.models.CommunicationDirection(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INBOUND = "inbound"
        OUTBOUND = "outbound"


    class azure.mgmt.support.models.CommunicationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PHONE = "phone"
        WEB = "web"


    class azure.mgmt.support.models.CommunicationsListResult(Model):
        next_link: str
        value: list[CommunicationDetails]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[CommunicationDetails]] = ..., 
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


    class azure.mgmt.support.models.Consent(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NO = "No"
        YES = "Yes"


    class azure.mgmt.support.models.ContactProfile(Model):
        additional_email_addresses: list[str]
        country: str
        first_name: str
        last_name: str
        phone_number: str
        preferred_contact_method: Union[str, PreferredContactMethod]
        preferred_support_language: str
        preferred_time_zone: str
        primary_email_address: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                additional_email_addresses: Optional[List[str]] = ..., 
                country: str, 
                first_name: str, 
                last_name: str, 
                phone_number: Optional[str] = ..., 
                preferred_contact_method: Union[str, PreferredContactMethod], 
                preferred_support_language: str, 
                preferred_time_zone: str, 
                primary_email_address: str, 
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


    class azure.mgmt.support.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.support.models.ErrorAdditionalInfo(Model):
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


    class azure.mgmt.support.models.ErrorDetail(Model):
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


    class azure.mgmt.support.models.ErrorResponse(Model):
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


    class azure.mgmt.support.models.FileDetails(ProxyResource):
        chunk_size: int
        created_on: datetime
        file_size: int
        id: str
        name: str
        number_of_chunks: int
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                chunk_size: Optional[int] = ..., 
                file_size: Optional[int] = ..., 
                number_of_chunks: Optional[int] = ..., 
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


    class azure.mgmt.support.models.FileWorkspaceDetails(ProxyResource):
        created_on: datetime
        expiration_time: datetime
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


    class azure.mgmt.support.models.FilesListResult(Model):
        next_link: str
        value: list[FileDetails]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[FileDetails]] = ..., 
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


    class azure.mgmt.support.models.IsTemporaryTicket(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NO = "No"
        YES = "Yes"


    class azure.mgmt.support.models.MessageProperties(Model):
        body: str
        communication_direction: Union[str, CommunicationDirection]
        content_type: Union[str, TranscriptContentType]
        created_date: datetime
        sender: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                body: Optional[str] = ..., 
                sender: Optional[str] = ..., 
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


    class azure.mgmt.support.models.Operation(Model):
        display: OperationDisplay
        name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                display: Optional[OperationDisplay] = ..., 
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


    class azure.mgmt.support.models.OperationDisplay(Model):
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


    class azure.mgmt.support.models.OperationsListResult(Model):
        value: list[Operation]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[Operation]] = ..., 
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


    class azure.mgmt.support.models.PreferredContactMethod(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EMAIL = "email"
        PHONE = "phone"


    class azure.mgmt.support.models.ProblemClassification(Model):
        display_name: str
        id: str
        name: str
        secondary_consent_enabled: list[SecondaryConsentEnabled]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                display_name: Optional[str] = ..., 
                secondary_consent_enabled: Optional[List[SecondaryConsentEnabled]] = ..., 
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


    class azure.mgmt.support.models.ProblemClassificationsListResult(Model):
        value: list[ProblemClassification]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[ProblemClassification]] = ..., 
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


    class azure.mgmt.support.models.ProxyResource(Resource):
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


    class azure.mgmt.support.models.QuotaChangeRequest(Model):
        payload: str
        region: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                payload: Optional[str] = ..., 
                region: Optional[str] = ..., 
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


    class azure.mgmt.support.models.QuotaTicketDetails(Model):
        quota_change_request_sub_type: str
        quota_change_request_version: str
        quota_change_requests: list[QuotaChangeRequest]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                quota_change_request_sub_type: Optional[str] = ..., 
                quota_change_request_version: Optional[str] = ..., 
                quota_change_requests: Optional[List[QuotaChangeRequest]] = ..., 
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


    class azure.mgmt.support.models.Resource(Model):
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


    class azure.mgmt.support.models.SecondaryConsent(Model):
        type: str
        user_consent: Union[str, UserConsent]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                type: Optional[str] = ..., 
                user_consent: Optional[Union[str, UserConsent]] = ..., 
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


    class azure.mgmt.support.models.SecondaryConsentEnabled(Model):
        description: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                type: Optional[str] = ..., 
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


    class azure.mgmt.support.models.Service(Model):
        display_name: str
        id: str
        name: str
        resource_types: list[str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                display_name: Optional[str] = ..., 
                resource_types: Optional[List[str]] = ..., 
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


    class azure.mgmt.support.models.ServiceLevelAgreement(Model):
        expiration_time: datetime
        sla_minutes: int
        start_time: datetime

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


    class azure.mgmt.support.models.ServicesListResult(Model):
        value: list[Service]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[Service]] = ..., 
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


    class azure.mgmt.support.models.SeverityLevel(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CRITICAL = "critical"
        HIGHESTCRITICALIMPACT = "highestcriticalimpact"
        MINIMAL = "minimal"
        MODERATE = "moderate"


    class azure.mgmt.support.models.Status(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CLOSED = "closed"
        OPEN = "open"


    class azure.mgmt.support.models.SupportEngineer(Model):
        email_address: str

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


    class azure.mgmt.support.models.SupportTicketDetails(Model):
        advanced_diagnostic_consent: Union[str, Consent]
        contact_details: ContactProfile
        created_date: datetime
        description: str
        enrollment_id: str
        file_workspace_name: str
        id: str
        is_temporary_ticket: Union[str, IsTemporaryTicket]
        modified_date: datetime
        name: str
        problem_classification_display_name: str
        problem_classification_id: str
        problem_scoping_questions: str
        problem_start_time: datetime
        quota_ticket_details: QuotaTicketDetails
        require24_x7_response: bool
        secondary_consent: list[SecondaryConsent]
        service_display_name: str
        service_id: str
        service_level_agreement: ServiceLevelAgreement
        severity: Union[str, SeverityLevel]
        status: str
        support_engineer: SupportEngineer
        support_plan_display_name: str
        support_plan_id: str
        support_plan_type: str
        support_ticket_id: str
        technical_ticket_details: TechnicalTicketDetails
        title: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                advanced_diagnostic_consent: Union[str, Consent], 
                contact_details: ContactProfile, 
                description: str, 
                enrollment_id: Optional[str] = ..., 
                file_workspace_name: Optional[str] = ..., 
                problem_classification_id: str, 
                problem_scoping_questions: Optional[str] = ..., 
                problem_start_time: Optional[datetime] = ..., 
                quota_ticket_details: Optional[QuotaTicketDetails] = ..., 
                require24_x7_response: Optional[bool] = ..., 
                secondary_consent: Optional[List[SecondaryConsent]] = ..., 
                service_id: str, 
                service_level_agreement: Optional[ServiceLevelAgreement] = ..., 
                severity: Union[str, SeverityLevel], 
                support_engineer: Optional[SupportEngineer] = ..., 
                support_plan_id: Optional[str] = ..., 
                support_ticket_id: Optional[str] = ..., 
                technical_ticket_details: Optional[TechnicalTicketDetails] = ..., 
                title: str, 
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


    class azure.mgmt.support.models.SupportTicketsListResult(Model):
        next_link: str
        value: list[SupportTicketDetails]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[SupportTicketDetails]] = ..., 
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


    class azure.mgmt.support.models.SystemData(Model):
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


    class azure.mgmt.support.models.TechnicalTicketDetails(Model):
        resource_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                resource_id: Optional[str] = ..., 
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


    class azure.mgmt.support.models.TranscriptContentType(str, Enum, metaclass=CaseInsensitiveEnumMeta):


    class azure.mgmt.support.models.Type(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MICROSOFT_SUPPORT_COMMUNICATIONS = "Microsoft.Support/communications"
        MICROSOFT_SUPPORT_SUPPORT_TICKETS = "Microsoft.Support/supportTickets"


    class azure.mgmt.support.models.UpdateContactProfile(Model):
        additional_email_addresses: list[str]
        country: str
        first_name: str
        last_name: str
        phone_number: str
        preferred_contact_method: Union[str, PreferredContactMethod]
        preferred_support_language: str
        preferred_time_zone: str
        primary_email_address: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                additional_email_addresses: Optional[List[str]] = ..., 
                country: Optional[str] = ..., 
                first_name: Optional[str] = ..., 
                last_name: Optional[str] = ..., 
                phone_number: Optional[str] = ..., 
                preferred_contact_method: Optional[Union[str, PreferredContactMethod]] = ..., 
                preferred_support_language: Optional[str] = ..., 
                preferred_time_zone: Optional[str] = ..., 
                primary_email_address: Optional[str] = ..., 
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


    class azure.mgmt.support.models.UpdateSupportTicket(Model):
        advanced_diagnostic_consent: Union[str, Consent]
        contact_details: UpdateContactProfile
        secondary_consent: list[SecondaryConsent]
        severity: Union[str, SeverityLevel]
        status: Union[str, Status]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                advanced_diagnostic_consent: Optional[Union[str, Consent]] = ..., 
                contact_details: Optional[UpdateContactProfile] = ..., 
                secondary_consent: Optional[List[SecondaryConsent]] = ..., 
                severity: Optional[Union[str, SeverityLevel]] = ..., 
                status: Optional[Union[str, Status]] = ..., 
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


    class azure.mgmt.support.models.UploadFile(Model):
        chunk_index: int
        content: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                chunk_index: Optional[int] = ..., 
                content: Optional[str] = ..., 
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


    class azure.mgmt.support.models.UserConsent(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NO = "No"
        YES = "Yes"


namespace azure.mgmt.support.operations

    class azure.mgmt.support.operations.ChatTranscriptsNoSubscriptionOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get(
                self, 
                support_ticket_name: str, 
                chat_transcript_name: str, 
                **kwargs: Any
            ) -> ChatTranscriptDetails: ...

        @distributed_trace
        def list(
                self, 
                support_ticket_name: str, 
                **kwargs: Any
            ) -> Iterable[ChatTranscriptDetails]: ...


    class azure.mgmt.support.operations.ChatTranscriptsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get(
                self, 
                support_ticket_name: str, 
                chat_transcript_name: str, 
                **kwargs: Any
            ) -> ChatTranscriptDetails: ...

        @distributed_trace
        def list(
                self, 
                support_ticket_name: str, 
                **kwargs: Any
            ) -> Iterable[ChatTranscriptDetails]: ...


    class azure.mgmt.support.operations.CommunicationsNoSubscriptionOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create(
                self, 
                support_ticket_name: str, 
                communication_name: str, 
                create_communication_parameters: CommunicationDetails, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CommunicationDetails]: ...

        @overload
        def begin_create(
                self, 
                support_ticket_name: str, 
                communication_name: str, 
                create_communication_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CommunicationDetails]: ...

        @overload
        def check_name_availability(
                self, 
                support_ticket_name: str, 
                check_name_availability_input: CheckNameAvailabilityInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityOutput: ...

        @overload
        def check_name_availability(
                self, 
                support_ticket_name: str, 
                check_name_availability_input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityOutput: ...

        @distributed_trace
        def get(
                self, 
                support_ticket_name: str, 
                communication_name: str, 
                **kwargs: Any
            ) -> CommunicationDetails: ...

        @distributed_trace
        def list(
                self, 
                support_ticket_name: str, 
                top: Optional[int] = None, 
                filter: Optional[str] = None, 
                **kwargs: Any
            ) -> Iterable[CommunicationDetails]: ...


    class azure.mgmt.support.operations.CommunicationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create(
                self, 
                support_ticket_name: str, 
                communication_name: str, 
                create_communication_parameters: CommunicationDetails, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CommunicationDetails]: ...

        @overload
        def begin_create(
                self, 
                support_ticket_name: str, 
                communication_name: str, 
                create_communication_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CommunicationDetails]: ...

        @overload
        def check_name_availability(
                self, 
                support_ticket_name: str, 
                check_name_availability_input: CheckNameAvailabilityInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityOutput: ...

        @overload
        def check_name_availability(
                self, 
                support_ticket_name: str, 
                check_name_availability_input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityOutput: ...

        @distributed_trace
        def get(
                self, 
                support_ticket_name: str, 
                communication_name: str, 
                **kwargs: Any
            ) -> CommunicationDetails: ...

        @distributed_trace
        def list(
                self, 
                support_ticket_name: str, 
                top: Optional[int] = None, 
                filter: Optional[str] = None, 
                **kwargs: Any
            ) -> Iterable[CommunicationDetails]: ...


    class azure.mgmt.support.operations.FileWorkspacesNoSubscriptionOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def create(
                self, 
                file_workspace_name: str, 
                **kwargs: Any
            ) -> FileWorkspaceDetails: ...

        @distributed_trace
        def get(
                self, 
                file_workspace_name: str, 
                **kwargs: Any
            ) -> FileWorkspaceDetails: ...


    class azure.mgmt.support.operations.FileWorkspacesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def create(
                self, 
                file_workspace_name: str, 
                **kwargs: Any
            ) -> FileWorkspaceDetails: ...

        @distributed_trace
        def get(
                self, 
                file_workspace_name: str, 
                **kwargs: Any
            ) -> FileWorkspaceDetails: ...


    class azure.mgmt.support.operations.FilesNoSubscriptionOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def create(
                self, 
                file_workspace_name: str, 
                file_name: str, 
                create_file_parameters: FileDetails, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FileDetails: ...

        @overload
        def create(
                self, 
                file_workspace_name: str, 
                file_name: str, 
                create_file_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FileDetails: ...

        @distributed_trace
        def get(
                self, 
                file_workspace_name: str, 
                file_name: str, 
                **kwargs: Any
            ) -> FileDetails: ...

        @distributed_trace
        def list(
                self, 
                file_workspace_name: str, 
                **kwargs: Any
            ) -> Iterable[FileDetails]: ...

        @overload
        def upload(
                self, 
                file_workspace_name: str, 
                file_name: str, 
                upload_file: UploadFile, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def upload(
                self, 
                file_workspace_name: str, 
                file_name: str, 
                upload_file: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.support.operations.FilesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def create(
                self, 
                file_workspace_name: str, 
                file_name: str, 
                create_file_parameters: FileDetails, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FileDetails: ...

        @overload
        def create(
                self, 
                file_workspace_name: str, 
                file_name: str, 
                create_file_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FileDetails: ...

        @distributed_trace
        def get(
                self, 
                file_workspace_name: str, 
                file_name: str, 
                **kwargs: Any
            ) -> FileDetails: ...

        @distributed_trace
        def list(
                self, 
                file_workspace_name: str, 
                **kwargs: Any
            ) -> Iterable[FileDetails]: ...

        @overload
        def upload(
                self, 
                file_workspace_name: str, 
                file_name: str, 
                upload_file: UploadFile, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def upload(
                self, 
                file_workspace_name: str, 
                file_name: str, 
                upload_file: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.support.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def list(self, **kwargs: Any) -> Iterable[Operation]: ...


    class azure.mgmt.support.operations.ProblemClassificationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get(
                self, 
                service_name: str, 
                problem_classification_name: str, 
                **kwargs: Any
            ) -> ProblemClassification: ...

        @distributed_trace
        def list(
                self, 
                service_name: str, 
                **kwargs: Any
            ) -> Iterable[ProblemClassification]: ...


    class azure.mgmt.support.operations.ServicesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get(
                self, 
                service_name: str, 
                **kwargs: Any
            ) -> Service: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> Iterable[Service]: ...


    class azure.mgmt.support.operations.SupportTicketsNoSubscriptionOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create(
                self, 
                support_ticket_name: str, 
                create_support_ticket_parameters: SupportTicketDetails, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SupportTicketDetails]: ...

        @overload
        def begin_create(
                self, 
                support_ticket_name: str, 
                create_support_ticket_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SupportTicketDetails]: ...

        @overload
        def check_name_availability(
                self, 
                check_name_availability_input: CheckNameAvailabilityInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityOutput: ...

        @overload
        def check_name_availability(
                self, 
                check_name_availability_input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityOutput: ...

        @distributed_trace
        def get(
                self, 
                support_ticket_name: str, 
                **kwargs: Any
            ) -> SupportTicketDetails: ...

        @distributed_trace
        def list(
                self, 
                top: Optional[int] = None, 
                filter: Optional[str] = None, 
                **kwargs: Any
            ) -> Iterable[SupportTicketDetails]: ...

        @overload
        def update(
                self, 
                support_ticket_name: str, 
                update_support_ticket: UpdateSupportTicket, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SupportTicketDetails: ...

        @overload
        def update(
                self, 
                support_ticket_name: str, 
                update_support_ticket: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SupportTicketDetails: ...


    class azure.mgmt.support.operations.SupportTicketsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create(
                self, 
                support_ticket_name: str, 
                create_support_ticket_parameters: SupportTicketDetails, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SupportTicketDetails]: ...

        @overload
        def begin_create(
                self, 
                support_ticket_name: str, 
                create_support_ticket_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SupportTicketDetails]: ...

        @overload
        def check_name_availability(
                self, 
                check_name_availability_input: CheckNameAvailabilityInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityOutput: ...

        @overload
        def check_name_availability(
                self, 
                check_name_availability_input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityOutput: ...

        @distributed_trace
        def get(
                self, 
                support_ticket_name: str, 
                **kwargs: Any
            ) -> SupportTicketDetails: ...

        @distributed_trace
        def list(
                self, 
                top: Optional[int] = None, 
                filter: Optional[str] = None, 
                **kwargs: Any
            ) -> Iterable[SupportTicketDetails]: ...

        @overload
        def update(
                self, 
                support_ticket_name: str, 
                update_support_ticket: UpdateSupportTicket, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SupportTicketDetails: ...

        @overload
        def update(
                self, 
                support_ticket_name: str, 
                update_support_ticket: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SupportTicketDetails: ...


```