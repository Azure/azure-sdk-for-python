```py
namespace azure.mgmt.confidentialledger

    class azure.mgmt.confidentialledger.ConfidentialLedgerMgmtClient(_ConfidentialLedgerMgmtClientOperationsMixin): implements ContextManager 
        ledger: LedgerOperations
        operations: Operations

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

        @overload
        def check_name_availability(
                self, 
                name_availability_request: CheckNameAvailabilityRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResponse: ...

        @overload
        def check_name_availability(
                self, 
                name_availability_request: CheckNameAvailabilityRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResponse: ...

        @overload
        def check_name_availability(
                self, 
                name_availability_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResponse: ...

        def close(self) -> None: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> HttpResponse: ...


namespace azure.mgmt.confidentialledger.aio

    class azure.mgmt.confidentialledger.aio.ConfidentialLedgerMgmtClient(_ConfidentialLedgerMgmtClientOperationsMixin): implements AsyncContextManager 
        ledger: LedgerOperations
        operations: Operations

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

        @overload
        async def check_name_availability(
                self, 
                name_availability_request: CheckNameAvailabilityRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResponse: ...

        @overload
        async def check_name_availability(
                self, 
                name_availability_request: CheckNameAvailabilityRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResponse: ...

        @overload
        async def check_name_availability(
                self, 
                name_availability_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResponse: ...

        async def close(self) -> None: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> Awaitable[AsyncHttpResponse]: ...


namespace azure.mgmt.confidentialledger.aio.operations

    class azure.mgmt.confidentialledger.aio.operations.LedgerOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                ledger_name: str, 
                confidential_ledger: ConfidentialLedger, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ConfidentialLedger]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                ledger_name: str, 
                confidential_ledger: ConfidentialLedger, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ConfidentialLedger]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                ledger_name: str, 
                confidential_ledger: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ConfidentialLedger]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                ledger_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_files_export(
                self, 
                resource_group_name: str, 
                ledger_name: str, 
                confidential_ledger: ConfidentialLedgerFilesExport, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ConfidentialLedgerFilesExportResponse]: ...

        @overload
        async def begin_files_export(
                self, 
                resource_group_name: str, 
                ledger_name: str, 
                confidential_ledger: ConfidentialLedgerFilesExport, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ConfidentialLedgerFilesExportResponse]: ...

        @overload
        async def begin_files_export(
                self, 
                resource_group_name: str, 
                ledger_name: str, 
                confidential_ledger: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ConfidentialLedgerFilesExportResponse]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                ledger_name: str, 
                confidential_ledger: ConfidentialLedger, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ConfidentialLedger]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                ledger_name: str, 
                confidential_ledger: ConfidentialLedger, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ConfidentialLedger]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                ledger_name: str, 
                confidential_ledger: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ConfidentialLedger]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                ledger_name: str, 
                **kwargs: Any
            ) -> ConfidentialLedger: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[ConfidentialLedger]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[ConfidentialLedger]: ...


    class azure.mgmt.confidentialledger.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[ResourceProviderOperationDefinition]: ...


namespace azure.mgmt.confidentialledger.models

    class azure.mgmt.confidentialledger.models.AADBasedSecurityPrincipal(_Model):
        ledger_role_name: Optional[Union[str, LedgerRoleName]]
        principal_id: Optional[str]
        tenant_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                ledger_role_name: Optional[Union[str, LedgerRoleName]] = ..., 
                principal_id: Optional[str] = ..., 
                tenant_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.confidentialledger.models.ApplicationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CODE_TRANSPARENCY = "CodeTransparency"
        CONFIDENTIAL_LEDGER = "ConfidentialLedger"


    class azure.mgmt.confidentialledger.models.CertBasedSecurityPrincipal(_Model):
        cert: Optional[str]
        ledger_role_name: Optional[Union[str, LedgerRoleName]]

        @overload
        def __init__(
                self, 
                *, 
                cert: Optional[str] = ..., 
                ledger_role_name: Optional[Union[str, LedgerRoleName]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.confidentialledger.models.CheckNameAvailabilityReason(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALREADY_EXISTS = "AlreadyExists"
        INVALID = "Invalid"


    class azure.mgmt.confidentialledger.models.CheckNameAvailabilityRequest(_Model):
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


    class azure.mgmt.confidentialledger.models.CheckNameAvailabilityResponse(_Model):
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


    class azure.mgmt.confidentialledger.models.ConfidentialLedger(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[LedgerProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[LedgerProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.confidentialledger.models.ConfidentialLedgerFilesExport(_Model):
        restore_region: Optional[str]
        uri: str

        @overload
        def __init__(
                self, 
                *, 
                restore_region: Optional[str] = ..., 
                uri: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.confidentialledger.models.ConfidentialLedgerFilesExportResponse(_Model):
        message: Optional[str]


    class azure.mgmt.confidentialledger.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.confidentialledger.models.EnclavePlatform(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AMD_SEV_SNP = "AmdSevSnp"
        INTEL_SGX = "IntelSgx"


    class azure.mgmt.confidentialledger.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.confidentialledger.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.confidentialledger.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.confidentialledger.models.LedgerProperties(_Model):
        aad_based_security_principals: Optional[list[AADBasedSecurityPrincipal]]
        application_type: Optional[Union[str, ApplicationType]]
        cert_based_security_principals: Optional[list[CertBasedSecurityPrincipal]]
        enclave_platform: Optional[Union[str, EnclavePlatform]]
        host_level: Optional[str]
        identity_service_uri: Optional[str]
        ledger_internal_namespace: Optional[str]
        ledger_name: Optional[str]
        ledger_sku: Optional[Union[str, LedgerSku]]
        ledger_type: Optional[Union[str, LedgerType]]
        ledger_uri: Optional[str]
        max_body_size_in_mb: Optional[int]
        node_count: Optional[int]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        running_state: Optional[Union[str, RunningState]]
        scitt_configuration: Optional[str]
        storage_usage_bytes: Optional[int]
        subject_name: Optional[str]
        worker_threads: Optional[int]
        write_lb_address_prefix: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                aad_based_security_principals: Optional[list[AADBasedSecurityPrincipal]] = ..., 
                application_type: Optional[Union[str, ApplicationType]] = ..., 
                cert_based_security_principals: Optional[list[CertBasedSecurityPrincipal]] = ..., 
                host_level: Optional[str] = ..., 
                ledger_sku: Optional[Union[str, LedgerSku]] = ..., 
                ledger_type: Optional[Union[str, LedgerType]] = ..., 
                max_body_size_in_mb: Optional[int] = ..., 
                node_count: Optional[int] = ..., 
                running_state: Optional[Union[str, RunningState]] = ..., 
                scitt_configuration: Optional[str] = ..., 
                subject_name: Optional[str] = ..., 
                worker_threads: Optional[int] = ..., 
                write_lb_address_prefix: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.confidentialledger.models.LedgerRoleName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ADMINISTRATOR = "Administrator"
        CONTRIBUTOR = "Contributor"
        READER = "Reader"


    class azure.mgmt.confidentialledger.models.LedgerSku(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BASIC = "Basic"
        STANDARD = "Standard"
        UNKNOWN = "Unknown"


    class azure.mgmt.confidentialledger.models.LedgerType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PRIVATE = "Private"
        PUBLIC = "Public"
        UNKNOWN = "Unknown"


    class azure.mgmt.confidentialledger.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UNKNOWN = "Unknown"
        UPDATING = "Updating"


    class azure.mgmt.confidentialledger.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.confidentialledger.models.ResourceProviderOperationDefinition(_Model):
        display: Optional[ResourceProviderOperationDisplay]
        is_data_action: Optional[bool]
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                display: Optional[ResourceProviderOperationDisplay] = ..., 
                is_data_action: Optional[bool] = ..., 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.confidentialledger.models.ResourceProviderOperationDisplay(_Model):
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


    class azure.mgmt.confidentialledger.models.RunningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        PAUSED = "Paused"
        PAUSING = "Pausing"
        RESUMING = "Resuming"
        UNKNOWN = "Unknown"


    class azure.mgmt.confidentialledger.models.SystemData(_Model):
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


    class azure.mgmt.confidentialledger.models.TrackedResource(Resource):
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


namespace azure.mgmt.confidentialledger.operations

    class azure.mgmt.confidentialledger.operations.LedgerOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                ledger_name: str, 
                confidential_ledger: ConfidentialLedger, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ConfidentialLedger]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                ledger_name: str, 
                confidential_ledger: ConfidentialLedger, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ConfidentialLedger]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                ledger_name: str, 
                confidential_ledger: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ConfidentialLedger]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                ledger_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_files_export(
                self, 
                resource_group_name: str, 
                ledger_name: str, 
                confidential_ledger: ConfidentialLedgerFilesExport, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ConfidentialLedgerFilesExportResponse]: ...

        @overload
        def begin_files_export(
                self, 
                resource_group_name: str, 
                ledger_name: str, 
                confidential_ledger: ConfidentialLedgerFilesExport, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ConfidentialLedgerFilesExportResponse]: ...

        @overload
        def begin_files_export(
                self, 
                resource_group_name: str, 
                ledger_name: str, 
                confidential_ledger: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ConfidentialLedgerFilesExportResponse]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                ledger_name: str, 
                confidential_ledger: ConfidentialLedger, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ConfidentialLedger]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                ledger_name: str, 
                confidential_ledger: ConfidentialLedger, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ConfidentialLedger]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                ledger_name: str, 
                confidential_ledger: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ConfidentialLedger]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                ledger_name: str, 
                **kwargs: Any
            ) -> ConfidentialLedger: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[ConfidentialLedger]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[ConfidentialLedger]: ...


    class azure.mgmt.confidentialledger.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[ResourceProviderOperationDefinition]: ...


namespace azure.mgmt.confidentialledger.types

    class azure.mgmt.confidentialledger.types.AADBasedSecurityPrincipal(TypedDict, total=False):
        key "ledgerRoleName": Union[str, LedgerRoleName]
        key "principalId": str
        key "tenantId": str
        ledger_role_name: Union[str, LedgerRoleName]
        principal_id: str
        tenant_id: str


    class azure.mgmt.confidentialledger.types.CertBasedSecurityPrincipal(TypedDict, total=False):
        key "cert": str
        key "ledgerRoleName": Union[str, LedgerRoleName]
        cert: str
        ledger_role_name: Union[str, LedgerRoleName]


    class azure.mgmt.confidentialledger.types.CheckNameAvailabilityRequest(TypedDict, total=False):
        key "name": str
        key "type": str
        name: str
        type: str


    class azure.mgmt.confidentialledger.types.CheckNameAvailabilityResponse(TypedDict, total=False):
        key "message": str
        key "nameAvailable": bool
        key "reason": Union[str, CheckNameAvailabilityReason]
        message: str
        name_available: bool
        reason: Union[str, CheckNameAvailabilityReason]


    class azure.mgmt.confidentialledger.types.ConfidentialLedger(TrackedResource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('LedgerProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: LedgerProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.confidentialledger.types.ConfidentialLedgerFilesExport(TypedDict, total=False):
        key "restoreRegion": str
        key "uri": Required[str]
        restore_region: str
        uri: str


    class azure.mgmt.confidentialledger.types.ConfidentialLedgerFilesExportResponse(TypedDict, total=False):
        key "message": str
        message: str


    class azure.mgmt.confidentialledger.types.ErrorAdditionalInfo(TypedDict, total=False):
        key "info": Any
        key "type": str
        info: Any
        type: str


    class azure.mgmt.confidentialledger.types.ErrorDetail(TypedDict, total=False):
        key "code": str
        key "message": str
        key "target": str
        additionalInfo: list[ErrorAdditionalInfo]
        additional_info: list[ErrorAdditionalInfo]
        code: str
        details: list[ErrorDetail]
        message: str
        target: str


    class azure.mgmt.confidentialledger.types.ErrorResponse(TypedDict, total=False):
        key "error": ForwardRef('ErrorDetail', module='types')
        error: ErrorDetail


    class azure.mgmt.confidentialledger.types.LedgerProperties(TypedDict, total=False):
        key "applicationType": Union[str, ApplicationType]
        key "enclavePlatform": Union[str, EnclavePlatform]
        key "hostLevel": str
        key "identityServiceUri": str
        key "ledgerInternalNamespace": str
        key "ledgerName": str
        key "ledgerSku": Union[str, LedgerSku]
        key "ledgerType": Union[str, LedgerType]
        key "ledgerUri": str
        key "maxBodySizeInMb": int
        key "nodeCount": int
        key "provisioningState": Union[str, ProvisioningState]
        key "runningState": Union[str, RunningState]
        key "scittConfiguration": str
        key "storageUsageBytes": int
        key "subjectName": str
        key "workerThreads": int
        key "writeLBAddressPrefix": str
        aadBasedSecurityPrincipals: list[AADBasedSecurityPrincipal]
        aad_based_security_principals: list[AADBasedSecurityPrincipal]
        application_type: Union[str, ApplicationType]
        certBasedSecurityPrincipals: list[CertBasedSecurityPrincipal]
        cert_based_security_principals: list[CertBasedSecurityPrincipal]
        enclave_platform: Union[str, EnclavePlatform]
        host_level: str
        identity_service_uri: str
        ledger_internal_namespace: str
        ledger_name: str
        ledger_sku: Union[str, LedgerSku]
        ledger_type: Union[str, LedgerType]
        ledger_uri: str
        max_body_size_in_mb: int
        node_count: int
        provisioning_state: Union[str, ProvisioningState]
        running_state: Union[str, RunningState]
        scitt_configuration: str
        storage_usage_bytes: int
        subject_name: str
        worker_threads: int
        write_lb_address_prefix: str


    class azure.mgmt.confidentialledger.types.Resource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.confidentialledger.types.ResourceProviderOperationDefinition(TypedDict, total=False):
        key "display": ForwardRef('ResourceProviderOperationDisplay', module='types')
        key "isDataAction": bool
        key "name": str
        display: ResourceProviderOperationDisplay
        is_data_action: bool
        name: str


    class azure.mgmt.confidentialledger.types.ResourceProviderOperationDisplay(TypedDict, total=False):
        key "description": str
        key "operation": str
        key "provider": str
        key "resource": str
        description: str
        operation: str
        provider: str
        resource: str


    class azure.mgmt.confidentialledger.types.SystemData(TypedDict, total=False):
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


    class azure.mgmt.confidentialledger.types.TrackedResource(Resource):
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


```