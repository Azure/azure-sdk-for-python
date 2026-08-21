```py
namespace azure.mgmt.support

    class azure.mgmt.support.SupportMgmtClient: implements ContextManager 
        chat_transcripts: ChatTranscriptsOperations
        chat_transcripts_no_subscription: ChatTranscriptsNoSubscriptionOperations
        classify_problems: ClassifyProblemsOperations
        classify_problems_no_subscription: ClassifyProblemsNoSubscriptionOperations
        classify_services: ClassifyServicesOperations
        classify_services_no_subscription: ClassifyServicesNoSubscriptionOperations
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


namespace azure.mgmt.support.aio

    class azure.mgmt.support.aio.SupportMgmtClient: implements AsyncContextManager 
        chat_transcripts: ChatTranscriptsOperations
        chat_transcripts_no_subscription: ChatTranscriptsNoSubscriptionOperations
        classify_problems: ClassifyProblemsOperations
        classify_problems_no_subscription: ClassifyProblemsNoSubscriptionOperations
        classify_services: ClassifyServicesOperations
        classify_services_no_subscription: ClassifyServicesNoSubscriptionOperations
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
            ) -> AsyncItemPaged[ChatTranscriptDetails]: ...


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
            ) -> AsyncItemPaged[ChatTranscriptDetails]: ...


    class azure.mgmt.support.aio.operations.ClassifyProblemsNoSubscriptionOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def classify_problems(
                self, 
                problem_service_name: str, 
                problem_classifications_classification_input: ProblemClassificationsClassificationInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ProblemClassificationsClassificationOutput: ...

        @overload
        async def classify_problems(
                self, 
                problem_service_name: str, 
                problem_classifications_classification_input: ProblemClassificationsClassificationInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ProblemClassificationsClassificationOutput: ...

        @overload
        async def classify_problems(
                self, 
                problem_service_name: str, 
                problem_classifications_classification_input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ProblemClassificationsClassificationOutput: ...


    class azure.mgmt.support.aio.operations.ClassifyProblemsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def classify_problems(
                self, 
                problem_service_name: str, 
                problem_classifications_classification_input: ProblemClassificationsClassificationInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ProblemClassificationsClassificationOutput: ...

        @overload
        async def classify_problems(
                self, 
                problem_service_name: str, 
                problem_classifications_classification_input: ProblemClassificationsClassificationInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ProblemClassificationsClassificationOutput: ...

        @overload
        async def classify_problems(
                self, 
                problem_service_name: str, 
                problem_classifications_classification_input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ProblemClassificationsClassificationOutput: ...


    class azure.mgmt.support.aio.operations.ClassifyServicesNoSubscriptionOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def classify_services(
                self, 
                service_classification_request: ServiceClassificationRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ServiceClassificationOutput: ...

        @overload
        async def classify_services(
                self, 
                service_classification_request: ServiceClassificationRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ServiceClassificationOutput: ...

        @overload
        async def classify_services(
                self, 
                service_classification_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ServiceClassificationOutput: ...


    class azure.mgmt.support.aio.operations.ClassifyServicesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def classify_services(
                self, 
                service_classification_request: ServiceClassificationRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ServiceClassificationOutput: ...

        @overload
        async def classify_services(
                self, 
                service_classification_request: ServiceClassificationRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ServiceClassificationOutput: ...

        @overload
        async def classify_services(
                self, 
                service_classification_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ServiceClassificationOutput: ...


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
                *, 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[CommunicationDetails]: ...


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
                *, 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[CommunicationDetails]: ...


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
            ) -> AsyncItemPaged[FileDetails]: ...

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
            ) -> AsyncItemPaged[FileDetails]: ...

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
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


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
            ) -> AsyncItemPaged[ProblemClassification]: ...


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
        def list(self, **kwargs: Any) -> AsyncItemPaged[Service]: ...


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
                *, 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[SupportTicketDetails]: ...

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
                *, 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[SupportTicketDetails]: ...

        @overload
        async def look_up_resource_id(
                self, 
                look_up_resource_id_request: LookUpResourceIdRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LookUpResourceIdResponse: ...

        @overload
        async def look_up_resource_id(
                self, 
                look_up_resource_id_request: LookUpResourceIdRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LookUpResourceIdResponse: ...

        @overload
        async def look_up_resource_id(
                self, 
                look_up_resource_id_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LookUpResourceIdResponse: ...

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

    class azure.mgmt.support.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.support.models.ChatConversationStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        CLOSED = "Closed"


    class azure.mgmt.support.models.ChatTranscriptDetails(ProxyResource):
        id: str
        name: str
        properties: Optional[ChatTranscriptDetailsProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ChatTranscriptDetailsProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.support.models.ChatTranscriptDetailsProperties(_Model):
        messages: Optional[list[MessageProperties]]
        start_time: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                messages: Optional[list[MessageProperties]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.support.models.CheckNameAvailabilityInput(_Model):
        name: str
        type: Union[str, Type]

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                type: Union[str, Type]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.support.models.CheckNameAvailabilityOutput(_Model):
        message: Optional[str]
        name_available: Optional[bool]
        reason: Optional[str]


    class azure.mgmt.support.models.ClassificationService(_Model):
        display_name: Optional[str]
        resource_types: Optional[list[str]]
        service_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                resource_types: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.support.models.CommunicationDetails(ProxyResource):
        id: str
        name: str
        properties: CommunicationDetailsProperties
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: CommunicationDetailsProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.support.models.CommunicationDetailsProperties(_Model):
        body: str
        communication_direction: Optional[Union[str, CommunicationDirection]]
        communication_type: Optional[Union[str, CommunicationType]]
        created_date: Optional[datetime]
        sender: Optional[str]
        subject: str

        @overload
        def __init__(
                self, 
                *, 
                body: str, 
                sender: Optional[str] = ..., 
                subject: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.support.models.CommunicationDirection(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INBOUND = "inbound"
        OUTBOUND = "outbound"


    class azure.mgmt.support.models.CommunicationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PHONE = "phone"
        WEB = "web"


    class azure.mgmt.support.models.Consent(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NO = "No"
        YES = "Yes"


    class azure.mgmt.support.models.ContactProfile(_Model):
        additional_email_addresses: Optional[list[str]]
        country: str
        first_name: str
        last_name: str
        phone_number: Optional[str]
        preferred_contact_method: Union[str, PreferredContactMethod]
        preferred_support_language: str
        preferred_time_zone: str
        primary_email_address: str

        @overload
        def __init__(
                self, 
                *, 
                additional_email_addresses: Optional[list[str]] = ..., 
                country: str, 
                first_name: str, 
                last_name: str, 
                phone_number: Optional[str] = ..., 
                preferred_contact_method: Union[str, PreferredContactMethod], 
                preferred_support_language: str, 
                preferred_time_zone: str, 
                primary_email_address: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.support.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.support.models.DirectConnectEscalation(_Model):
        allowed_severities: Optional[list[Union[str, SeverityLevel]]]
        azure_ee_status: Optional[Union[str, EscalationStatus]]
        reason_for_escalation: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                allowed_severities: Optional[list[Union[str, SeverityLevel]]] = ..., 
                azure_ee_status: Optional[Union[str, EscalationStatus]] = ..., 
                reason_for_escalation: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.support.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.support.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.support.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.support.models.EscalationStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ESCALATION_AVAILABLE = "EscalationAvailable"
        ESCALATION_INITIATED = "EscalationInitiated"
        ESCALATION_PROCESSED = "EscalationProcessed"
        ESCALATION_UNAVAILABLE = "EscalationUnavailable"
        ESCALATION_UNSUPPORTED = "EscalationUnsupported"


    class azure.mgmt.support.models.FileDetails(ProxyResource):
        id: str
        name: str
        properties: Optional[FileDetailsProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[FileDetailsProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.support.models.FileDetailsProperties(_Model):
        chunk_size: Optional[int]
        created_on: Optional[datetime]
        file_size: Optional[int]
        number_of_chunks: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                chunk_size: Optional[int] = ..., 
                file_size: Optional[int] = ..., 
                number_of_chunks: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.support.models.FileWorkspaceDetails(ProxyResource):
        id: str
        name: str
        properties: Optional[FileWorkspaceDetailsProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[FileWorkspaceDetailsProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.support.models.FileWorkspaceDetailsProperties(_Model):
        created_on: Optional[datetime]
        expiration_time: Optional[datetime]


    class azure.mgmt.support.models.IsTemporaryTicket(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NO = "No"
        YES = "Yes"


    class azure.mgmt.support.models.LookUpResourceIdRequest(_Model):
        identifier: Optional[str]
        type: Optional[Literal["Support/supportTickets"]]

        @overload
        def __init__(
                self, 
                *, 
                identifier: Optional[str] = ..., 
                type: Optional[Literal[Support/supportTickets]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.support.models.LookUpResourceIdResponse(_Model):
        resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.support.models.MessageProperties(_Model):
        body: Optional[str]
        communication_direction: Optional[Union[str, CommunicationDirection]]
        content_type: Optional[str]
        created_date: Optional[datetime]
        sender: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                body: Optional[str] = ..., 
                sender: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.support.models.Operation(_Model):
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


    class azure.mgmt.support.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.support.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.support.models.PreferredContactMethod(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EMAIL = "email"
        PHONE = "phone"


    class azure.mgmt.support.models.ProblemClassification(ProxyResource):
        id: str
        name: str
        properties: Optional[ProblemClassificationProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ProblemClassificationProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.support.models.ProblemClassificationProperties(_Model):
        display_name: Optional[str]
        secondary_consent_enabled: Optional[list[SecondaryConsentEnabled]]

        @overload
        def __init__(
                self, 
                *, 
                display_name: Optional[str] = ..., 
                secondary_consent_enabled: Optional[list[SecondaryConsentEnabled]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.support.models.ProblemClassificationsClassificationInput(_Model):
        issue_summary: str
        resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                issue_summary: str, 
                resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.support.models.ProblemClassificationsClassificationOutput(_Model):
        problem_classification_results: Optional[list[ProblemClassificationsClassificationResult]]

        @overload
        def __init__(
                self, 
                *, 
                problem_classification_results: Optional[list[ProblemClassificationsClassificationResult]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.support.models.ProblemClassificationsClassificationResult(_Model):
        article_id: Optional[str]
        description: Optional[str]
        problem_classification_id: Optional[str]
        problem_id: Optional[str]
        related_service: Optional[ClassificationService]
        service_id: Optional[str]
        title: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                related_service: Optional[ClassificationService] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.support.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.support.models.QuotaChangeRequest(_Model):
        payload: Optional[str]
        region: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                payload: Optional[str] = ..., 
                region: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.support.models.QuotaTicketDetails(_Model):
        quota_change_request_sub_type: Optional[str]
        quota_change_request_version: Optional[str]
        quota_change_requests: Optional[list[QuotaChangeRequest]]

        @overload
        def __init__(
                self, 
                *, 
                quota_change_request_sub_type: Optional[str] = ..., 
                quota_change_request_version: Optional[str] = ..., 
                quota_change_requests: Optional[list[QuotaChangeRequest]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.support.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.support.models.SecondaryConsent(_Model):
        type: Optional[str]
        user_consent: Optional[Union[str, UserConsent]]

        @overload
        def __init__(
                self, 
                *, 
                type: Optional[str] = ..., 
                user_consent: Optional[Union[str, UserConsent]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.support.models.SecondaryConsentEnabled(_Model):
        description: Optional[str]
        type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.support.models.Service(ProxyResource):
        id: str
        name: str
        properties: Optional[ServiceProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ServiceProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.support.models.ServiceClassificationAnswer(ClassificationService):
        child_service: Optional[ClassificationService]
        display_name: str
        resource_types: list[str]
        service_id: str

        @overload
        def __init__(
                self, 
                *, 
                child_service: Optional[ClassificationService] = ..., 
                resource_types: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.support.models.ServiceClassificationOutput(_Model):
        service_classification_results: Optional[list[ServiceClassificationAnswer]]

        @overload
        def __init__(
                self, 
                *, 
                service_classification_results: Optional[list[ServiceClassificationAnswer]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.support.models.ServiceClassificationRequest(_Model):
        additional_context: Optional[str]
        issue_summary: Optional[str]
        resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                additional_context: Optional[str] = ..., 
                issue_summary: Optional[str] = ..., 
                resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.support.models.ServiceLevelAgreement(_Model):
        expiration_time: Optional[datetime]
        sla_minutes: Optional[int]
        start_time: Optional[datetime]


    class azure.mgmt.support.models.ServiceProperties(_Model):
        display_name: Optional[str]
        resource_types: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                display_name: Optional[str] = ..., 
                resource_types: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.support.models.SeverityLevel(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CRITICAL = "critical"
        HIGHESTCRITICALIMPACT = "highestcriticalimpact"
        MINIMAL = "minimal"
        MODERATE = "moderate"


    class azure.mgmt.support.models.Status(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CLOSED = "closed"
        OPEN = "open"


    class azure.mgmt.support.models.SupportChannel(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CHAT = "Chat"
        WEB = "Web"


    class azure.mgmt.support.models.SupportEngineer(_Model):
        email_address: Optional[str]


    class azure.mgmt.support.models.SupportTicketDetails(ProxyResource):
        id: str
        name: str
        properties: SupportTicketDetailsProperties
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: SupportTicketDetailsProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.support.models.SupportTicketDetailsProperties(_Model):
        advanced_diagnostic_consent: Union[str, Consent]
        chat_conversation_status: Optional[Union[str, ChatConversationStatus]]
        community_forum_post: Optional[str]
        contact_details: ContactProfile
        created_date: Optional[datetime]
        description: str
        direct_connect_escalation: Optional[DirectConnectEscalation]
        enrollment_id: Optional[str]
        file_workspace_name: Optional[str]
        is_temporary_ticket: Optional[Union[str, IsTemporaryTicket]]
        modified_date: Optional[datetime]
        problem_classification_display_name: Optional[str]
        problem_classification_id: str
        problem_scoping_questions: Optional[str]
        problem_start_time: Optional[datetime]
        quota_ticket_details: Optional[QuotaTicketDetails]
        require24_x7_response: Optional[bool]
        secondary_consent: Optional[list[SecondaryConsent]]
        service_display_name: Optional[str]
        service_id: str
        service_level_agreement: Optional[ServiceLevelAgreement]
        severity: Union[str, SeverityLevel]
        status: Optional[str]
        support_channel: Optional[Union[str, SupportChannel]]
        support_engineer: Optional[SupportEngineer]
        support_plan_display_name: Optional[str]
        support_plan_id: Optional[str]
        support_plan_type: Optional[str]
        support_ticket_id: Optional[str]
        technical_ticket_details: Optional[TechnicalTicketDetails]
        title: str

        @overload
        def __init__(
                self, 
                *, 
                advanced_diagnostic_consent: Union[str, Consent], 
                community_forum_post: Optional[str] = ..., 
                contact_details: ContactProfile, 
                description: str, 
                direct_connect_escalation: Optional[DirectConnectEscalation] = ..., 
                enrollment_id: Optional[str] = ..., 
                file_workspace_name: Optional[str] = ..., 
                problem_classification_id: str, 
                problem_scoping_questions: Optional[str] = ..., 
                problem_start_time: Optional[datetime] = ..., 
                quota_ticket_details: Optional[QuotaTicketDetails] = ..., 
                require24_x7_response: Optional[bool] = ..., 
                secondary_consent: Optional[list[SecondaryConsent]] = ..., 
                service_id: str, 
                service_level_agreement: Optional[ServiceLevelAgreement] = ..., 
                severity: Union[str, SeverityLevel], 
                support_engineer: Optional[SupportEngineer] = ..., 
                support_plan_id: Optional[str] = ..., 
                support_ticket_id: Optional[str] = ..., 
                technical_ticket_details: Optional[TechnicalTicketDetails] = ..., 
                title: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.support.models.SystemData(_Model):
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


    class azure.mgmt.support.models.TechnicalTicketDetails(_Model):
        resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.support.models.Type(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MICROSOFT_SUPPORT_COMMUNICATIONS = "Microsoft.Support/communications"
        MICROSOFT_SUPPORT_SUPPORT_TICKETS = "Microsoft.Support/supportTickets"


    class azure.mgmt.support.models.UpdateContactProfile(_Model):
        additional_email_addresses: Optional[list[str]]
        country: Optional[str]
        first_name: Optional[str]
        last_name: Optional[str]
        phone_number: Optional[str]
        preferred_contact_method: Optional[Union[str, PreferredContactMethod]]
        preferred_support_language: Optional[str]
        preferred_time_zone: Optional[str]
        primary_email_address: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                additional_email_addresses: Optional[list[str]] = ..., 
                country: Optional[str] = ..., 
                first_name: Optional[str] = ..., 
                last_name: Optional[str] = ..., 
                phone_number: Optional[str] = ..., 
                preferred_contact_method: Optional[Union[str, PreferredContactMethod]] = ..., 
                preferred_support_language: Optional[str] = ..., 
                preferred_time_zone: Optional[str] = ..., 
                primary_email_address: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.support.models.UpdateSupportTicket(_Model):
        advanced_diagnostic_consent: Optional[Union[str, Consent]]
        contact_details: Optional[UpdateContactProfile]
        direct_connect_escalation: Optional[DirectConnectEscalation]
        secondary_consent: Optional[list[SecondaryConsent]]
        severity: Optional[Union[str, SeverityLevel]]
        status: Optional[Union[str, Status]]

        @overload
        def __init__(
                self, 
                *, 
                advanced_diagnostic_consent: Optional[Union[str, Consent]] = ..., 
                contact_details: Optional[UpdateContactProfile] = ..., 
                direct_connect_escalation: Optional[DirectConnectEscalation] = ..., 
                secondary_consent: Optional[list[SecondaryConsent]] = ..., 
                severity: Optional[Union[str, SeverityLevel]] = ..., 
                status: Optional[Union[str, Status]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.support.models.UploadFile(_Model):
        chunk_index: Optional[int]
        content: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                chunk_index: Optional[int] = ..., 
                content: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.support.models.UserConsent(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NO = "No"
        YES = "Yes"


namespace azure.mgmt.support.operations

    class azure.mgmt.support.operations.ChatTranscriptsNoSubscriptionOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
            ) -> ItemPaged[ChatTranscriptDetails]: ...


    class azure.mgmt.support.operations.ChatTranscriptsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
            ) -> ItemPaged[ChatTranscriptDetails]: ...


    class azure.mgmt.support.operations.ClassifyProblemsNoSubscriptionOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def classify_problems(
                self, 
                problem_service_name: str, 
                problem_classifications_classification_input: ProblemClassificationsClassificationInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ProblemClassificationsClassificationOutput: ...

        @overload
        def classify_problems(
                self, 
                problem_service_name: str, 
                problem_classifications_classification_input: ProblemClassificationsClassificationInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ProblemClassificationsClassificationOutput: ...

        @overload
        def classify_problems(
                self, 
                problem_service_name: str, 
                problem_classifications_classification_input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ProblemClassificationsClassificationOutput: ...


    class azure.mgmt.support.operations.ClassifyProblemsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def classify_problems(
                self, 
                problem_service_name: str, 
                problem_classifications_classification_input: ProblemClassificationsClassificationInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ProblemClassificationsClassificationOutput: ...

        @overload
        def classify_problems(
                self, 
                problem_service_name: str, 
                problem_classifications_classification_input: ProblemClassificationsClassificationInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ProblemClassificationsClassificationOutput: ...

        @overload
        def classify_problems(
                self, 
                problem_service_name: str, 
                problem_classifications_classification_input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ProblemClassificationsClassificationOutput: ...


    class azure.mgmt.support.operations.ClassifyServicesNoSubscriptionOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def classify_services(
                self, 
                service_classification_request: ServiceClassificationRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ServiceClassificationOutput: ...

        @overload
        def classify_services(
                self, 
                service_classification_request: ServiceClassificationRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ServiceClassificationOutput: ...

        @overload
        def classify_services(
                self, 
                service_classification_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ServiceClassificationOutput: ...


    class azure.mgmt.support.operations.ClassifyServicesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def classify_services(
                self, 
                service_classification_request: ServiceClassificationRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ServiceClassificationOutput: ...

        @overload
        def classify_services(
                self, 
                service_classification_request: ServiceClassificationRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ServiceClassificationOutput: ...

        @overload
        def classify_services(
                self, 
                service_classification_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ServiceClassificationOutput: ...


    class azure.mgmt.support.operations.CommunicationsNoSubscriptionOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
                *, 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[CommunicationDetails]: ...


    class azure.mgmt.support.operations.CommunicationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
                *, 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[CommunicationDetails]: ...


    class azure.mgmt.support.operations.FileWorkspacesNoSubscriptionOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
            ) -> None: ...

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
            ) -> None: ...

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
            ) -> ItemPaged[FileDetails]: ...

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
            ) -> None: ...

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
            ) -> ItemPaged[FileDetails]: ...

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
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


    class azure.mgmt.support.operations.ProblemClassificationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
            ) -> ItemPaged[ProblemClassification]: ...


    class azure.mgmt.support.operations.ServicesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                service_name: str, 
                **kwargs: Any
            ) -> Service: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Service]: ...


    class azure.mgmt.support.operations.SupportTicketsNoSubscriptionOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
                *, 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[SupportTicketDetails]: ...

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
            ) -> None: ...

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
                *, 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[SupportTicketDetails]: ...

        @overload
        def look_up_resource_id(
                self, 
                look_up_resource_id_request: LookUpResourceIdRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LookUpResourceIdResponse: ...

        @overload
        def look_up_resource_id(
                self, 
                look_up_resource_id_request: LookUpResourceIdRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LookUpResourceIdResponse: ...

        @overload
        def look_up_resource_id(
                self, 
                look_up_resource_id_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LookUpResourceIdResponse: ...

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


namespace azure.mgmt.support.types

    class azure.mgmt.support.types.ChatTranscriptDetails(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('ChatTranscriptDetailsProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: ChatTranscriptDetailsProperties
        system_data: SystemData
        type: str


    class azure.mgmt.support.types.ChatTranscriptDetailsProperties(TypedDict, total=False):
        key "startTime": str
        messages: list[MessageProperties]
        start_time: str


    class azure.mgmt.support.types.CheckNameAvailabilityInput(TypedDict, total=False):
        key "name": Required[str]
        key "type": Required[Union[str, Type]]
        name: str
        type: Union[str, Type]


    class azure.mgmt.support.types.CheckNameAvailabilityOutput(TypedDict, total=False):
        key "message": str
        key "nameAvailable": bool
        key "reason": str
        message: str
        name_available: bool
        reason: str


    class azure.mgmt.support.types.ClassificationService(TypedDict, total=False):
        key "displayName": str
        key "serviceId": str
        display_name: str
        resourceTypes: list[str]
        resource_types: list[str]
        service_id: str


    class azure.mgmt.support.types.CommunicationDetails(ProxyResource):
        key "id": str
        key "name": str
        key "properties": Required[CommunicationDetailsProperties]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: CommunicationDetailsProperties
        system_data: SystemData
        type: str


    class azure.mgmt.support.types.CommunicationDetailsProperties(TypedDict, total=False):
        key "body": Required[str]
        key "communicationDirection": Union[str, CommunicationDirection]
        key "communicationType": Union[str, CommunicationType]
        key "createdDate": str
        key "sender": str
        key "subject": Required[str]
        body: str
        communication_direction: Union[str, CommunicationDirection]
        communication_type: Union[str, CommunicationType]
        created_date: str
        sender: str
        subject: str


    class azure.mgmt.support.types.ContactProfile(TypedDict, total=False):
        key "country": Required[str]
        key "firstName": Required[str]
        key "lastName": Required[str]
        key "phoneNumber": str
        key "preferredContactMethod": Required[Union[str, PreferredContactMethod]]
        key "preferredSupportLanguage": Required[str]
        key "preferredTimeZone": Required[str]
        key "primaryEmailAddress": Required[str]
        additionalEmailAddresses: list[str]
        additional_email_addresses: list[str]
        country: str
        first_name: str
        last_name: str
        phone_number: str
        preferred_contact_method: Union[str, PreferredContactMethod]
        preferred_support_language: str
        preferred_time_zone: str
        primary_email_address: str


    class azure.mgmt.support.types.DirectConnectEscalation(TypedDict, total=False):
        key "azureEEStatus": Union[str, EscalationStatus]
        key "reasonForEscalation": str
        allowedSeverities: list[Union[str, SeverityLevel]]
        allowed_severities: list[Union[str, SeverityLevel]]
        azure_ee_status: Union[str, EscalationStatus]
        reason_for_escalation: str


    class azure.mgmt.support.types.ErrorAdditionalInfo(TypedDict, total=False):
        key "info": Any
        key "type": str
        info: Any
        type: str


    class azure.mgmt.support.types.ErrorDetail(TypedDict, total=False):
        key "code": str
        key "message": str
        key "target": str
        additionalInfo: list[ErrorAdditionalInfo]
        additional_info: list[ErrorAdditionalInfo]
        code: str
        details: list[ErrorDetail]
        message: str
        target: str


    class azure.mgmt.support.types.ErrorResponse(TypedDict, total=False):
        key "error": ForwardRef('ErrorDetail', module='types')
        error: ErrorDetail


    class azure.mgmt.support.types.FileDetails(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('FileDetailsProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: FileDetailsProperties
        system_data: SystemData
        type: str


    class azure.mgmt.support.types.FileDetailsProperties(TypedDict, total=False):
        key "chunkSize": int
        key "createdOn": str
        key "fileSize": int
        key "numberOfChunks": int
        chunk_size: int
        created_on: str
        file_size: int
        number_of_chunks: int


    class azure.mgmt.support.types.FileWorkspaceDetails(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('FileWorkspaceDetailsProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: FileWorkspaceDetailsProperties
        system_data: SystemData
        type: str


    class azure.mgmt.support.types.FileWorkspaceDetailsProperties(TypedDict, total=False):
        key "createdOn": str
        key "expirationTime": str
        created_on: str
        expiration_time: str


    class azure.mgmt.support.types.LookUpResourceIdRequest(TypedDict, total=False):
        key "identifier": str
        key "type": Literal["Support/supportTickets"]
        identifier: str
        type: Literal[Support/supportTickets]


    class azure.mgmt.support.types.LookUpResourceIdResponse(TypedDict, total=False):
        key "resourceId": str
        resource_id: str


    class azure.mgmt.support.types.MessageProperties(TypedDict, total=False):
        key "body": str
        key "communicationDirection": Union[str, CommunicationDirection]
        key "contentType": str
        key "createdDate": str
        key "sender": str
        body: str
        communication_direction: Union[str, CommunicationDirection]
        content_type: str
        created_date: str
        sender: str


    class azure.mgmt.support.types.Operation(TypedDict, total=False):
        key "actionType": Union[str, ActionType]
        key "display": ForwardRef('OperationDisplay', module='types')
        key "isDataAction": bool
        key "name": str
        key "origin": Union[str, Origin]
        action_type: Union[str, ActionType]
        display: OperationDisplay
        is_data_action: bool
        name: str
        origin: Union[str, Origin]


    class azure.mgmt.support.types.OperationDisplay(TypedDict, total=False):
        key "description": str
        key "operation": str
        key "provider": str
        key "resource": str
        description: str
        operation: str
        provider: str
        resource: str


    class azure.mgmt.support.types.ProblemClassification(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('ProblemClassificationProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: ProblemClassificationProperties
        system_data: SystemData
        type: str


    class azure.mgmt.support.types.ProblemClassificationProperties(TypedDict, total=False):
        key "displayName": str
        display_name: str
        secondaryConsentEnabled: list[SecondaryConsentEnabled]
        secondary_consent_enabled: list[SecondaryConsentEnabled]


    class azure.mgmt.support.types.ProblemClassificationsClassificationInput(TypedDict, total=False):
        key "issueSummary": Required[str]
        key "resourceId": str
        issue_summary: str
        resource_id: str


    class azure.mgmt.support.types.ProblemClassificationsClassificationOutput(TypedDict, total=False):
        problemClassificationResults: list[ProblemClassificationsClassificationResult]
        problem_classification_results: list[ProblemClassificationsClassificationResult]


    class azure.mgmt.support.types.ProblemClassificationsClassificationResult(TypedDict, total=False):
        key "articleId": str
        key "description": str
        key "problemClassificationId": str
        key "problemId": str
        key "relatedService": ForwardRef('ClassificationService', module='types')
        key "serviceId": str
        key "title": str
        article_id: str
        description: str
        problem_classification_id: str
        problem_id: str
        related_service: ClassificationService
        service_id: str
        title: str


    class azure.mgmt.support.types.ProxyResource(Resource):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.support.types.QuotaChangeRequest(TypedDict, total=False):
        key "payload": str
        key "region": str
        payload: str
        region: str


    class azure.mgmt.support.types.QuotaTicketDetails(TypedDict, total=False):
        key "quotaChangeRequestSubType": str
        key "quotaChangeRequestVersion": str
        quotaChangeRequests: list[QuotaChangeRequest]
        quota_change_request_sub_type: str
        quota_change_request_version: str
        quota_change_requests: list[QuotaChangeRequest]


    class azure.mgmt.support.types.Resource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.support.types.SecondaryConsent(TypedDict, total=False):
        key "type": str
        key "userConsent": Union[str, UserConsent]
        type: str
        user_consent: Union[str, UserConsent]


    class azure.mgmt.support.types.SecondaryConsentEnabled(TypedDict, total=False):
        key "description": str
        key "type": str
        description: str
        type: str


    class azure.mgmt.support.types.Service(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('ServiceProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: ServiceProperties
        system_data: SystemData
        type: str


    class azure.mgmt.support.types.ServiceClassificationAnswer(ClassificationService):
        key "childService": ForwardRef('ClassificationService', module='types')
        key "displayName": str
        key "serviceId": str
        child_service: ClassificationService
        display_name: str
        resourceTypes: list[str]
        resource_types: list[str]
        service_id: str


    class azure.mgmt.support.types.ServiceClassificationOutput(TypedDict, total=False):
        serviceClassificationResults: list[ServiceClassificationAnswer]
        service_classification_results: list[ServiceClassificationAnswer]


    class azure.mgmt.support.types.ServiceClassificationRequest(TypedDict, total=False):
        key "additionalContext": str
        key "issueSummary": str
        key "resourceId": str
        additional_context: str
        issue_summary: str
        resource_id: str


    class azure.mgmt.support.types.ServiceLevelAgreement(TypedDict, total=False):
        key "expirationTime": str
        key "slaMinutes": int
        key "startTime": str
        expiration_time: str
        sla_minutes: int
        start_time: str


    class azure.mgmt.support.types.ServiceProperties(TypedDict, total=False):
        key "displayName": str
        display_name: str
        resourceTypes: list[str]
        resource_types: list[str]


    class azure.mgmt.support.types.SupportEngineer(TypedDict, total=False):
        key "emailAddress": str
        email_address: str


    class azure.mgmt.support.types.SupportTicketDetails(ProxyResource):
        key "id": str
        key "name": str
        key "properties": Required[SupportTicketDetailsProperties]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: SupportTicketDetailsProperties
        system_data: SystemData
        type: str


    class azure.mgmt.support.types.SupportTicketDetailsProperties(TypedDict, total=False):
        key "advancedDiagnosticConsent": Required[Union[str, Consent]]
        key "chatConversationStatus": Union[str, ChatConversationStatus]
        key "communityForumPost": str
        key "contactDetails": Required[ContactProfile]
        key "createdDate": str
        key "description": Required[str]
        key "directConnectEscalation": ForwardRef('DirectConnectEscalation', module='types')
        key "enrollmentId": str
        key "fileWorkspaceName": str
        key "isTemporaryTicket": Union[str, IsTemporaryTicket]
        key "modifiedDate": str
        key "problemClassificationDisplayName": str
        key "problemClassificationId": Required[str]
        key "problemScopingQuestions": str
        key "problemStartTime": str
        key "quotaTicketDetails": ForwardRef('QuotaTicketDetails', module='types')
        key "require24X7Response": bool
        key "serviceDisplayName": str
        key "serviceId": Required[str]
        key "serviceLevelAgreement": ForwardRef('ServiceLevelAgreement', module='types')
        key "severity": Required[Union[str, SeverityLevel]]
        key "status": str
        key "supportChannel": Union[str, SupportChannel]
        key "supportEngineer": ForwardRef('SupportEngineer', module='types')
        key "supportPlanDisplayName": str
        key "supportPlanId": str
        key "supportPlanType": str
        key "supportTicketId": str
        key "technicalTicketDetails": ForwardRef('TechnicalTicketDetails', module='types')
        key "title": Required[str]
        advanced_diagnostic_consent: Union[str, Consent]
        chat_conversation_status: Union[str, ChatConversationStatus]
        community_forum_post: str
        contact_details: ContactProfile
        created_date: str
        description: str
        direct_connect_escalation: DirectConnectEscalation
        enrollment_id: str
        file_workspace_name: str
        is_temporary_ticket: Union[str, IsTemporaryTicket]
        modified_date: str
        problem_classification_display_name: str
        problem_classification_id: str
        problem_scoping_questions: str
        problem_start_time: str
        quota_ticket_details: QuotaTicketDetails
        require24_x7_response: bool
        secondaryConsent: list[SecondaryConsent]
        secondary_consent: list[SecondaryConsent]
        service_display_name: str
        service_id: str
        service_level_agreement: ServiceLevelAgreement
        severity: Union[str, SeverityLevel]
        status: str
        support_channel: Union[str, SupportChannel]
        support_engineer: SupportEngineer
        support_plan_display_name: str
        support_plan_id: str
        support_plan_type: str
        support_ticket_id: str
        technical_ticket_details: TechnicalTicketDetails
        title: str


    class azure.mgmt.support.types.SystemData(TypedDict, total=False):
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


    class azure.mgmt.support.types.TechnicalTicketDetails(TypedDict, total=False):
        key "resourceId": str
        resource_id: str


    class azure.mgmt.support.types.UpdateContactProfile(TypedDict, total=False):
        key "country": str
        key "firstName": str
        key "lastName": str
        key "phoneNumber": str
        key "preferredContactMethod": Union[str, PreferredContactMethod]
        key "preferredSupportLanguage": str
        key "preferredTimeZone": str
        key "primaryEmailAddress": str
        additionalEmailAddresses: list[str]
        additional_email_addresses: list[str]
        country: str
        first_name: str
        last_name: str
        phone_number: str
        preferred_contact_method: Union[str, PreferredContactMethod]
        preferred_support_language: str
        preferred_time_zone: str
        primary_email_address: str


    class azure.mgmt.support.types.UpdateSupportTicket(TypedDict, total=False):
        key "advancedDiagnosticConsent": Union[str, Consent]
        key "contactDetails": ForwardRef('UpdateContactProfile', module='types')
        key "directConnectEscalation": ForwardRef('DirectConnectEscalation', module='types')
        key "severity": Union[str, SeverityLevel]
        key "status": Union[str, Status]
        advanced_diagnostic_consent: Union[str, Consent]
        contact_details: UpdateContactProfile
        direct_connect_escalation: DirectConnectEscalation
        secondaryConsent: list[SecondaryConsent]
        secondary_consent: list[SecondaryConsent]
        severity: Union[str, SeverityLevel]
        status: Union[str, Status]


    class azure.mgmt.support.types.UploadFile(TypedDict, total=False):
        key "chunkIndex": int
        key "content": str
        chunk_index: int
        content: str


```