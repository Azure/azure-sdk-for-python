```py
namespace azure.mgmt.billingtrust

    class azure.mgmt.billingtrust.BillingTrustMgmtClient: implements ContextManager 
        assessments: AssessmentsOperations
        operations: Operations
        rules: RulesOperations

        def __init__(
                self, 
                credential: TokenCredential, 
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


namespace azure.mgmt.billingtrust.aio

    class azure.mgmt.billingtrust.aio.BillingTrustMgmtClient: implements AsyncContextManager 
        assessments: AssessmentsOperations
        operations: Operations
        rules: RulesOperations

        def __init__(
                self, 
                credential: AsyncTokenCredential, 
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


namespace azure.mgmt.billingtrust.aio.operations

    class azure.mgmt.billingtrust.aio.operations.AssessmentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_uri: str, 
                resource: Assessment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_uri: str, 
                resource: Assessment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_uri: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_uri: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_uri: str, 
                **kwargs: Any
            ) -> Assessment: ...

        @distributed_trace
        def list(
                self, 
                resource_uri: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Assessment]: ...

        @distributed_trace_async
        async def list_upload_token(
                self, 
                resource_uri: str, 
                **kwargs: Any
            ) -> GenerateUploadTokenResponse: ...


    class azure.mgmt.billingtrust.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


    class azure.mgmt.billingtrust.aio.operations.RulesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_uri: str, 
                rule_name: str, 
                resource: Rule, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Rule: ...

        @overload
        async def create_or_update(
                self, 
                resource_uri: str, 
                rule_name: str, 
                resource: Rule, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Rule: ...

        @overload
        async def create_or_update(
                self, 
                resource_uri: str, 
                rule_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Rule: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_uri: str, 
                rule_name: str, 
                **kwargs: Any
            ) -> Rule: ...

        @distributed_trace
        def list(
                self, 
                resource_uri: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Rule]: ...

        @overload
        async def update(
                self, 
                resource_uri: str, 
                rule_name: str, 
                properties: RulePatchProperties, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Rule: ...

        @overload
        async def update(
                self, 
                resource_uri: str, 
                rule_name: str, 
                properties: RulePatchProperties, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Rule: ...

        @overload
        async def update(
                self, 
                resource_uri: str, 
                rule_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Rule: ...


namespace azure.mgmt.billingtrust.models

    class azure.mgmt.billingtrust.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.billingtrust.models.Assessment(ExtensionResource):
        id: str
        name: str
        properties: Optional[AssessmentProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[AssessmentProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billingtrust.models.AssessmentProperties(_Model):
        assessment_type: Union[str, AssessmentType]
        error: Optional[ErrorDetail]
        evaluation_state: Optional[Union[str, AssessmentState]]
        initial_values: Optional[list[InitialRuleValueBase]]
        next_evaluation: Optional[datetime]
        provisioning_state: Optional[Union[str, ProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                assessment_type: Union[str, AssessmentType], 
                initial_values: Optional[list[InitialRuleValueBase]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billingtrust.models.AssessmentState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTION_REQUIRED = "actionRequired"
        EXPIRED = "expired"
        FAILED = "failed"
        FAILED_WITH_OVERRIDE = "failedWithOverride"
        PENDING = "pending"
        RUNNING = "running"
        SUCCEEDED = "succeeded"
        SUCCEEDED_WITH_OVERRIDE = "succeededWithOverride"
        UNDER_REVIEW = "underReview"


    class azure.mgmt.billingtrust.models.AssessmentType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BUSINESS_VERIFICATION = "BusinessVerification"
        EDU = "Edu"
        PAYEE_ENROLLMENT = "PayeeEnrollment"
        PAYEE_PROFILE = "PayeeProfile"


    class azure.mgmt.billingtrust.models.BusinessVerificationRulePatchProperties(RulePatchProperties, discriminator='businessVerification'):
        external_id: Optional[ExternalId]
        kind: Literal[RuleKind.BUSINESS_VERIFICATION]
        supplemental_documents: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                external_id: Optional[ExternalId] = ..., 
                supplemental_documents: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billingtrust.models.BusinessVerificationRuleProperties(RuleProperties, discriminator='businessVerification'):
        error: ErrorDetail
        evaluation_state: Union[str, RuleState]
        external_id: Optional[ExternalId]
        kind: Literal[RuleKind.BUSINESS_VERIFICATION]
        provisioning_state: Union[str, ProvisioningState]
        registration_number: Optional[RegistrationNumber]
        sold_to: Optional[SoldTo]
        supplemental_documents: Optional[list[str]]
        tax_ids: Optional[list[TaxId]]

        @overload
        def __init__(
                self, 
                *, 
                external_id: Optional[ExternalId] = ..., 
                supplemental_documents: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billingtrust.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.billingtrust.models.DomainEntry(_Model):
        domain_names: list[str]
        error: Optional[ErrorDetail]
        state: Optional[Union[str, DomainEntryState]]
        tenant_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                domain_names: list[str], 
                tenant_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billingtrust.models.DomainEntryState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTION_REQUIRED = "actionRequired"
        FAILED = "failed"
        PENDING = "pending"
        SUCCEEDED = "succeeded"


    class azure.mgmt.billingtrust.models.EduInitialValue(InitialRuleValueBase, discriminator='eduQualification'):
        domains: list[DomainEntry]
        kind: Literal[RuleKind.EDU_QUALIFICATION]

        @overload
        def __init__(
                self, 
                *, 
                domains: list[DomainEntry]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billingtrust.models.EduQualificationRulePatchProperties(RulePatchProperties, discriminator='eduQualification'):
        kind: Literal[RuleKind.EDU_QUALIFICATION]
        supplemental_documents: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                supplemental_documents: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billingtrust.models.EduQualificationRuleProperties(RuleProperties, discriminator='eduQualification'):
        domains: Optional[list[DomainEntry]]
        error: ErrorDetail
        evaluation_state: Union[str, RuleState]
        kind: Literal[RuleKind.EDU_QUALIFICATION]
        provisioning_state: Union[str, ProvisioningState]
        supplemental_documents: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                domains: Optional[list[DomainEntry]] = ..., 
                supplemental_documents: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billingtrust.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.billingtrust.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.billingtrust.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billingtrust.models.ExtensionResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.billingtrust.models.ExternalId(_Model):
        type: str
        value: str

        @overload
        def __init__(
                self, 
                *, 
                type: str, 
                value: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billingtrust.models.GenerateUploadTokenResponse(_Model):
        token: str

        @overload
        def __init__(
                self, 
                *, 
                token: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billingtrust.models.InitialRuleValueBase(_Model):
        kind: str

        @overload
        def __init__(
                self, 
                *, 
                kind: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billingtrust.models.Operation(_Model):
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


    class azure.mgmt.billingtrust.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.billingtrust.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.billingtrust.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        CANCELED = "Canceled"
        FAILED = "Failed"
        PROVISIONING = "Provisioning"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.billingtrust.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.billingtrust.models.RegistrationNumber(_Model):
        registration_requirement: Optional[Union[str, RegistrationRequirement]]
        type: Optional[list[str]]
        value: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                registration_requirement: Optional[Union[str, RegistrationRequirement]] = ..., 
                type: Optional[list[str]] = ..., 
                value: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billingtrust.models.RegistrationRequirement(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NOT_APPLICABLE = "notApplicable"
        OPTIONAL = "optional"
        REQUIRED = "required"


    class azure.mgmt.billingtrust.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.billingtrust.models.Rule(ProxyResource):
        id: str
        name: str
        properties: Optional[RuleProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[RuleProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billingtrust.models.RuleKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BUSINESS_VERIFICATION = "businessVerification"
        EDU_QUALIFICATION = "eduQualification"


    class azure.mgmt.billingtrust.models.RulePatchProperties(_Model):
        kind: str

        @overload
        def __init__(
                self, 
                *, 
                kind: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billingtrust.models.RuleProperties(_Model):
        error: Optional[ErrorDetail]
        evaluation_state: Optional[Union[str, RuleState]]
        kind: str
        provisioning_state: Optional[Union[str, ProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                kind: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billingtrust.models.RuleState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTION_REQUIRED = "actionRequired"
        EXPIRED = "expired"
        FAILED = "failed"
        FAILED_WITH_OVERRIDE = "failedWithOverride"
        PENDING = "pending"
        RUNNING = "running"
        SKIPPED = "skipped"
        SUCCEEDED = "succeeded"
        SUCCEEDED_WITH_OVERRIDE = "succeededWithOverride"
        UNDER_REVIEW = "underReview"


    class azure.mgmt.billingtrust.models.SoldTo(_Model):
        address_line1: Optional[str]
        address_line2: Optional[str]
        address_line3: Optional[str]
        city: Optional[str]
        company_name: Optional[str]
        country: Optional[str]
        district: Optional[str]
        email: Optional[str]
        first_name: Optional[str]
        last_name: Optional[str]
        middle_name: Optional[str]
        phone_number: Optional[str]
        postal_code: Optional[str]
        region: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                address_line1: Optional[str] = ..., 
                address_line2: Optional[str] = ..., 
                address_line3: Optional[str] = ..., 
                city: Optional[str] = ..., 
                company_name: Optional[str] = ..., 
                country: Optional[str] = ..., 
                district: Optional[str] = ..., 
                email: Optional[str] = ..., 
                first_name: Optional[str] = ..., 
                last_name: Optional[str] = ..., 
                middle_name: Optional[str] = ..., 
                phone_number: Optional[str] = ..., 
                postal_code: Optional[str] = ..., 
                region: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billingtrust.models.SystemData(_Model):
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


    class azure.mgmt.billingtrust.models.TaxId(_Model):
        country: Optional[str]
        scope: Optional[str]
        status: Optional[Union[str, TaxIdStatus]]
        type: Optional[str]
        value: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                country: Optional[str] = ..., 
                scope: Optional[str] = ..., 
                status: Optional[Union[str, TaxIdStatus]] = ..., 
                type: Optional[str] = ..., 
                value: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billingtrust.models.TaxIdStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INVALID = "invalid"
        OTHER = "other"
        VALID = "valid"


namespace azure.mgmt.billingtrust.operations

    class azure.mgmt.billingtrust.operations.AssessmentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_uri: str, 
                resource: Assessment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_uri: str, 
                resource: Assessment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_uri: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_uri: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_uri: str, 
                **kwargs: Any
            ) -> Assessment: ...

        @distributed_trace
        def list(
                self, 
                resource_uri: str, 
                **kwargs: Any
            ) -> ItemPaged[Assessment]: ...

        @distributed_trace
        def list_upload_token(
                self, 
                resource_uri: str, 
                **kwargs: Any
            ) -> GenerateUploadTokenResponse: ...


    class azure.mgmt.billingtrust.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


    class azure.mgmt.billingtrust.operations.RulesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                resource_uri: str, 
                rule_name: str, 
                resource: Rule, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Rule: ...

        @overload
        def create_or_update(
                self, 
                resource_uri: str, 
                rule_name: str, 
                resource: Rule, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Rule: ...

        @overload
        def create_or_update(
                self, 
                resource_uri: str, 
                rule_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Rule: ...

        @distributed_trace
        def get(
                self, 
                resource_uri: str, 
                rule_name: str, 
                **kwargs: Any
            ) -> Rule: ...

        @distributed_trace
        def list(
                self, 
                resource_uri: str, 
                **kwargs: Any
            ) -> ItemPaged[Rule]: ...

        @overload
        def update(
                self, 
                resource_uri: str, 
                rule_name: str, 
                properties: RulePatchProperties, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Rule: ...

        @overload
        def update(
                self, 
                resource_uri: str, 
                rule_name: str, 
                properties: RulePatchProperties, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Rule: ...

        @overload
        def update(
                self, 
                resource_uri: str, 
                rule_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Rule: ...


namespace azure.mgmt.billingtrust.types

    class azure.mgmt.billingtrust.types.Assessment(ExtensionResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('AssessmentProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: AssessmentProperties
        system_data: SystemData
        type: str


    class azure.mgmt.billingtrust.types.AssessmentProperties(TypedDict, total=False):
        key "assessmentType": Required[Union[str, AssessmentType]]
        key "error": ForwardRef('ErrorDetail', module='types')
        key "evaluationState": Union[str, AssessmentState]
        key "nextEvaluation": str
        key "provisioningState": Union[str, ProvisioningState]
        assessment_type: Union[str, AssessmentType]
        error: ErrorDetail
        evaluation_state: Union[str, AssessmentState]
        initialValues: list[InitialRuleValueBase]
        initial_values: list[InitialRuleValueBase]
        next_evaluation: str
        provisioning_state: Union[str, ProvisioningState]


    class azure.mgmt.billingtrust.types.BusinessVerificationRulePatchProperties(TypedDict, total=False):
        key "externalId": ForwardRef('ExternalId', module='types')
        key "kind": Required[Literal[RuleKind.BUSINESS_VERIFICATION]]
        external_id: ExternalId
        kind: Literal[RuleKind.BUSINESS_VERIFICATION]
        supplementalDocuments: list[str]
        supplemental_documents: list[str]


    class azure.mgmt.billingtrust.types.BusinessVerificationRuleProperties(TypedDict, total=False):
        key "error": ForwardRef('ErrorDetail', module='types')
        key "evaluationState": Union[str, RuleState]
        key "externalId": ForwardRef('ExternalId', module='types')
        key "kind": Required[Literal[RuleKind.BUSINESS_VERIFICATION]]
        key "provisioningState": Union[str, ProvisioningState]
        key "registrationNumber": ForwardRef('RegistrationNumber', module='types')
        key "soldTo": ForwardRef('SoldTo', module='types')
        error: ErrorDetail
        evaluation_state: Union[str, RuleState]
        external_id: ExternalId
        kind: Literal[RuleKind.BUSINESS_VERIFICATION]
        provisioning_state: Union[str, ProvisioningState]
        registration_number: RegistrationNumber
        sold_to: SoldTo
        supplementalDocuments: list[str]
        supplemental_documents: list[str]
        taxIds: list[TaxId]
        tax_ids: list[TaxId]


    class azure.mgmt.billingtrust.types.DomainEntry(TypedDict, total=False):
        key "domainNames": Required[list[str]]
        key "error": ForwardRef('ErrorDetail', module='types')
        key "state": Union[str, DomainEntryState]
        key "tenantId": str
        domain_names: list[str]
        error: ErrorDetail
        state: Union[str, DomainEntryState]
        tenant_id: str


    class azure.mgmt.billingtrust.types.EduInitialValue(TypedDict, total=False):
        key "domains": Required[list[DomainEntry]]
        key "kind": Required[Literal[RuleKind.EDU_QUALIFICATION]]
        domains: list[DomainEntry]
        kind: Literal[RuleKind.EDU_QUALIFICATION]


    class azure.mgmt.billingtrust.types.EduQualificationRulePatchProperties(TypedDict, total=False):
        key "kind": Required[Literal[RuleKind.EDU_QUALIFICATION]]
        kind: Literal[RuleKind.EDU_QUALIFICATION]
        supplementalDocuments: list[str]
        supplemental_documents: list[str]


    class azure.mgmt.billingtrust.types.EduQualificationRuleProperties(TypedDict, total=False):
        key "error": ForwardRef('ErrorDetail', module='types')
        key "evaluationState": Union[str, RuleState]
        key "kind": Required[Literal[RuleKind.EDU_QUALIFICATION]]
        key "provisioningState": Union[str, ProvisioningState]
        domains: list[DomainEntry]
        error: ErrorDetail
        evaluation_state: Union[str, RuleState]
        kind: Literal[RuleKind.EDU_QUALIFICATION]
        provisioning_state: Union[str, ProvisioningState]
        supplementalDocuments: list[str]
        supplemental_documents: list[str]


    class azure.mgmt.billingtrust.types.ErrorAdditionalInfo(TypedDict, total=False):
        key "info": Any
        key "type": str
        info: Any
        type: str


    class azure.mgmt.billingtrust.types.ErrorDetail(TypedDict, total=False):
        key "code": str
        key "message": str
        key "target": str
        additionalInfo: list[ErrorAdditionalInfo]
        additional_info: list[ErrorAdditionalInfo]
        code: str
        details: list[ErrorDetail]
        message: str
        target: str


    class azure.mgmt.billingtrust.types.ErrorResponse(TypedDict, total=False):
        key "error": ForwardRef('ErrorDetail', module='types')
        error: ErrorDetail


    class azure.mgmt.billingtrust.types.ExtensionResource(Resource):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.billingtrust.types.ExternalId(TypedDict, total=False):
        key "type": Required[str]
        key "value": Required[str]
        type: str
        value: str


    class azure.mgmt.billingtrust.types.GenerateUploadTokenResponse(TypedDict, total=False):
        key "token": Required[str]
        token: str


    class azure.mgmt.billingtrust.types.InitialRuleValueBase(TypedDict, total=False):
        key "domains": Required[list[DomainEntry]]
        key "kind": Required[Literal[RuleKind.EDU_QUALIFICATION]]
        domains: list[DomainEntry]
        kind: Literal[RuleKind.EDU_QUALIFICATION]


    class azure.mgmt.billingtrust.types.Operation(TypedDict, total=False):
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


    class azure.mgmt.billingtrust.types.OperationDisplay(TypedDict, total=False):
        key "description": str
        key "operation": str
        key "provider": str
        key "resource": str
        description: str
        operation: str
        provider: str
        resource: str


    class azure.mgmt.billingtrust.types.ProxyResource(Resource):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.billingtrust.types.RegistrationNumber(TypedDict, total=False):
        key "registrationRequirement": Union[str, RegistrationRequirement]
        key "value": str
        registration_requirement: Union[str, RegistrationRequirement]
        type: list[str]
        value: str


    class azure.mgmt.billingtrust.types.Resource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.billingtrust.types.Rule(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('RuleProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: RuleProperties
        system_data: SystemData
        type: str


    class azure.mgmt.billingtrust.types.RuleKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BUSINESS_VERIFICATION = "businessVerification"
        EDU_QUALIFICATION = "eduQualification"


    class azure.mgmt.billingtrust.types.SoldTo(TypedDict, total=False):
        key "addressLine1": str
        key "addressLine2": str
        key "addressLine3": str
        key "city": str
        key "companyName": str
        key "country": str
        key "district": str
        key "email": str
        key "firstName": str
        key "lastName": str
        key "middleName": str
        key "phoneNumber": str
        key "postalCode": str
        key "region": str
        address_line1: str
        address_line2: str
        address_line3: str
        city: str
        company_name: str
        country: str
        district: str
        email: str
        first_name: str
        last_name: str
        middle_name: str
        phone_number: str
        postal_code: str
        region: str


    class azure.mgmt.billingtrust.types.SystemData(TypedDict, total=False):
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


    class azure.mgmt.billingtrust.types.TaxId(TypedDict, total=False):
        key "country": str
        key "scope": str
        key "status": Union[str, TaxIdStatus]
        key "type": str
        key "value": str
        country: str
        scope: str
        status: Union[str, TaxIdStatus]
        type: str
        value: str


```