```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.education

    class azure.mgmt.education.EducationManagementClient(EducationManagementClientOperationsMixin): implements ContextManager 
        grants: GrantsOperations
        join_requests: JoinRequestsOperations
        labs: LabsOperations
        operations: Operations
        student_labs: StudentLabsOperations
        students: StudentsOperations

        def __init__(
                self, 
                credential: TokenCredential, 
                base_url: str = "https://management.azure.com", 
                *, 
                api_version: str = ..., 
                **kwargs: Any
            ) -> None: ...

        def close(self) -> None: ...

        @overload
        def redeem_invitation_code(
                self, 
                parameters: RedeemRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def redeem_invitation_code(
                self, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...


namespace azure.mgmt.education.aio

    class azure.mgmt.education.aio.EducationManagementClient(EducationManagementClientOperationsMixin): implements AsyncContextManager 
        grants: GrantsOperations
        join_requests: JoinRequestsOperations
        labs: LabsOperations
        operations: Operations
        student_labs: StudentLabsOperations
        students: StudentsOperations

        def __init__(
                self, 
                credential: AsyncTokenCredential, 
                base_url: str = "https://management.azure.com", 
                *, 
                api_version: str = ..., 
                **kwargs: Any
            ) -> None: ...

        async def close(self) -> None: ...

        @overload
        async def redeem_invitation_code(
                self, 
                parameters: RedeemRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def redeem_invitation_code(
                self, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...


namespace azure.mgmt.education.aio.operations

    class azure.mgmt.education.aio.operations.EducationManagementClientOperationsMixin(EducationManagementClientMixinABC):

        @overload
        async def redeem_invitation_code(
                self, 
                parameters: RedeemRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def redeem_invitation_code(
                self, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.education.aio.operations.GrantsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                include_allocated_budget: Optional[bool] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> GrantDetails: ...

        @distributed_trace
        def list(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                include_allocated_budget: Optional[bool] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[GrantDetails]: ...

        @distributed_trace
        def list_all(
                self, 
                include_allocated_budget: Optional[bool] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[GrantDetails]: ...


    class azure.mgmt.education.aio.operations.JoinRequestsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def approve(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                invoice_section_name: str, 
                join_request_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def deny(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                invoice_section_name: str, 
                join_request_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                invoice_section_name: str, 
                join_request_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> JoinRequestDetails: ...

        @distributed_trace
        def list(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                invoice_section_name: str, 
                include_denied: Optional[bool] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[JoinRequestDetails]: ...


    class azure.mgmt.education.aio.operations.LabsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                invoice_section_name: str, 
                parameters: LabDetails, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LabDetails: ...

        @overload
        async def create_or_update(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                invoice_section_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LabDetails: ...

        @distributed_trace_async
        async def delete(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                invoice_section_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def generate_invite_code(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                invoice_section_name: str, 
                parameters: InviteCodeGenerateRequest, 
                only_update_student_count_parameter: Optional[bool] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LabDetails: ...

        @overload
        async def generate_invite_code(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                invoice_section_name: str, 
                parameters: IO, 
                only_update_student_count_parameter: Optional[bool] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LabDetails: ...

        @distributed_trace_async
        async def get(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                invoice_section_name: str, 
                include_budget: Optional[bool] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> LabDetails: ...

        @distributed_trace
        def list(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                invoice_section_name: str, 
                include_budget: Optional[bool] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[LabDetails]: ...

        @distributed_trace
        def list_all(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                include_budget: Optional[bool] = None, 
                include_deleted: Optional[bool] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[LabDetails]: ...


    class azure.mgmt.education.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def list(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> OperationListResult: ...


    class azure.mgmt.education.aio.operations.StudentLabsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                student_lab_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> StudentLabDetails: ...

        @distributed_trace
        def list_all(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[StudentLabDetails]: ...


    class azure.mgmt.education.aio.operations.StudentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                invoice_section_name: str, 
                student_alias: str, 
                parameters: StudentDetails, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StudentDetails: ...

        @overload
        async def create_or_update(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                invoice_section_name: str, 
                student_alias: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StudentDetails: ...

        @distributed_trace_async
        async def delete(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                invoice_section_name: str, 
                student_alias: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                invoice_section_name: str, 
                student_alias: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> StudentDetails: ...

        @distributed_trace
        def list(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                invoice_section_name: str, 
                include_deleted: Optional[bool] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[StudentDetails]: ...


namespace azure.mgmt.education.models

    class azure.mgmt.education.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.education.models.Amount(Model):
        currency: str
        value: float

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                currency: Optional[str] = ..., 
                value: Optional[float] = ..., 
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


    class azure.mgmt.education.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.education.models.ErrorResponse(Model):
        code: str
        message: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                message: Optional[str] = ..., 
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


    class azure.mgmt.education.models.ErrorResponseBody(Model):
        error: ErrorResponse

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                error: Optional[ErrorResponse] = ..., 
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


    class azure.mgmt.education.models.GrantDetails(Resource):
        allocated_budget: Amount
        effective_date: datetime
        expiration_date: datetime
        id: str
        name: str
        offer_cap: Amount
        offer_type: Union[str, GrantType]
        status: Union[str, GrantStatus]
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


    class azure.mgmt.education.models.GrantListResponse(Model):
        next_link: str
        value: list[GrantDetails]

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


    class azure.mgmt.education.models.GrantStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        INACTIVE = "Inactive"


    class azure.mgmt.education.models.GrantType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACADEMIC = "Academic"
        STUDENT = "Student"


    class azure.mgmt.education.models.InviteCodeGenerateRequest(Model):
        max_student_count: float

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                max_student_count: Optional[float] = ..., 
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


    class azure.mgmt.education.models.JoinRequestDetails(Resource):
        email: str
        first_name: str
        id: str
        last_name: str
        name: str
        status: Union[str, JoinRequestStatus]
        system_data: SystemData
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                email: Optional[str] = ..., 
                first_name: Optional[str] = ..., 
                last_name: Optional[str] = ..., 
                status: Optional[Union[str, JoinRequestStatus]] = ..., 
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


    class azure.mgmt.education.models.JoinRequestList(Model):
        next_link: str
        value: list[JoinRequestDetails]

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


    class azure.mgmt.education.models.JoinRequestStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DENIED = "Denied"
        PENDING = "Pending"


    class azure.mgmt.education.models.LabDetails(Resource):
        budget_per_student: Amount
        currency_properties_total_allocated_budget_currency: str
        currency_properties_total_budget_currency: str
        description: str
        display_name: str
        effective_date: datetime
        expiration_date: datetime
        id: str
        invitation_code: str
        max_student_count: float
        name: str
        status: Union[str, LabStatus]
        system_data: SystemData
        type: str
        value_properties_total_allocated_budget_value: float
        value_properties_total_budget_value: float

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                budget_per_student: Optional[Amount] = ..., 
                currency_properties_total_allocated_budget_currency: Optional[str] = ..., 
                currency_properties_total_budget_currency: Optional[str] = ..., 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                expiration_date: Optional[datetime] = ..., 
                value_properties_total_allocated_budget_value: Optional[float] = ..., 
                value_properties_total_budget_value: Optional[float] = ..., 
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


    class azure.mgmt.education.models.LabListResult(Model):
        next_link: str
        value: list[LabDetails]

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


    class azure.mgmt.education.models.LabStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        DELETED = "Deleted"
        PENDING = "Pending"


    class azure.mgmt.education.models.Operation(Model):
        action_type: Union[str, ActionType]
        display: OperationDisplay
        is_data_action: bool
        name: str
        origin: Union[str, Origin]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                display: Optional[OperationDisplay] = ..., 
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


    class azure.mgmt.education.models.OperationDisplay(Model):
        description: str
        operation: str
        provider: str
        resource: str

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


    class azure.mgmt.education.models.OperationListResult(Model):
        next_link: str
        value: list[Operation]

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


    class azure.mgmt.education.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.education.models.RedeemRequest(Model):
        first_name: str
        last_name: str
        redeem_code: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                first_name: str, 
                last_name: str, 
                redeem_code: str, 
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


    class azure.mgmt.education.models.Resource(Model):
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


    class azure.mgmt.education.models.StudentDetails(Resource):
        budget: Amount
        effective_date: datetime
        email: str
        expiration_date: datetime
        first_name: str
        id: str
        last_name: str
        name: str
        role: Union[str, StudentRole]
        status: Union[str, StudentLabStatus]
        subscription_alias: str
        subscription_id: str
        subscription_invite_last_sent_date: datetime
        system_data: SystemData
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                budget: Optional[Amount] = ..., 
                email: Optional[str] = ..., 
                expiration_date: Optional[datetime] = ..., 
                first_name: Optional[str] = ..., 
                last_name: Optional[str] = ..., 
                role: Optional[Union[str, StudentRole]] = ..., 
                subscription_alias: Optional[str] = ..., 
                subscription_invite_last_sent_date: Optional[datetime] = ..., 
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


    class azure.mgmt.education.models.StudentLabDetails(Resource):
        budget: Amount
        description: str
        display_name: str
        effective_date: datetime
        expiration_date: datetime
        id: str
        lab_scope: str
        name: str
        role: Union[str, StudentRole]
        status: Union[str, StudentLabStatus]
        subscription_id: str
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


    class azure.mgmt.education.models.StudentLabListResult(Model):
        next_link: str
        value: list[StudentLabDetails]

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


    class azure.mgmt.education.models.StudentLabStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        DELETED = "Deleted"
        DISABLED = "Disabled"
        EXPIRED = "Expired"
        PENDING = "Pending"


    class azure.mgmt.education.models.StudentListResult(Model):
        next_link: str
        value: list[StudentDetails]

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


    class azure.mgmt.education.models.StudentRole(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ADMIN = "Admin"
        STUDENT = "Student"


    class azure.mgmt.education.models.SystemData(Model):
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


namespace azure.mgmt.education.operations

    class azure.mgmt.education.operations.EducationManagementClientOperationsMixin(EducationManagementClientMixinABC):

        @overload
        def redeem_invitation_code(
                self, 
                parameters: RedeemRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def redeem_invitation_code(
                self, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.education.operations.GrantsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                include_allocated_budget: Optional[bool] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> GrantDetails: ...

        @distributed_trace
        def list(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                include_allocated_budget: Optional[bool] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[GrantDetails]: ...

        @distributed_trace
        def list_all(
                self, 
                include_allocated_budget: Optional[bool] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[GrantDetails]: ...


    class azure.mgmt.education.operations.JoinRequestsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def approve(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                invoice_section_name: str, 
                join_request_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def deny(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                invoice_section_name: str, 
                join_request_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                invoice_section_name: str, 
                join_request_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> JoinRequestDetails: ...

        @distributed_trace
        def list(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                invoice_section_name: str, 
                include_denied: Optional[bool] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[JoinRequestDetails]: ...


    class azure.mgmt.education.operations.LabsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def create_or_update(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                invoice_section_name: str, 
                parameters: LabDetails, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LabDetails: ...

        @overload
        def create_or_update(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                invoice_section_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LabDetails: ...

        @distributed_trace
        def delete(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                invoice_section_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @overload
        def generate_invite_code(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                invoice_section_name: str, 
                parameters: InviteCodeGenerateRequest, 
                only_update_student_count_parameter: Optional[bool] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LabDetails: ...

        @overload
        def generate_invite_code(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                invoice_section_name: str, 
                parameters: IO, 
                only_update_student_count_parameter: Optional[bool] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LabDetails: ...

        @distributed_trace
        def get(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                invoice_section_name: str, 
                include_budget: Optional[bool] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> LabDetails: ...

        @distributed_trace
        def list(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                invoice_section_name: str, 
                include_budget: Optional[bool] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[LabDetails]: ...

        @distributed_trace
        def list_all(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                include_budget: Optional[bool] = None, 
                include_deleted: Optional[bool] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[LabDetails]: ...


    class azure.mgmt.education.operations.Operations:

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
            ) -> OperationListResult: ...


    class azure.mgmt.education.operations.StudentLabsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get(
                self, 
                student_lab_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> StudentLabDetails: ...

        @distributed_trace
        def list_all(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[StudentLabDetails]: ...


    class azure.mgmt.education.operations.StudentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def create_or_update(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                invoice_section_name: str, 
                student_alias: str, 
                parameters: StudentDetails, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StudentDetails: ...

        @overload
        def create_or_update(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                invoice_section_name: str, 
                student_alias: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StudentDetails: ...

        @distributed_trace
        def delete(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                invoice_section_name: str, 
                student_alias: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                invoice_section_name: str, 
                student_alias: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> StudentDetails: ...

        @distributed_trace
        def list(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                invoice_section_name: str, 
                include_deleted: Optional[bool] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[StudentDetails]: ...


```