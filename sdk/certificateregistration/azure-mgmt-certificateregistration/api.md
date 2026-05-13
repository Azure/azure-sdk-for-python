```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.certificateregistration

    class azure.mgmt.certificateregistration.CertificateRegistrationMgmtClient: implements ContextManager 
        app_service_certificate_orders: AppServiceCertificateOrdersOperations
        certificate_orders_diagnostics: CertificateOrdersDiagnosticsOperations
        certificate_registration_provider: CertificateRegistrationProviderOperations

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


namespace azure.mgmt.certificateregistration.aio

    class azure.mgmt.certificateregistration.aio.CertificateRegistrationMgmtClient: implements AsyncContextManager 
        app_service_certificate_orders: AppServiceCertificateOrdersOperations
        certificate_orders_diagnostics: CertificateOrdersDiagnosticsOperations
        certificate_registration_provider: CertificateRegistrationProviderOperations

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


namespace azure.mgmt.certificateregistration.aio.operations

    class azure.mgmt.certificateregistration.aio.operations.AppServiceCertificateOrdersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                certificate_order_name: str, 
                certificate_distinguished_name: AppServiceCertificateOrder, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AppServiceCertificateOrder]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                certificate_order_name: str, 
                certificate_distinguished_name: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AppServiceCertificateOrder]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                certificate_order_name: str, 
                certificate_distinguished_name: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AppServiceCertificateOrder]: ...

        @overload
        async def begin_create_or_update_certificate(
                self, 
                resource_group_name: str, 
                certificate_order_name: str, 
                name: str, 
                key_vault_certificate: AppServiceCertificateResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AppServiceCertificateResource]: ...

        @overload
        async def begin_create_or_update_certificate(
                self, 
                resource_group_name: str, 
                certificate_order_name: str, 
                name: str, 
                key_vault_certificate: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AppServiceCertificateResource]: ...

        @overload
        async def begin_create_or_update_certificate(
                self, 
                resource_group_name: str, 
                certificate_order_name: str, 
                name: str, 
                key_vault_certificate: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AppServiceCertificateResource]: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                certificate_order_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def delete_certificate(
                self, 
                resource_group_name: str, 
                certificate_order_name: str, 
                name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                certificate_order_name: str, 
                **kwargs: Any
            ) -> AppServiceCertificateOrder: ...

        @distributed_trace_async
        async def get_certificate(
                self, 
                resource_group_name: str, 
                certificate_order_name: str, 
                name: str, 
                **kwargs: Any
            ) -> AppServiceCertificateResource: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[AppServiceCertificateOrder]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[AppServiceCertificateOrder]: ...

        @distributed_trace
        def list_certificates(
                self, 
                resource_group_name: str, 
                certificate_order_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[AppServiceCertificateResource]: ...

        @overload
        async def reissue(
                self, 
                resource_group_name: str, 
                certificate_order_name: str, 
                reissue_certificate_order_request: ReissueCertificateOrderRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def reissue(
                self, 
                resource_group_name: str, 
                certificate_order_name: str, 
                reissue_certificate_order_request: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def reissue(
                self, 
                resource_group_name: str, 
                certificate_order_name: str, 
                reissue_certificate_order_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def renew(
                self, 
                resource_group_name: str, 
                certificate_order_name: str, 
                renew_certificate_order_request: RenewCertificateOrderRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def renew(
                self, 
                resource_group_name: str, 
                certificate_order_name: str, 
                renew_certificate_order_request: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def renew(
                self, 
                resource_group_name: str, 
                certificate_order_name: str, 
                renew_certificate_order_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def resend_email(
                self, 
                resource_group_name: str, 
                certificate_order_name: str, 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def resend_request_emails(
                self, 
                resource_group_name: str, 
                certificate_order_name: str, 
                name_identifier: NameIdentifier, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def resend_request_emails(
                self, 
                resource_group_name: str, 
                certificate_order_name: str, 
                name_identifier: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def resend_request_emails(
                self, 
                resource_group_name: str, 
                certificate_order_name: str, 
                name_identifier: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def retrieve_certificate_actions(
                self, 
                resource_group_name: str, 
                name: str, 
                **kwargs: Any
            ) -> List[CertificateOrderAction]: ...

        @distributed_trace_async
        async def retrieve_certificate_email_history(
                self, 
                resource_group_name: str, 
                name: str, 
                **kwargs: Any
            ) -> List[CertificateEmail]: ...

        @overload
        async def retrieve_site_seal(
                self, 
                resource_group_name: str, 
                certificate_order_name: str, 
                site_seal_request: SiteSealRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SiteSeal: ...

        @overload
        async def retrieve_site_seal(
                self, 
                resource_group_name: str, 
                certificate_order_name: str, 
                site_seal_request: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SiteSeal: ...

        @overload
        async def retrieve_site_seal(
                self, 
                resource_group_name: str, 
                certificate_order_name: str, 
                site_seal_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SiteSeal: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                certificate_order_name: str, 
                certificate_distinguished_name: AppServiceCertificateOrderPatchResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AppServiceCertificateOrder: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                certificate_order_name: str, 
                certificate_distinguished_name: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AppServiceCertificateOrder: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                certificate_order_name: str, 
                certificate_distinguished_name: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AppServiceCertificateOrder: ...

        @overload
        async def update_certificate(
                self, 
                resource_group_name: str, 
                certificate_order_name: str, 
                name: str, 
                key_vault_certificate: AppServiceCertificatePatchResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AppServiceCertificateResource: ...

        @overload
        async def update_certificate(
                self, 
                resource_group_name: str, 
                certificate_order_name: str, 
                name: str, 
                key_vault_certificate: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AppServiceCertificateResource: ...

        @overload
        async def update_certificate(
                self, 
                resource_group_name: str, 
                certificate_order_name: str, 
                name: str, 
                key_vault_certificate: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AppServiceCertificateResource: ...

        @overload
        async def validate_purchase_information(
                self, 
                app_service_certificate_order: AppServiceCertificateOrder, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def validate_purchase_information(
                self, 
                app_service_certificate_order: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def validate_purchase_information(
                self, 
                app_service_certificate_order: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def verify_domain_ownership(
                self, 
                resource_group_name: str, 
                certificate_order_name: str, 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.certificateregistration.aio.operations.CertificateOrdersDiagnosticsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get_app_service_certificate_order_detector_response(
                self, 
                resource_group_name: str, 
                certificate_order_name: str, 
                detector_name: str, 
                *, 
                end_time: Optional[datetime] = ..., 
                start_time: Optional[datetime] = ..., 
                time_grain: Optional[str] = ..., 
                **kwargs: Any
            ) -> DetectorResponse: ...

        @distributed_trace
        def list_app_service_certificate_order_detector_response(
                self, 
                resource_group_name: str, 
                certificate_order_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[DetectorResponse]: ...


    class azure.mgmt.certificateregistration.aio.operations.CertificateRegistrationProviderOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_operations(self, **kwargs: Any) -> AsyncItemPaged[CsmOperationDescription]: ...


namespace azure.mgmt.certificateregistration.models

    class azure.mgmt.certificateregistration.models.AppServiceCertificate(_Model):
        key_vault_id: Optional[str]
        key_vault_secret_name: Optional[str]
        provisioning_state: Optional[Union[str, KeyVaultSecretStatus]]

        @overload
        def __init__(
                self, 
                *, 
                key_vault_id: Optional[str] = ..., 
                key_vault_secret_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.certificateregistration.models.AppServiceCertificateOrder(TrackedResource):
        id: str
        kind: Optional[str]
        location: str
        name: str
        properties: Optional[AppServiceCertificateOrderProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                kind: Optional[str] = ..., 
                location: str, 
                properties: Optional[AppServiceCertificateOrderProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.certificateregistration.models.AppServiceCertificateOrderPatchResource(ProxyOnlyResource):
        id: str
        kind: str
        name: str
        properties: Optional[AppServiceCertificateOrderPatchResourceProperties]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                kind: Optional[str] = ..., 
                properties: Optional[AppServiceCertificateOrderPatchResourceProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.certificateregistration.models.AppServiceCertificateOrderPatchResourceProperties(_Model):
        app_service_certificate_not_renewable_reasons: Optional[list[Union[str, ResourceNotRenewableReason]]]
        auto_renew: Optional[bool]
        certificates: Optional[dict[str, AppServiceCertificate]]
        contact: Optional[CertificateOrderContact]
        csr: Optional[str]
        distinguished_name: Optional[str]
        domain_verification_token: Optional[str]
        expiration_time: Optional[datetime]
        intermediate: Optional[CertificateDetails]
        is_private_key_external: Optional[bool]
        key_size: Optional[int]
        last_certificate_issuance_time: Optional[datetime]
        next_auto_renewal_time_stamp: Optional[datetime]
        product_type: Union[str, CertificateProductType]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        root: Optional[CertificateDetails]
        serial_number: Optional[str]
        signed_certificate: Optional[CertificateDetails]
        status: Optional[Union[str, CertificateOrderStatus]]
        validity_in_years: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                auto_renew: Optional[bool] = ..., 
                certificates: Optional[dict[str, AppServiceCertificate]] = ..., 
                csr: Optional[str] = ..., 
                distinguished_name: Optional[str] = ..., 
                key_size: Optional[int] = ..., 
                product_type: Union[str, CertificateProductType], 
                validity_in_years: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.certificateregistration.models.AppServiceCertificateOrderProperties(_Model):
        app_service_certificate_not_renewable_reasons: Optional[list[Union[str, ResourceNotRenewableReason]]]
        auto_renew: Optional[bool]
        certificates: Optional[dict[str, AppServiceCertificate]]
        contact: Optional[CertificateOrderContact]
        csr: Optional[str]
        distinguished_name: Optional[str]
        domain_verification_token: Optional[str]
        expiration_time: Optional[datetime]
        intermediate: Optional[CertificateDetails]
        is_private_key_external: Optional[bool]
        key_size: Optional[int]
        last_certificate_issuance_time: Optional[datetime]
        next_auto_renewal_time_stamp: Optional[datetime]
        product_type: Union[str, CertificateProductType]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        root: Optional[CertificateDetails]
        serial_number: Optional[str]
        signed_certificate: Optional[CertificateDetails]
        status: Optional[Union[str, CertificateOrderStatus]]
        validity_in_years: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                auto_renew: Optional[bool] = ..., 
                certificates: Optional[dict[str, AppServiceCertificate]] = ..., 
                csr: Optional[str] = ..., 
                distinguished_name: Optional[str] = ..., 
                key_size: Optional[int] = ..., 
                product_type: Union[str, CertificateProductType], 
                validity_in_years: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.certificateregistration.models.AppServiceCertificatePatchResource(ProxyOnlyResource):
        id: str
        kind: str
        name: str
        properties: Optional[AppServiceCertificate]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                kind: Optional[str] = ..., 
                properties: Optional[AppServiceCertificate] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.certificateregistration.models.AppServiceCertificateResource(TrackedResource):
        id: str
        kind: Optional[str]
        location: str
        name: str
        properties: Optional[AppServiceCertificate]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                kind: Optional[str] = ..., 
                location: str, 
                properties: Optional[AppServiceCertificate] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.certificateregistration.models.CertificateDetails(_Model):
        issuer: Optional[str]
        not_after: Optional[datetime]
        not_before: Optional[datetime]
        raw_data: Optional[str]
        serial_number: Optional[str]
        signature_algorithm: Optional[str]
        subject: Optional[str]
        thumbprint: Optional[str]
        version: Optional[int]


    class azure.mgmt.certificateregistration.models.CertificateEmail(_Model):
        email_id: Optional[str]
        time_stamp: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                email_id: Optional[str] = ..., 
                time_stamp: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.certificateregistration.models.CertificateOrderAction(_Model):
        action_type: Optional[Union[str, CertificateOrderActionType]]
        created_at: Optional[datetime]


    class azure.mgmt.certificateregistration.models.CertificateOrderActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CERTIFICATE_EXPIRATION_WARNING = "CertificateExpirationWarning"
        CERTIFICATE_EXPIRED = "CertificateExpired"
        CERTIFICATE_ISSUED = "CertificateIssued"
        CERTIFICATE_ORDER_CANCELED = "CertificateOrderCanceled"
        CERTIFICATE_ORDER_CREATED = "CertificateOrderCreated"
        CERTIFICATE_REVOKED = "CertificateRevoked"
        DOMAIN_VALIDATION_COMPLETE = "DomainValidationComplete"
        FRAUD_CLEARED = "FraudCleared"
        FRAUD_DETECTED = "FraudDetected"
        FRAUD_DOCUMENTATION_REQUIRED = "FraudDocumentationRequired"
        ORG_NAME_CHANGE = "OrgNameChange"
        ORG_VALIDATION_COMPLETE = "OrgValidationComplete"
        SAN_DROP = "SanDrop"
        UNKNOWN = "Unknown"


    class azure.mgmt.certificateregistration.models.CertificateOrderContact(_Model):
        email: Optional[str]
        name_first: Optional[str]
        name_last: Optional[str]
        phone: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                email: Optional[str] = ..., 
                name_first: Optional[str] = ..., 
                name_last: Optional[str] = ..., 
                phone: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.certificateregistration.models.CertificateOrderStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        DENIED = "Denied"
        EXPIRED = "Expired"
        ISSUED = "Issued"
        NOT_SUBMITTED = "NotSubmitted"
        PENDINGISSUANCE = "Pendingissuance"
        PENDINGREVOCATION = "Pendingrevocation"
        PENDING_REKEY = "PendingRekey"
        REVOKED = "Revoked"
        UNUSED = "Unused"


    class azure.mgmt.certificateregistration.models.CertificateProductType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        STANDARD_DOMAIN_VALIDATED_SSL = "StandardDomainValidatedSsl"
        STANDARD_DOMAIN_VALIDATED_WILD_CARD_SSL = "StandardDomainValidatedWildCardSsl"


    class azure.mgmt.certificateregistration.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.certificateregistration.models.CsmOperationDescription(_Model):
        display: Optional[CsmOperationDisplay]
        is_data_action: Optional[bool]
        name: Optional[str]
        origin: Optional[str]
        properties: Optional[CsmOperationDescriptionProperties]

        @overload
        def __init__(
                self, 
                *, 
                display: Optional[CsmOperationDisplay] = ..., 
                is_data_action: Optional[bool] = ..., 
                name: Optional[str] = ..., 
                origin: Optional[str] = ..., 
                properties: Optional[CsmOperationDescriptionProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.certificateregistration.models.CsmOperationDescriptionProperties(_Model):
        service_specification: Optional[ServiceSpecification]

        @overload
        def __init__(
                self, 
                *, 
                service_specification: Optional[ServiceSpecification] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.certificateregistration.models.CsmOperationDisplay(_Model):
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


    class azure.mgmt.certificateregistration.models.DataProviderMetadata(_Model):
        property_bag: Optional[list[KeyValuePairStringObject]]
        provider_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                provider_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.certificateregistration.models.DataTableResponseColumn(_Model):
        column_name: Optional[str]
        column_type: Optional[str]
        data_type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                column_name: Optional[str] = ..., 
                column_type: Optional[str] = ..., 
                data_type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.certificateregistration.models.DataTableResponseObject(_Model):
        columns: Optional[list[DataTableResponseColumn]]
        rows: Optional[list[list[str]]]
        table_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                columns: Optional[list[DataTableResponseColumn]] = ..., 
                rows: Optional[list[list[str]]] = ..., 
                table_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.certificateregistration.models.DefaultErrorResponse(_Model):
        error: Optional[DefaultErrorResponseError]


    class azure.mgmt.certificateregistration.models.DefaultErrorResponseError(_Model):
        code: Optional[str]
        details: Optional[list[DefaultErrorResponseErrorDetailsItem]]
        innererror: Optional[str]
        message: Optional[str]
        target: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                details: Optional[list[DefaultErrorResponseErrorDetailsItem]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.certificateregistration.models.DefaultErrorResponseErrorDetailsItem(_Model):
        code: Optional[str]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.certificateregistration.models.DetectorInfo(_Model):
        analysis_type: Optional[list[str]]
        author: Optional[str]
        category: Optional[str]
        description: Optional[str]
        id: Optional[str]
        name: Optional[str]
        score: Optional[float]
        support_topic_list: Optional[list[SupportTopic]]
        type: Optional[Union[str, DetectorType]]


    class azure.mgmt.certificateregistration.models.DetectorResponse(ProxyResource):
        id: str
        kind: Optional[str]
        name: str
        properties: Optional[DetectorResponseProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                kind: Optional[str] = ..., 
                properties: Optional[DetectorResponseProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.certificateregistration.models.DetectorResponseProperties(_Model):
        data_providers_metadata: Optional[list[DataProviderMetadata]]
        dataset: Optional[list[DiagnosticData]]
        metadata: Optional[DetectorInfo]
        status: Optional[Status]
        suggested_utterances: Optional[QueryUtterancesResults]

        @overload
        def __init__(
                self, 
                *, 
                data_providers_metadata: Optional[list[DataProviderMetadata]] = ..., 
                dataset: Optional[list[DiagnosticData]] = ..., 
                metadata: Optional[DetectorInfo] = ..., 
                status: Optional[Status] = ..., 
                suggested_utterances: Optional[QueryUtterancesResults] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.certificateregistration.models.DetectorType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ANALYSIS = "Analysis"
        CATEGORY_OVERVIEW = "CategoryOverview"
        DETECTOR = "Detector"


    class azure.mgmt.certificateregistration.models.DiagnosticData(_Model):
        rendering_properties: Optional[Rendering]
        table: Optional[DataTableResponseObject]

        @overload
        def __init__(
                self, 
                *, 
                rendering_properties: Optional[Rendering] = ..., 
                table: Optional[DataTableResponseObject] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.certificateregistration.models.Dimension(_Model):
        display_name: Optional[str]
        internal_name: Optional[str]
        name: Optional[str]
        to_be_exported_for_shoebox: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                display_name: Optional[str] = ..., 
                internal_name: Optional[str] = ..., 
                name: Optional[str] = ..., 
                to_be_exported_for_shoebox: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.certificateregistration.models.InsightStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CRITICAL = "Critical"
        INFO = "Info"
        NONE = "None"
        SUCCESS = "Success"
        WARNING = "Warning"


    class azure.mgmt.certificateregistration.models.KeyValuePairStringObject(_Model):
        key: Optional[str]
        value: Optional[dict[str, str]]


    class azure.mgmt.certificateregistration.models.KeyVaultSecretStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_SERVICE_UNAUTHORIZED_TO_ACCESS_KEY_VAULT = "AzureServiceUnauthorizedToAccessKeyVault"
        CERTIFICATE_ORDER_FAILED = "CertificateOrderFailed"
        EXTERNAL_PRIVATE_KEY = "ExternalPrivateKey"
        INITIALIZED = "Initialized"
        KEY_VAULT_DOES_NOT_EXIST = "KeyVaultDoesNotExist"
        KEY_VAULT_SECRET_DOES_NOT_EXIST = "KeyVaultSecretDoesNotExist"
        OPERATION_NOT_PERMITTED_ON_KEY_VAULT = "OperationNotPermittedOnKeyVault"
        SUCCEEDED = "Succeeded"
        UNKNOWN = "Unknown"
        UNKNOWN_ERROR = "UnknownError"
        WAITING_ON_CERTIFICATE_ORDER = "WaitingOnCertificateOrder"


    class azure.mgmt.certificateregistration.models.LogSpecification(_Model):
        blob_duration: Optional[str]
        display_name: Optional[str]
        log_filter_pattern: Optional[str]
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                blob_duration: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                log_filter_pattern: Optional[str] = ..., 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.certificateregistration.models.MetricAvailability(_Model):
        blob_duration: Optional[str]
        time_grain: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                blob_duration: Optional[str] = ..., 
                time_grain: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.certificateregistration.models.MetricSpecification(_Model):
        aggregation_type: Optional[str]
        availabilities: Optional[list[MetricAvailability]]
        category: Optional[str]
        dimensions: Optional[list[Dimension]]
        display_description: Optional[str]
        display_name: Optional[str]
        enable_regional_mdm_account: Optional[bool]
        fill_gap_with_zero: Optional[bool]
        is_internal: Optional[bool]
        metric_filter_pattern: Optional[str]
        name: Optional[str]
        source_mdm_account: Optional[str]
        source_mdm_namespace: Optional[str]
        supported_aggregation_types: Optional[list[str]]
        supported_time_grain_types: Optional[list[str]]
        supports_instance_level_aggregation: Optional[bool]
        unit: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                aggregation_type: Optional[str] = ..., 
                availabilities: Optional[list[MetricAvailability]] = ..., 
                category: Optional[str] = ..., 
                dimensions: Optional[list[Dimension]] = ..., 
                display_description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                enable_regional_mdm_account: Optional[bool] = ..., 
                fill_gap_with_zero: Optional[bool] = ..., 
                is_internal: Optional[bool] = ..., 
                metric_filter_pattern: Optional[str] = ..., 
                name: Optional[str] = ..., 
                source_mdm_account: Optional[str] = ..., 
                source_mdm_namespace: Optional[str] = ..., 
                supported_aggregation_types: Optional[list[str]] = ..., 
                supported_time_grain_types: Optional[list[str]] = ..., 
                supports_instance_level_aggregation: Optional[bool] = ..., 
                unit: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.certificateregistration.models.NameIdentifier(_Model):
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.certificateregistration.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        DELETING = "Deleting"
        FAILED = "Failed"
        IN_PROGRESS = "InProgress"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.certificateregistration.models.ProxyOnlyResource(_Model):
        id: Optional[str]
        kind: Optional[str]
        name: Optional[str]
        type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                kind: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.certificateregistration.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.certificateregistration.models.QueryUtterancesResult(_Model):
        sample_utterance: Optional[SampleUtterance]
        score: Optional[float]

        @overload
        def __init__(
                self, 
                *, 
                sample_utterance: Optional[SampleUtterance] = ..., 
                score: Optional[float] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.certificateregistration.models.QueryUtterancesResults(_Model):
        query: Optional[str]
        results: Optional[list[QueryUtterancesResult]]

        @overload
        def __init__(
                self, 
                *, 
                query: Optional[str] = ..., 
                results: Optional[list[QueryUtterancesResult]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.certificateregistration.models.ReissueCertificateOrderRequest(ProxyOnlyResource):
        id: str
        kind: str
        name: str
        properties: Optional[ReissueCertificateOrderRequestProperties]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                kind: Optional[str] = ..., 
                properties: Optional[ReissueCertificateOrderRequestProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.certificateregistration.models.ReissueCertificateOrderRequestProperties(_Model):
        csr: Optional[str]
        delay_existing_revoke_in_hours: Optional[int]
        is_private_key_external: Optional[bool]
        key_size: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                csr: Optional[str] = ..., 
                delay_existing_revoke_in_hours: Optional[int] = ..., 
                is_private_key_external: Optional[bool] = ..., 
                key_size: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.certificateregistration.models.Rendering(_Model):
        description: Optional[str]
        title: Optional[str]
        type: Optional[Union[str, RenderingType]]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                title: Optional[str] = ..., 
                type: Optional[Union[str, RenderingType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.certificateregistration.models.RenderingType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APP_INSIGHT = "AppInsight"
        APP_INSIGHT_ENABLEMENT = "AppInsightEnablement"
        CARD = "Card"
        CHANGES_VIEW = "ChangesView"
        CHANGE_ANALYSIS_ONBOARDING = "ChangeAnalysisOnboarding"
        CHANGE_SETS = "ChangeSets"
        DATA_SUMMARY = "DataSummary"
        DEPENDENCY_GRAPH = "DependencyGraph"
        DETECTOR = "Detector"
        DOWN_TIME = "DownTime"
        DROP_DOWN = "DropDown"
        DYNAMIC_INSIGHT = "DynamicInsight"
        EMAIL = "Email"
        FORM = "Form"
        GUAGE = "Guage"
        INSIGHTS = "Insights"
        MARKDOWN = "Markdown"
        NO_GRAPH = "NoGraph"
        PIE_CHART = "PieChart"
        SEARCH_COMPONENT = "SearchComponent"
        SOLUTION = "Solution"
        SUMMARY_CARD = "SummaryCard"
        TABLE = "Table"
        TIME_SERIES = "TimeSeries"
        TIME_SERIES_PER_INSTANCE = "TimeSeriesPerInstance"


    class azure.mgmt.certificateregistration.models.RenewCertificateOrderRequest(ProxyOnlyResource):
        id: str
        kind: str
        name: str
        properties: Optional[RenewCertificateOrderRequestProperties]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                kind: Optional[str] = ..., 
                properties: Optional[RenewCertificateOrderRequestProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.certificateregistration.models.RenewCertificateOrderRequestProperties(_Model):
        csr: Optional[str]
        is_private_key_external: Optional[bool]
        key_size: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                csr: Optional[str] = ..., 
                is_private_key_external: Optional[bool] = ..., 
                key_size: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.certificateregistration.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.certificateregistration.models.ResourceNotRenewableReason(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EXPIRATION_NOT_IN_RENEWAL_TIME_RANGE = "ExpirationNotInRenewalTimeRange"
        REGISTRATION_STATUS_NOT_SUPPORTED_FOR_RENEWAL = "RegistrationStatusNotSupportedForRenewal"
        SUBSCRIPTION_NOT_ACTIVE = "SubscriptionNotActive"


    class azure.mgmt.certificateregistration.models.SampleUtterance(_Model):
        links: Optional[list[str]]
        qid: Optional[str]
        text: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                links: Optional[list[str]] = ..., 
                qid: Optional[str] = ..., 
                text: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.certificateregistration.models.ServiceSpecification(_Model):
        log_specifications: Optional[list[LogSpecification]]
        metric_specifications: Optional[list[MetricSpecification]]

        @overload
        def __init__(
                self, 
                *, 
                log_specifications: Optional[list[LogSpecification]] = ..., 
                metric_specifications: Optional[list[MetricSpecification]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.certificateregistration.models.SiteSeal(_Model):
        html: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                html: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.certificateregistration.models.SiteSealRequest(_Model):
        light_theme: Optional[bool]
        locale: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                light_theme: Optional[bool] = ..., 
                locale: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.certificateregistration.models.Status(_Model):
        message: Optional[str]
        status_id: Optional[Union[str, InsightStatus]]

        @overload
        def __init__(
                self, 
                *, 
                message: Optional[str] = ..., 
                status_id: Optional[Union[str, InsightStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.certificateregistration.models.SupportTopic(_Model):
        id: Optional[str]
        pes_id: Optional[str]


    class azure.mgmt.certificateregistration.models.SystemData(_Model):
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


    class azure.mgmt.certificateregistration.models.TrackedResource(Resource):
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


namespace azure.mgmt.certificateregistration.operations

    class azure.mgmt.certificateregistration.operations.AppServiceCertificateOrdersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                certificate_order_name: str, 
                certificate_distinguished_name: AppServiceCertificateOrder, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AppServiceCertificateOrder]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                certificate_order_name: str, 
                certificate_distinguished_name: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AppServiceCertificateOrder]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                certificate_order_name: str, 
                certificate_distinguished_name: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AppServiceCertificateOrder]: ...

        @overload
        def begin_create_or_update_certificate(
                self, 
                resource_group_name: str, 
                certificate_order_name: str, 
                name: str, 
                key_vault_certificate: AppServiceCertificateResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AppServiceCertificateResource]: ...

        @overload
        def begin_create_or_update_certificate(
                self, 
                resource_group_name: str, 
                certificate_order_name: str, 
                name: str, 
                key_vault_certificate: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AppServiceCertificateResource]: ...

        @overload
        def begin_create_or_update_certificate(
                self, 
                resource_group_name: str, 
                certificate_order_name: str, 
                name: str, 
                key_vault_certificate: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AppServiceCertificateResource]: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                certificate_order_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def delete_certificate(
                self, 
                resource_group_name: str, 
                certificate_order_name: str, 
                name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                certificate_order_name: str, 
                **kwargs: Any
            ) -> AppServiceCertificateOrder: ...

        @distributed_trace
        def get_certificate(
                self, 
                resource_group_name: str, 
                certificate_order_name: str, 
                name: str, 
                **kwargs: Any
            ) -> AppServiceCertificateResource: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[AppServiceCertificateOrder]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[AppServiceCertificateOrder]: ...

        @distributed_trace
        def list_certificates(
                self, 
                resource_group_name: str, 
                certificate_order_name: str, 
                **kwargs: Any
            ) -> ItemPaged[AppServiceCertificateResource]: ...

        @overload
        def reissue(
                self, 
                resource_group_name: str, 
                certificate_order_name: str, 
                reissue_certificate_order_request: ReissueCertificateOrderRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def reissue(
                self, 
                resource_group_name: str, 
                certificate_order_name: str, 
                reissue_certificate_order_request: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def reissue(
                self, 
                resource_group_name: str, 
                certificate_order_name: str, 
                reissue_certificate_order_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def renew(
                self, 
                resource_group_name: str, 
                certificate_order_name: str, 
                renew_certificate_order_request: RenewCertificateOrderRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def renew(
                self, 
                resource_group_name: str, 
                certificate_order_name: str, 
                renew_certificate_order_request: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def renew(
                self, 
                resource_group_name: str, 
                certificate_order_name: str, 
                renew_certificate_order_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def resend_email(
                self, 
                resource_group_name: str, 
                certificate_order_name: str, 
                **kwargs: Any
            ) -> None: ...

        @overload
        def resend_request_emails(
                self, 
                resource_group_name: str, 
                certificate_order_name: str, 
                name_identifier: NameIdentifier, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def resend_request_emails(
                self, 
                resource_group_name: str, 
                certificate_order_name: str, 
                name_identifier: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def resend_request_emails(
                self, 
                resource_group_name: str, 
                certificate_order_name: str, 
                name_identifier: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def retrieve_certificate_actions(
                self, 
                resource_group_name: str, 
                name: str, 
                **kwargs: Any
            ) -> List[CertificateOrderAction]: ...

        @distributed_trace
        def retrieve_certificate_email_history(
                self, 
                resource_group_name: str, 
                name: str, 
                **kwargs: Any
            ) -> List[CertificateEmail]: ...

        @overload
        def retrieve_site_seal(
                self, 
                resource_group_name: str, 
                certificate_order_name: str, 
                site_seal_request: SiteSealRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SiteSeal: ...

        @overload
        def retrieve_site_seal(
                self, 
                resource_group_name: str, 
                certificate_order_name: str, 
                site_seal_request: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SiteSeal: ...

        @overload
        def retrieve_site_seal(
                self, 
                resource_group_name: str, 
                certificate_order_name: str, 
                site_seal_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SiteSeal: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                certificate_order_name: str, 
                certificate_distinguished_name: AppServiceCertificateOrderPatchResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AppServiceCertificateOrder: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                certificate_order_name: str, 
                certificate_distinguished_name: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AppServiceCertificateOrder: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                certificate_order_name: str, 
                certificate_distinguished_name: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AppServiceCertificateOrder: ...

        @overload
        def update_certificate(
                self, 
                resource_group_name: str, 
                certificate_order_name: str, 
                name: str, 
                key_vault_certificate: AppServiceCertificatePatchResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AppServiceCertificateResource: ...

        @overload
        def update_certificate(
                self, 
                resource_group_name: str, 
                certificate_order_name: str, 
                name: str, 
                key_vault_certificate: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AppServiceCertificateResource: ...

        @overload
        def update_certificate(
                self, 
                resource_group_name: str, 
                certificate_order_name: str, 
                name: str, 
                key_vault_certificate: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AppServiceCertificateResource: ...

        @overload
        def validate_purchase_information(
                self, 
                app_service_certificate_order: AppServiceCertificateOrder, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def validate_purchase_information(
                self, 
                app_service_certificate_order: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def validate_purchase_information(
                self, 
                app_service_certificate_order: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def verify_domain_ownership(
                self, 
                resource_group_name: str, 
                certificate_order_name: str, 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.certificateregistration.operations.CertificateOrdersDiagnosticsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get_app_service_certificate_order_detector_response(
                self, 
                resource_group_name: str, 
                certificate_order_name: str, 
                detector_name: str, 
                *, 
                end_time: Optional[datetime] = ..., 
                start_time: Optional[datetime] = ..., 
                time_grain: Optional[str] = ..., 
                **kwargs: Any
            ) -> DetectorResponse: ...

        @distributed_trace
        def list_app_service_certificate_order_detector_response(
                self, 
                resource_group_name: str, 
                certificate_order_name: str, 
                **kwargs: Any
            ) -> ItemPaged[DetectorResponse]: ...


    class azure.mgmt.certificateregistration.operations.CertificateRegistrationProviderOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_operations(self, **kwargs: Any) -> ItemPaged[CsmOperationDescription]: ...


```