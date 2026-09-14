```py
namespace azure.mgmt.billing

    class azure.mgmt.billing.BillingManagementClient: implements ContextManager 
        address: AddressOperations
        agreements: AgreementsOperations
        associated_tenants: AssociatedTenantsOperations
        available_balances: AvailableBalancesOperations
        billing_accounts: BillingAccountsOperations
        billing_permissions: BillingPermissionsOperations
        billing_profiles: BillingProfilesOperations
        billing_property: BillingPropertyOperations
        billing_requests: BillingRequestsOperations
        billing_role_assignments: BillingRoleAssignmentsOperations
        billing_role_definition: BillingRoleDefinitionOperations
        billing_subscriptions: BillingSubscriptionsOperations
        billing_subscriptions_aliases: BillingSubscriptionsAliasesOperations
        customers: CustomersOperations
        departments: DepartmentsOperations
        enrollment_accounts: EnrollmentAccountsOperations
        invoice_sections: InvoiceSectionsOperations
        invoices: InvoicesOperations
        operations: Operations
        partner_transfers: PartnerTransfersOperations
        payment_methods: PaymentMethodsOperations
        policies: PoliciesOperations
        products: ProductsOperations
        recipient_transfers: RecipientTransfersOperations
        reservation_orders: ReservationOrdersOperations
        reservations: ReservationsOperations
        savings_plan_orders: SavingsPlanOrdersOperations
        savings_plans: SavingsPlansOperations
        transactions: TransactionsOperations
        transfers: TransfersOperations

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


namespace azure.mgmt.billing.aio

    class azure.mgmt.billing.aio.BillingManagementClient: implements AsyncContextManager 
        address: AddressOperations
        agreements: AgreementsOperations
        associated_tenants: AssociatedTenantsOperations
        available_balances: AvailableBalancesOperations
        billing_accounts: BillingAccountsOperations
        billing_permissions: BillingPermissionsOperations
        billing_profiles: BillingProfilesOperations
        billing_property: BillingPropertyOperations
        billing_requests: BillingRequestsOperations
        billing_role_assignments: BillingRoleAssignmentsOperations
        billing_role_definition: BillingRoleDefinitionOperations
        billing_subscriptions: BillingSubscriptionsOperations
        billing_subscriptions_aliases: BillingSubscriptionsAliasesOperations
        customers: CustomersOperations
        departments: DepartmentsOperations
        enrollment_accounts: EnrollmentAccountsOperations
        invoice_sections: InvoiceSectionsOperations
        invoices: InvoicesOperations
        operations: Operations
        partner_transfers: PartnerTransfersOperations
        payment_methods: PaymentMethodsOperations
        policies: PoliciesOperations
        products: ProductsOperations
        recipient_transfers: RecipientTransfersOperations
        reservation_orders: ReservationOrdersOperations
        reservations: ReservationsOperations
        savings_plan_orders: SavingsPlanOrdersOperations
        savings_plans: SavingsPlansOperations
        transactions: TransactionsOperations
        transfers: TransfersOperations

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


namespace azure.mgmt.billing.aio.operations

    class azure.mgmt.billing.aio.operations.AddressOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def validate(
                self, 
                parameters: AddressDetails, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AddressValidationResponse: ...

        @overload
        async def validate(
                self, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AddressValidationResponse: ...

        @overload
        async def validate(
                self, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AddressValidationResponse: ...


    class azure.mgmt.billing.aio.operations.AgreementsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                billing_account_name: str, 
                agreement_name: str, 
                **kwargs: Any
            ) -> Agreement: ...

        @distributed_trace
        def list_by_billing_account(
                self, 
                billing_account_name: str, 
                *, 
                expand: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Agreement]: ...


    class azure.mgmt.billing.aio.operations.AssociatedTenantsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                billing_account_name: str, 
                associated_tenant_name: str, 
                parameters: AssociatedTenant, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AssociatedTenant]: ...

        @overload
        async def begin_create_or_update(
                self, 
                billing_account_name: str, 
                associated_tenant_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AssociatedTenant]: ...

        @overload
        async def begin_create_or_update(
                self, 
                billing_account_name: str, 
                associated_tenant_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AssociatedTenant]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                billing_account_name: str, 
                associated_tenant_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                billing_account_name: str, 
                associated_tenant_name: str, 
                **kwargs: Any
            ) -> AssociatedTenant: ...

        @distributed_trace
        def list_by_billing_account(
                self, 
                billing_account_name: str, 
                *, 
                count: Optional[bool] = ..., 
                filter: Optional[str] = ..., 
                include_revoked: bool = False, 
                order_by: Optional[str] = ..., 
                search: Optional[str] = ..., 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[AssociatedTenant]: ...


    class azure.mgmt.billing.aio.operations.AvailableBalancesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get_by_billing_account(
                self, 
                billing_account_name: str, 
                **kwargs: Any
            ) -> AvailableBalance: ...

        @distributed_trace_async
        async def get_by_billing_profile(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                **kwargs: Any
            ) -> AvailableBalance: ...


    class azure.mgmt.billing.aio.operations.BillingAccountsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_add_payment_terms(
                self, 
                billing_account_name: str, 
                parameters: List[PaymentTerm], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BillingAccount]: ...

        @overload
        async def begin_add_payment_terms(
                self, 
                billing_account_name: str, 
                parameters: List[JSON], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BillingAccount]: ...

        @overload
        async def begin_add_payment_terms(
                self, 
                billing_account_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BillingAccount]: ...

        @distributed_trace_async
        async def begin_cancel_payment_terms(
                self, 
                billing_account_name: str, 
                parameters: datetime, 
                **kwargs: Any
            ) -> AsyncLROPoller[BillingAccount]: ...

        @overload
        async def begin_update(
                self, 
                billing_account_name: str, 
                parameters: BillingAccountPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BillingAccount]: ...

        @overload
        async def begin_update(
                self, 
                billing_account_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BillingAccount]: ...

        @overload
        async def begin_update(
                self, 
                billing_account_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BillingAccount]: ...

        @distributed_trace_async
        async def confirm_transition(
                self, 
                billing_account_name: str, 
                **kwargs: Any
            ) -> TransitionDetails: ...

        @distributed_trace_async
        async def get(
                self, 
                billing_account_name: str, 
                **kwargs: Any
            ) -> BillingAccount: ...

        @distributed_trace
        def list(
                self, 
                *, 
                expand: Optional[str] = ..., 
                filter: Optional[str] = ..., 
                include_all: bool = False, 
                include_all_without_billing_profiles: bool = False, 
                include_deleted: bool = False, 
                include_pending_agreement: bool = False, 
                include_resellee: bool = False, 
                legal_owner_oid: Optional[str] = ..., 
                legal_owner_tid: Optional[str] = ..., 
                search: Optional[str] = ..., 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[BillingAccount]: ...

        @distributed_trace
        def list_invoice_sections_by_create_subscription_permission(
                self, 
                billing_account_name: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[InvoiceSectionWithCreateSubPermission]: ...

        @overload
        async def validate_payment_terms(
                self, 
                billing_account_name: str, 
                parameters: List[PaymentTerm], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PaymentTermsEligibilityResult: ...

        @overload
        async def validate_payment_terms(
                self, 
                billing_account_name: str, 
                parameters: List[JSON], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PaymentTermsEligibilityResult: ...

        @overload
        async def validate_payment_terms(
                self, 
                billing_account_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PaymentTermsEligibilityResult: ...


    class azure.mgmt.billing.aio.operations.BillingPermissionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def check_access_by_billing_account(
                self, 
                billing_account_name: str, 
                parameters: CheckAccessRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> List[CheckAccessResponse]: ...

        @overload
        async def check_access_by_billing_account(
                self, 
                billing_account_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> List[CheckAccessResponse]: ...

        @overload
        async def check_access_by_billing_account(
                self, 
                billing_account_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> List[CheckAccessResponse]: ...

        @overload
        async def check_access_by_billing_profile(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                parameters: CheckAccessRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> List[CheckAccessResponse]: ...

        @overload
        async def check_access_by_billing_profile(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> List[CheckAccessResponse]: ...

        @overload
        async def check_access_by_billing_profile(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> List[CheckAccessResponse]: ...

        @overload
        async def check_access_by_customer(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                customer_name: str, 
                parameters: CheckAccessRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> List[CheckAccessResponse]: ...

        @overload
        async def check_access_by_customer(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                customer_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> List[CheckAccessResponse]: ...

        @overload
        async def check_access_by_customer(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                customer_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> List[CheckAccessResponse]: ...

        @overload
        async def check_access_by_department(
                self, 
                billing_account_name: str, 
                department_name: str, 
                parameters: CheckAccessRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> List[CheckAccessResponse]: ...

        @overload
        async def check_access_by_department(
                self, 
                billing_account_name: str, 
                department_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> List[CheckAccessResponse]: ...

        @overload
        async def check_access_by_department(
                self, 
                billing_account_name: str, 
                department_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> List[CheckAccessResponse]: ...

        @overload
        async def check_access_by_enrollment_account(
                self, 
                billing_account_name: str, 
                enrollment_account_name: str, 
                parameters: CheckAccessRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> List[CheckAccessResponse]: ...

        @overload
        async def check_access_by_enrollment_account(
                self, 
                billing_account_name: str, 
                enrollment_account_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> List[CheckAccessResponse]: ...

        @overload
        async def check_access_by_enrollment_account(
                self, 
                billing_account_name: str, 
                enrollment_account_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> List[CheckAccessResponse]: ...

        @overload
        async def check_access_by_invoice_section(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                invoice_section_name: str, 
                parameters: CheckAccessRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> List[CheckAccessResponse]: ...

        @overload
        async def check_access_by_invoice_section(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                invoice_section_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> List[CheckAccessResponse]: ...

        @overload
        async def check_access_by_invoice_section(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                invoice_section_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> List[CheckAccessResponse]: ...

        @distributed_trace
        def list_by_billing_account(
                self, 
                billing_account_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[BillingPermission]: ...

        @distributed_trace
        def list_by_billing_profile(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[BillingPermission]: ...

        @distributed_trace
        def list_by_customer(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                customer_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[BillingPermission]: ...

        @distributed_trace
        def list_by_customer_at_billing_account(
                self, 
                billing_account_name: str, 
                customer_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[BillingPermission]: ...

        @distributed_trace
        def list_by_department(
                self, 
                billing_account_name: str, 
                department_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[BillingPermission]: ...

        @distributed_trace
        def list_by_enrollment_account(
                self, 
                billing_account_name: str, 
                enrollment_account_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[BillingPermission]: ...

        @distributed_trace
        def list_by_invoice_section(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                invoice_section_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[BillingPermission]: ...


    class azure.mgmt.billing.aio.operations.BillingProfilesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                parameters: BillingProfile, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BillingProfile]: ...

        @overload
        async def begin_create_or_update(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BillingProfile]: ...

        @overload
        async def begin_create_or_update(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BillingProfile]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                **kwargs: Any
            ) -> BillingProfile: ...

        @distributed_trace
        def list_by_billing_account(
                self, 
                billing_account_name: str, 
                *, 
                count: Optional[bool] = ..., 
                filter: Optional[str] = ..., 
                include_deleted: bool = False, 
                order_by: Optional[str] = ..., 
                search: Optional[str] = ..., 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[BillingProfile]: ...

        @distributed_trace_async
        async def validate_delete_eligibility(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                **kwargs: Any
            ) -> DeleteBillingProfileEligibilityResult: ...


    class azure.mgmt.billing.aio.operations.BillingPropertyOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                *, 
                include_billing_country: bool = False, 
                include_transition_status: bool = False, 
                **kwargs: Any
            ) -> BillingProperty: ...

        @overload
        async def update(
                self, 
                parameters: BillingProperty, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> BillingProperty: ...

        @overload
        async def update(
                self, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> BillingProperty: ...

        @overload
        async def update(
                self, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> BillingProperty: ...


    class azure.mgmt.billing.aio.operations.BillingRequestsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                billing_request_name: str, 
                parameters: BillingRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BillingRequest]: ...

        @overload
        async def begin_create_or_update(
                self, 
                billing_request_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BillingRequest]: ...

        @overload
        async def begin_create_or_update(
                self, 
                billing_request_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BillingRequest]: ...

        @distributed_trace_async
        async def get(
                self, 
                billing_request_name: str, 
                **kwargs: Any
            ) -> BillingRequest: ...

        @distributed_trace
        def list_by_billing_account(
                self, 
                billing_account_name: str, 
                *, 
                count: Optional[bool] = ..., 
                filter: Optional[str] = ..., 
                order_by: Optional[str] = ..., 
                search: Optional[str] = ..., 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[BillingRequest]: ...

        @distributed_trace
        def list_by_billing_profile(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                *, 
                count: Optional[bool] = ..., 
                filter: Optional[str] = ..., 
                order_by: Optional[str] = ..., 
                search: Optional[str] = ..., 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[BillingRequest]: ...

        @distributed_trace
        def list_by_customer(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                customer_name: str, 
                *, 
                count: Optional[bool] = ..., 
                filter: Optional[str] = ..., 
                order_by: Optional[str] = ..., 
                search: Optional[str] = ..., 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[BillingRequest]: ...

        @distributed_trace
        def list_by_invoice_section(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                invoice_section_name: str, 
                *, 
                count: Optional[bool] = ..., 
                filter: Optional[str] = ..., 
                order_by: Optional[str] = ..., 
                search: Optional[str] = ..., 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[BillingRequest]: ...

        @distributed_trace
        def list_by_user(
                self, 
                *, 
                count: Optional[bool] = ..., 
                filter: Optional[str] = ..., 
                order_by: Optional[str] = ..., 
                search: Optional[str] = ..., 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[BillingRequest]: ...


    class azure.mgmt.billing.aio.operations.BillingRoleAssignmentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_by_billing_account(
                self, 
                billing_account_name: str, 
                parameters: BillingRoleAssignmentProperties, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BillingRoleAssignment]: ...

        @overload
        async def begin_create_by_billing_account(
                self, 
                billing_account_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BillingRoleAssignment]: ...

        @overload
        async def begin_create_by_billing_account(
                self, 
                billing_account_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BillingRoleAssignment]: ...

        @overload
        async def begin_create_by_billing_profile(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                parameters: BillingRoleAssignmentProperties, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BillingRoleAssignment]: ...

        @overload
        async def begin_create_by_billing_profile(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BillingRoleAssignment]: ...

        @overload
        async def begin_create_by_billing_profile(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BillingRoleAssignment]: ...

        @overload
        async def begin_create_by_customer(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                customer_name: str, 
                parameters: BillingRoleAssignmentProperties, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BillingRoleAssignment]: ...

        @overload
        async def begin_create_by_customer(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                customer_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BillingRoleAssignment]: ...

        @overload
        async def begin_create_by_customer(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                customer_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BillingRoleAssignment]: ...

        @overload
        async def begin_create_by_invoice_section(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                invoice_section_name: str, 
                parameters: BillingRoleAssignmentProperties, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BillingRoleAssignment]: ...

        @overload
        async def begin_create_by_invoice_section(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                invoice_section_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BillingRoleAssignment]: ...

        @overload
        async def begin_create_by_invoice_section(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                invoice_section_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BillingRoleAssignment]: ...

        @overload
        async def begin_create_or_update_by_billing_account(
                self, 
                billing_account_name: str, 
                billing_role_assignment_name: str, 
                parameters: BillingRoleAssignment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BillingRoleAssignment]: ...

        @overload
        async def begin_create_or_update_by_billing_account(
                self, 
                billing_account_name: str, 
                billing_role_assignment_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BillingRoleAssignment]: ...

        @overload
        async def begin_create_or_update_by_billing_account(
                self, 
                billing_account_name: str, 
                billing_role_assignment_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BillingRoleAssignment]: ...

        @overload
        async def begin_create_or_update_by_department(
                self, 
                billing_account_name: str, 
                department_name: str, 
                billing_role_assignment_name: str, 
                parameters: BillingRoleAssignment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BillingRoleAssignment]: ...

        @overload
        async def begin_create_or_update_by_department(
                self, 
                billing_account_name: str, 
                department_name: str, 
                billing_role_assignment_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BillingRoleAssignment]: ...

        @overload
        async def begin_create_or_update_by_department(
                self, 
                billing_account_name: str, 
                department_name: str, 
                billing_role_assignment_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BillingRoleAssignment]: ...

        @overload
        async def begin_create_or_update_by_enrollment_account(
                self, 
                billing_account_name: str, 
                enrollment_account_name: str, 
                billing_role_assignment_name: str, 
                parameters: BillingRoleAssignment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BillingRoleAssignment]: ...

        @overload
        async def begin_create_or_update_by_enrollment_account(
                self, 
                billing_account_name: str, 
                enrollment_account_name: str, 
                billing_role_assignment_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BillingRoleAssignment]: ...

        @overload
        async def begin_create_or_update_by_enrollment_account(
                self, 
                billing_account_name: str, 
                enrollment_account_name: str, 
                billing_role_assignment_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BillingRoleAssignment]: ...

        @distributed_trace_async
        async def begin_resolve_by_billing_account(
                self, 
                billing_account_name: str, 
                *, 
                filter: Optional[str] = ..., 
                resolve_scope_display_names: bool = False, 
                **kwargs: Any
            ) -> AsyncLROPoller[BillingRoleAssignmentListResult]: ...

        @distributed_trace_async
        async def begin_resolve_by_billing_profile(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                *, 
                filter: Optional[str] = ..., 
                resolve_scope_display_names: bool = False, 
                **kwargs: Any
            ) -> AsyncLROPoller[BillingRoleAssignmentListResult]: ...

        @distributed_trace_async
        async def begin_resolve_by_customer(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                customer_name: str, 
                *, 
                filter: Optional[str] = ..., 
                resolve_scope_display_names: bool = False, 
                **kwargs: Any
            ) -> AsyncLROPoller[BillingRoleAssignmentListResult]: ...

        @distributed_trace_async
        async def begin_resolve_by_invoice_section(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                invoice_section_name: str, 
                *, 
                filter: Optional[str] = ..., 
                resolve_scope_display_names: bool = False, 
                **kwargs: Any
            ) -> AsyncLROPoller[BillingRoleAssignmentListResult]: ...

        @distributed_trace_async
        async def delete_by_billing_account(
                self, 
                billing_account_name: str, 
                billing_role_assignment_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def delete_by_billing_profile(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                billing_role_assignment_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def delete_by_customer(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                customer_name: str, 
                billing_role_assignment_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def delete_by_department(
                self, 
                billing_account_name: str, 
                department_name: str, 
                billing_role_assignment_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def delete_by_enrollment_account(
                self, 
                billing_account_name: str, 
                enrollment_account_name: str, 
                billing_role_assignment_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def delete_by_invoice_section(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                invoice_section_name: str, 
                billing_role_assignment_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get_by_billing_account(
                self, 
                billing_account_name: str, 
                billing_role_assignment_name: str, 
                **kwargs: Any
            ) -> BillingRoleAssignment: ...

        @distributed_trace_async
        async def get_by_billing_profile(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                billing_role_assignment_name: str, 
                **kwargs: Any
            ) -> BillingRoleAssignment: ...

        @distributed_trace_async
        async def get_by_customer(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                customer_name: str, 
                billing_role_assignment_name: str, 
                **kwargs: Any
            ) -> BillingRoleAssignment: ...

        @distributed_trace_async
        async def get_by_department(
                self, 
                billing_account_name: str, 
                department_name: str, 
                billing_role_assignment_name: str, 
                **kwargs: Any
            ) -> BillingRoleAssignment: ...

        @distributed_trace_async
        async def get_by_enrollment_account(
                self, 
                billing_account_name: str, 
                enrollment_account_name: str, 
                billing_role_assignment_name: str, 
                **kwargs: Any
            ) -> BillingRoleAssignment: ...

        @distributed_trace_async
        async def get_by_invoice_section(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                invoice_section_name: str, 
                billing_role_assignment_name: str, 
                **kwargs: Any
            ) -> BillingRoleAssignment: ...

        @distributed_trace
        def list_by_billing_account(
                self, 
                billing_account_name: str, 
                *, 
                filter: Optional[str] = ..., 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[BillingRoleAssignment]: ...

        @distributed_trace
        def list_by_billing_profile(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                *, 
                filter: Optional[str] = ..., 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[BillingRoleAssignment]: ...

        @distributed_trace
        def list_by_customer(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                customer_name: str, 
                *, 
                filter: Optional[str] = ..., 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[BillingRoleAssignment]: ...

        @distributed_trace
        def list_by_department(
                self, 
                billing_account_name: str, 
                department_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[BillingRoleAssignment]: ...

        @distributed_trace
        def list_by_enrollment_account(
                self, 
                billing_account_name: str, 
                enrollment_account_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[BillingRoleAssignment]: ...

        @distributed_trace
        def list_by_invoice_section(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                invoice_section_name: str, 
                *, 
                filter: Optional[str] = ..., 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[BillingRoleAssignment]: ...


    class azure.mgmt.billing.aio.operations.BillingRoleDefinitionOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get_by_billing_account(
                self, 
                billing_account_name: str, 
                role_definition_name: str, 
                **kwargs: Any
            ) -> BillingRoleDefinition: ...

        @distributed_trace_async
        async def get_by_billing_profile(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                role_definition_name: str, 
                **kwargs: Any
            ) -> BillingRoleDefinition: ...

        @distributed_trace_async
        async def get_by_customer(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                customer_name: str, 
                role_definition_name: str, 
                **kwargs: Any
            ) -> BillingRoleDefinition: ...

        @distributed_trace_async
        async def get_by_department(
                self, 
                billing_account_name: str, 
                department_name: str, 
                role_definition_name: str, 
                **kwargs: Any
            ) -> BillingRoleDefinition: ...

        @distributed_trace_async
        async def get_by_enrollment_account(
                self, 
                billing_account_name: str, 
                enrollment_account_name: str, 
                role_definition_name: str, 
                **kwargs: Any
            ) -> BillingRoleDefinition: ...

        @distributed_trace_async
        async def get_by_invoice_section(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                invoice_section_name: str, 
                role_definition_name: str, 
                **kwargs: Any
            ) -> BillingRoleDefinition: ...

        @distributed_trace
        def list_by_billing_account(
                self, 
                billing_account_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[BillingRoleDefinition]: ...

        @distributed_trace
        def list_by_billing_profile(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[BillingRoleDefinition]: ...

        @distributed_trace
        def list_by_customer(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                customer_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[BillingRoleDefinition]: ...

        @distributed_trace
        def list_by_department(
                self, 
                billing_account_name: str, 
                department_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[BillingRoleDefinition]: ...

        @distributed_trace
        def list_by_enrollment_account(
                self, 
                billing_account_name: str, 
                enrollment_account_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[BillingRoleDefinition]: ...

        @distributed_trace
        def list_by_invoice_section(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                invoice_section_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[BillingRoleDefinition]: ...


    class azure.mgmt.billing.aio.operations.BillingSubscriptionsAliasesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                billing_account_name: str, 
                alias_name: str, 
                parameters: BillingSubscriptionAlias, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BillingSubscriptionAlias]: ...

        @overload
        async def begin_create_or_update(
                self, 
                billing_account_name: str, 
                alias_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BillingSubscriptionAlias]: ...

        @overload
        async def begin_create_or_update(
                self, 
                billing_account_name: str, 
                alias_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BillingSubscriptionAlias]: ...

        @distributed_trace_async
        async def get(
                self, 
                billing_account_name: str, 
                alias_name: str, 
                **kwargs: Any
            ) -> BillingSubscriptionAlias: ...

        @distributed_trace
        def list_by_billing_account(
                self, 
                billing_account_name: str, 
                *, 
                count: Optional[bool] = ..., 
                filter: Optional[str] = ..., 
                include_deleted: bool = False, 
                order_by: Optional[str] = ..., 
                search: Optional[str] = ..., 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[BillingSubscriptionAlias]: ...


    class azure.mgmt.billing.aio.operations.BillingSubscriptionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_cancel(
                self, 
                billing_account_name: str, 
                billing_subscription_name: str, 
                parameters: CancelSubscriptionRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_cancel(
                self, 
                billing_account_name: str, 
                billing_subscription_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_cancel(
                self, 
                billing_account_name: str, 
                billing_subscription_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                billing_account_name: str, 
                billing_subscription_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_merge(
                self, 
                billing_account_name: str, 
                billing_subscription_name: str, 
                parameters: BillingSubscriptionMergeRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BillingSubscription]: ...

        @overload
        async def begin_merge(
                self, 
                billing_account_name: str, 
                billing_subscription_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BillingSubscription]: ...

        @overload
        async def begin_merge(
                self, 
                billing_account_name: str, 
                billing_subscription_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BillingSubscription]: ...

        @overload
        async def begin_move(
                self, 
                billing_account_name: str, 
                billing_subscription_name: str, 
                parameters: MoveBillingSubscriptionRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BillingSubscription]: ...

        @overload
        async def begin_move(
                self, 
                billing_account_name: str, 
                billing_subscription_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BillingSubscription]: ...

        @overload
        async def begin_move(
                self, 
                billing_account_name: str, 
                billing_subscription_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BillingSubscription]: ...

        @overload
        async def begin_split(
                self, 
                billing_account_name: str, 
                billing_subscription_name: str, 
                parameters: BillingSubscriptionSplitRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BillingSubscription]: ...

        @overload
        async def begin_split(
                self, 
                billing_account_name: str, 
                billing_subscription_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BillingSubscription]: ...

        @overload
        async def begin_split(
                self, 
                billing_account_name: str, 
                billing_subscription_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BillingSubscription]: ...

        @overload
        async def begin_update(
                self, 
                billing_account_name: str, 
                billing_subscription_name: str, 
                parameters: BillingSubscriptionPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BillingSubscription]: ...

        @overload
        async def begin_update(
                self, 
                billing_account_name: str, 
                billing_subscription_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BillingSubscription]: ...

        @overload
        async def begin_update(
                self, 
                billing_account_name: str, 
                billing_subscription_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BillingSubscription]: ...

        @distributed_trace_async
        async def get(
                self, 
                billing_account_name: str, 
                billing_subscription_name: str, 
                *, 
                expand: Optional[str] = ..., 
                **kwargs: Any
            ) -> BillingSubscription: ...

        @distributed_trace_async
        async def get_by_billing_profile(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                billing_subscription_name: str, 
                *, 
                expand: Optional[str] = ..., 
                **kwargs: Any
            ) -> BillingSubscription: ...

        @distributed_trace
        def list_by_billing_account(
                self, 
                billing_account_name: str, 
                *, 
                count: Optional[bool] = ..., 
                expand: Optional[str] = ..., 
                filter: Optional[str] = ..., 
                include_deleted: bool = False, 
                include_failed: bool = False, 
                include_tenant_subscriptions: bool = False, 
                order_by: Optional[str] = ..., 
                search: Optional[str] = ..., 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[BillingSubscription]: ...

        @distributed_trace
        def list_by_billing_profile(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                *, 
                count: Optional[bool] = ..., 
                expand: Optional[str] = ..., 
                filter: Optional[str] = ..., 
                include_deleted: bool = False, 
                order_by: Optional[str] = ..., 
                search: Optional[str] = ..., 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[BillingSubscription]: ...

        @distributed_trace
        def list_by_customer(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                customer_name: str, 
                *, 
                count: Optional[bool] = ..., 
                expand: Optional[str] = ..., 
                filter: Optional[str] = ..., 
                include_deleted: bool = False, 
                order_by: Optional[str] = ..., 
                search: Optional[str] = ..., 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[BillingSubscription]: ...

        @distributed_trace
        def list_by_customer_at_billing_account(
                self, 
                billing_account_name: str, 
                customer_name: str, 
                *, 
                count: Optional[bool] = ..., 
                expand: Optional[str] = ..., 
                filter: Optional[str] = ..., 
                include_deleted: bool = False, 
                order_by: Optional[str] = ..., 
                search: Optional[str] = ..., 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[BillingSubscription]: ...

        @distributed_trace
        def list_by_enrollment_account(
                self, 
                billing_account_name: str, 
                enrollment_account_name: str, 
                *, 
                count: Optional[bool] = ..., 
                filter: Optional[str] = ..., 
                order_by: Optional[str] = ..., 
                search: Optional[str] = ..., 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[BillingSubscription]: ...

        @distributed_trace
        def list_by_invoice_section(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                invoice_section_name: str, 
                *, 
                count: Optional[bool] = ..., 
                expand: Optional[str] = ..., 
                filter: Optional[str] = ..., 
                include_deleted: bool = False, 
                order_by: Optional[str] = ..., 
                search: Optional[str] = ..., 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[BillingSubscription]: ...

        @overload
        async def validate_move_eligibility(
                self, 
                billing_account_name: str, 
                billing_subscription_name: str, 
                parameters: MoveBillingSubscriptionRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MoveBillingSubscriptionEligibilityResult: ...

        @overload
        async def validate_move_eligibility(
                self, 
                billing_account_name: str, 
                billing_subscription_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MoveBillingSubscriptionEligibilityResult: ...

        @overload
        async def validate_move_eligibility(
                self, 
                billing_account_name: str, 
                billing_subscription_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MoveBillingSubscriptionEligibilityResult: ...


    class azure.mgmt.billing.aio.operations.CustomersOperations:

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
                customer_name: str, 
                **kwargs: Any
            ) -> Customer: ...

        @distributed_trace_async
        async def get_by_billing_account(
                self, 
                billing_account_name: str, 
                customer_name: str, 
                **kwargs: Any
            ) -> Customer: ...

        @distributed_trace
        def list_by_billing_account(
                self, 
                billing_account_name: str, 
                *, 
                count: Optional[bool] = ..., 
                expand: Optional[str] = ..., 
                filter: Optional[str] = ..., 
                order_by: Optional[str] = ..., 
                search: Optional[str] = ..., 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Customer]: ...

        @distributed_trace
        def list_by_billing_profile(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                *, 
                count: Optional[bool] = ..., 
                expand: Optional[str] = ..., 
                filter: Optional[str] = ..., 
                order_by: Optional[str] = ..., 
                search: Optional[str] = ..., 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Customer]: ...


    class azure.mgmt.billing.aio.operations.DepartmentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                billing_account_name: str, 
                department_name: str, 
                **kwargs: Any
            ) -> Department: ...

        @distributed_trace
        def list_by_billing_account(
                self, 
                billing_account_name: str, 
                *, 
                filter: Optional[str] = ..., 
                order_by: Optional[str] = ..., 
                search: Optional[str] = ..., 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Department]: ...


    class azure.mgmt.billing.aio.operations.EnrollmentAccountsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                billing_account_name: str, 
                enrollment_account_name: str, 
                **kwargs: Any
            ) -> EnrollmentAccount: ...

        @distributed_trace_async
        async def get_by_department(
                self, 
                billing_account_name: str, 
                department_name: str, 
                enrollment_account_name: str, 
                **kwargs: Any
            ) -> EnrollmentAccount: ...

        @distributed_trace
        def list_by_billing_account(
                self, 
                billing_account_name: str, 
                *, 
                count: Optional[bool] = ..., 
                filter: Optional[str] = ..., 
                order_by: Optional[str] = ..., 
                search: Optional[str] = ..., 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[EnrollmentAccount]: ...

        @distributed_trace
        def list_by_department(
                self, 
                billing_account_name: str, 
                department_name: str, 
                *, 
                count: Optional[bool] = ..., 
                filter: Optional[str] = ..., 
                order_by: Optional[str] = ..., 
                search: Optional[str] = ..., 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[EnrollmentAccount]: ...


    class azure.mgmt.billing.aio.operations.InvoiceSectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                invoice_section_name: str, 
                parameters: InvoiceSection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[InvoiceSection]: ...

        @overload
        async def begin_create_or_update(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                invoice_section_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[InvoiceSection]: ...

        @overload
        async def begin_create_or_update(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                invoice_section_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[InvoiceSection]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                invoice_section_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                invoice_section_name: str, 
                **kwargs: Any
            ) -> InvoiceSection: ...

        @distributed_trace
        def list_by_billing_profile(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                *, 
                count: Optional[bool] = ..., 
                filter: Optional[str] = ..., 
                include_deleted: bool = False, 
                order_by: Optional[str] = ..., 
                search: Optional[str] = ..., 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[InvoiceSection]: ...

        @distributed_trace_async
        async def validate_delete_eligibility(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                invoice_section_name: str, 
                **kwargs: Any
            ) -> DeleteInvoiceSectionEligibilityResult: ...


    class azure.mgmt.billing.aio.operations.InvoicesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_amend(
                self, 
                billing_account_name: str, 
                invoice_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_download_by_billing_account(
                self, 
                billing_account_name: str, 
                invoice_name: str, 
                *, 
                document_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[DocumentDownloadResult]: ...

        @distributed_trace_async
        async def begin_download_by_billing_subscription(
                self, 
                invoice_name: str, 
                *, 
                document_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[DocumentDownloadResult]: ...

        @overload
        async def begin_download_documents_by_billing_account(
                self, 
                billing_account_name: str, 
                parameters: List[DocumentDownloadRequest], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DocumentDownloadResult]: ...

        @overload
        async def begin_download_documents_by_billing_account(
                self, 
                billing_account_name: str, 
                parameters: List[JSON], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DocumentDownloadResult]: ...

        @overload
        async def begin_download_documents_by_billing_account(
                self, 
                billing_account_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DocumentDownloadResult]: ...

        @overload
        async def begin_download_documents_by_billing_subscription(
                self, 
                parameters: List[DocumentDownloadRequest], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DocumentDownloadResult]: ...

        @overload
        async def begin_download_documents_by_billing_subscription(
                self, 
                parameters: List[JSON], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DocumentDownloadResult]: ...

        @overload
        async def begin_download_documents_by_billing_subscription(
                self, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DocumentDownloadResult]: ...

        @distributed_trace_async
        async def begin_download_summary_by_billing_account(
                self, 
                billing_account_name: str, 
                invoice_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[DocumentDownloadResult]: ...

        @distributed_trace_async
        async def get(
                self, 
                invoice_name: str, 
                **kwargs: Any
            ) -> Invoice: ...

        @distributed_trace_async
        async def get_by_billing_account(
                self, 
                billing_account_name: str, 
                invoice_name: str, 
                **kwargs: Any
            ) -> Invoice: ...

        @distributed_trace_async
        async def get_by_billing_subscription(
                self, 
                invoice_name: str, 
                **kwargs: Any
            ) -> Invoice: ...

        @distributed_trace
        def list_by_billing_account(
                self, 
                billing_account_name: str, 
                *, 
                count: Optional[bool] = ..., 
                filter: Optional[str] = ..., 
                order_by: Optional[str] = ..., 
                period_end_date: Optional[date] = ..., 
                period_start_date: Optional[date] = ..., 
                search: Optional[str] = ..., 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Invoice]: ...

        @distributed_trace
        def list_by_billing_profile(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                *, 
                count: Optional[bool] = ..., 
                filter: Optional[str] = ..., 
                order_by: Optional[str] = ..., 
                period_end_date: Optional[date] = ..., 
                period_start_date: Optional[date] = ..., 
                search: Optional[str] = ..., 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Invoice]: ...

        @distributed_trace
        def list_by_billing_subscription(
                self, 
                *, 
                count: Optional[bool] = ..., 
                filter: Optional[str] = ..., 
                order_by: Optional[str] = ..., 
                period_end_date: Optional[date] = ..., 
                period_start_date: Optional[date] = ..., 
                search: Optional[str] = ..., 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Invoice]: ...


    class azure.mgmt.billing.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


    class azure.mgmt.billing.aio.operations.PartnerTransfersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def cancel(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                customer_name: str, 
                transfer_name: str, 
                **kwargs: Any
            ) -> PartnerTransferDetails: ...

        @distributed_trace_async
        async def get(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                customer_name: str, 
                transfer_name: str, 
                **kwargs: Any
            ) -> PartnerTransferDetails: ...

        @overload
        async def initiate(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                customer_name: str, 
                transfer_name: str, 
                parameters: PartnerInitiateTransferRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PartnerTransferDetails: ...

        @overload
        async def initiate(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                customer_name: str, 
                transfer_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PartnerTransferDetails: ...

        @overload
        async def initiate(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                customer_name: str, 
                transfer_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PartnerTransferDetails: ...

        @distributed_trace
        def list(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                customer_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[PartnerTransferDetails]: ...


    class azure.mgmt.billing.aio.operations.PaymentMethodsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def delete_by_user(
                self, 
                payment_method_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get_by_billing_account(
                self, 
                billing_account_name: str, 
                payment_method_name: str, 
                **kwargs: Any
            ) -> PaymentMethod: ...

        @distributed_trace_async
        async def get_by_billing_profile(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                payment_method_name: str, 
                **kwargs: Any
            ) -> PaymentMethodLink: ...

        @distributed_trace_async
        async def get_by_user(
                self, 
                payment_method_name: str, 
                **kwargs: Any
            ) -> PaymentMethod: ...

        @distributed_trace
        def list_by_billing_account(
                self, 
                billing_account_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[PaymentMethod]: ...

        @distributed_trace
        def list_by_billing_profile(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[PaymentMethodLink]: ...

        @distributed_trace
        def list_by_user(self, **kwargs: Any) -> AsyncItemPaged[PaymentMethod]: ...


    class azure.mgmt.billing.aio.operations.PoliciesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update_by_billing_account(
                self, 
                billing_account_name: str, 
                parameters: BillingAccountPolicy, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BillingAccountPolicy]: ...

        @overload
        async def begin_create_or_update_by_billing_account(
                self, 
                billing_account_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BillingAccountPolicy]: ...

        @overload
        async def begin_create_or_update_by_billing_account(
                self, 
                billing_account_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BillingAccountPolicy]: ...

        @overload
        async def begin_create_or_update_by_billing_profile(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                parameters: BillingProfilePolicy, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BillingProfilePolicy]: ...

        @overload
        async def begin_create_or_update_by_billing_profile(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BillingProfilePolicy]: ...

        @overload
        async def begin_create_or_update_by_billing_profile(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BillingProfilePolicy]: ...

        @overload
        async def begin_create_or_update_by_customer(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                customer_name: str, 
                parameters: CustomerPolicy, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CustomerPolicy]: ...

        @overload
        async def begin_create_or_update_by_customer(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                customer_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CustomerPolicy]: ...

        @overload
        async def begin_create_or_update_by_customer(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                customer_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CustomerPolicy]: ...

        @overload
        async def begin_create_or_update_by_customer_at_billing_account(
                self, 
                billing_account_name: str, 
                customer_name: str, 
                parameters: CustomerPolicy, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CustomerPolicy]: ...

        @overload
        async def begin_create_or_update_by_customer_at_billing_account(
                self, 
                billing_account_name: str, 
                customer_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CustomerPolicy]: ...

        @overload
        async def begin_create_or_update_by_customer_at_billing_account(
                self, 
                billing_account_name: str, 
                customer_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CustomerPolicy]: ...

        @distributed_trace_async
        async def get_by_billing_account(
                self, 
                billing_account_name: str, 
                **kwargs: Any
            ) -> BillingAccountPolicy: ...

        @distributed_trace_async
        async def get_by_billing_profile(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                **kwargs: Any
            ) -> BillingProfilePolicy: ...

        @distributed_trace_async
        async def get_by_customer(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                customer_name: str, 
                policy_name: Union[str, ServiceDefinedResourceName], 
                **kwargs: Any
            ) -> CustomerPolicy: ...

        @distributed_trace_async
        async def get_by_customer_at_billing_account(
                self, 
                billing_account_name: str, 
                customer_name: str, 
                **kwargs: Any
            ) -> CustomerPolicy: ...

        @distributed_trace_async
        async def get_by_subscription(self, **kwargs: Any) -> SubscriptionPolicy: ...


    class azure.mgmt.billing.aio.operations.ProductsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_move(
                self, 
                billing_account_name: str, 
                product_name: str, 
                parameters: MoveProductRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Product]: ...

        @overload
        async def begin_move(
                self, 
                billing_account_name: str, 
                product_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Product]: ...

        @overload
        async def begin_move(
                self, 
                billing_account_name: str, 
                product_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Product]: ...

        @distributed_trace_async
        async def get(
                self, 
                billing_account_name: str, 
                product_name: str, 
                **kwargs: Any
            ) -> Product: ...

        @distributed_trace
        def list_by_billing_account(
                self, 
                billing_account_name: str, 
                *, 
                count: Optional[bool] = ..., 
                filter: Optional[str] = ..., 
                order_by: Optional[str] = ..., 
                search: Optional[str] = ..., 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Product]: ...

        @distributed_trace
        def list_by_billing_profile(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                *, 
                count: Optional[bool] = ..., 
                filter: Optional[str] = ..., 
                order_by: Optional[str] = ..., 
                search: Optional[str] = ..., 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Product]: ...

        @distributed_trace
        def list_by_customer(
                self, 
                billing_account_name: str, 
                customer_name: str, 
                *, 
                count: Optional[bool] = ..., 
                filter: Optional[str] = ..., 
                order_by: Optional[str] = ..., 
                search: Optional[str] = ..., 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Product]: ...

        @distributed_trace
        def list_by_invoice_section(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                invoice_section_name: str, 
                *, 
                count: Optional[bool] = ..., 
                filter: Optional[str] = ..., 
                order_by: Optional[str] = ..., 
                search: Optional[str] = ..., 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Product]: ...

        @overload
        async def update(
                self, 
                billing_account_name: str, 
                product_name: str, 
                parameters: ProductPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Product: ...

        @overload
        async def update(
                self, 
                billing_account_name: str, 
                product_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Product: ...

        @overload
        async def update(
                self, 
                billing_account_name: str, 
                product_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Product: ...

        @overload
        async def validate_move_eligibility(
                self, 
                billing_account_name: str, 
                product_name: str, 
                parameters: MoveProductRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MoveProductEligibilityResult: ...

        @overload
        async def validate_move_eligibility(
                self, 
                billing_account_name: str, 
                product_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MoveProductEligibilityResult: ...

        @overload
        async def validate_move_eligibility(
                self, 
                billing_account_name: str, 
                product_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MoveProductEligibilityResult: ...


    class azure.mgmt.billing.aio.operations.RecipientTransfersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def accept(
                self, 
                transfer_name: str, 
                parameters: AcceptTransferRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RecipientTransferDetails: ...

        @overload
        async def accept(
                self, 
                transfer_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RecipientTransferDetails: ...

        @overload
        async def accept(
                self, 
                transfer_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RecipientTransferDetails: ...

        @distributed_trace_async
        async def decline(
                self, 
                transfer_name: str, 
                **kwargs: Any
            ) -> RecipientTransferDetails: ...

        @distributed_trace_async
        async def get(
                self, 
                transfer_name: str, 
                **kwargs: Any
            ) -> RecipientTransferDetails: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[RecipientTransferDetails]: ...

        @overload
        async def validate(
                self, 
                transfer_name: str, 
                parameters: AcceptTransferRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ValidateTransferListResponse: ...

        @overload
        async def validate(
                self, 
                transfer_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ValidateTransferListResponse: ...

        @overload
        async def validate(
                self, 
                transfer_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ValidateTransferListResponse: ...


    class azure.mgmt.billing.aio.operations.ReservationOrdersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get_by_billing_account(
                self, 
                billing_account_name: str, 
                reservation_order_id: str, 
                *, 
                expand: Optional[str] = ..., 
                **kwargs: Any
            ) -> ReservationOrder: ...

        @distributed_trace
        def list_by_billing_account(
                self, 
                billing_account_name: str, 
                *, 
                filter: Optional[str] = ..., 
                order_by: Optional[str] = ..., 
                skiptoken: Optional[float] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[ReservationOrder]: ...


    class azure.mgmt.billing.aio.operations.ReservationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_update_by_billing_account(
                self, 
                billing_account_name: str, 
                reservation_order_id: str, 
                reservation_id: str, 
                body: Patch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Reservation]: ...

        @overload
        async def begin_update_by_billing_account(
                self, 
                billing_account_name: str, 
                reservation_order_id: str, 
                reservation_id: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Reservation]: ...

        @overload
        async def begin_update_by_billing_account(
                self, 
                billing_account_name: str, 
                reservation_order_id: str, 
                reservation_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Reservation]: ...

        @distributed_trace_async
        async def get_by_reservation_order(
                self, 
                billing_account_name: str, 
                reservation_order_id: str, 
                reservation_id: str, 
                *, 
                expand: Optional[str] = ..., 
                **kwargs: Any
            ) -> Reservation: ...

        @distributed_trace
        def list_by_billing_account(
                self, 
                billing_account_name: str, 
                *, 
                filter: Optional[str] = ..., 
                order_by: Optional[str] = ..., 
                refresh_summary: Optional[str] = ..., 
                selected_state: Optional[str] = ..., 
                skiptoken: Optional[float] = ..., 
                take: Optional[float] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Reservation]: ...

        @distributed_trace
        def list_by_billing_profile(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                *, 
                filter: Optional[str] = ..., 
                order_by: Optional[str] = ..., 
                refresh_summary: Optional[str] = ..., 
                selected_state: Optional[str] = ..., 
                skiptoken: Optional[float] = ..., 
                take: Optional[float] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Reservation]: ...

        @distributed_trace
        def list_by_reservation_order(
                self, 
                billing_account_name: str, 
                reservation_order_id: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Reservation]: ...


    class azure.mgmt.billing.aio.operations.SavingsPlanOrdersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get_by_billing_account(
                self, 
                billing_account_name: str, 
                savings_plan_order_id: str, 
                *, 
                expand: Optional[str] = ..., 
                **kwargs: Any
            ) -> SavingsPlanOrderModel: ...

        @distributed_trace
        def list_by_billing_account(
                self, 
                billing_account_name: str, 
                *, 
                filter: Optional[str] = ..., 
                order_by: Optional[str] = ..., 
                skiptoken: Optional[float] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[SavingsPlanOrderModel]: ...


    class azure.mgmt.billing.aio.operations.SavingsPlansOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_update_by_billing_account(
                self, 
                billing_account_name: str, 
                savings_plan_order_id: str, 
                savings_plan_id: str, 
                body: SavingsPlanUpdateRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SavingsPlanModel]: ...

        @overload
        async def begin_update_by_billing_account(
                self, 
                billing_account_name: str, 
                savings_plan_order_id: str, 
                savings_plan_id: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SavingsPlanModel]: ...

        @overload
        async def begin_update_by_billing_account(
                self, 
                billing_account_name: str, 
                savings_plan_order_id: str, 
                savings_plan_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SavingsPlanModel]: ...

        @distributed_trace_async
        async def get_by_billing_account(
                self, 
                billing_account_name: str, 
                savings_plan_order_id: str, 
                savings_plan_id: str, 
                *, 
                expand: Optional[str] = ..., 
                **kwargs: Any
            ) -> SavingsPlanModel: ...

        @distributed_trace
        def list_by_billing_account(
                self, 
                billing_account_name: str, 
                *, 
                filter: Optional[str] = ..., 
                order_by: Optional[str] = ..., 
                refresh_summary: Optional[str] = ..., 
                selected_state: Optional[str] = ..., 
                skiptoken: Optional[float] = ..., 
                take: Optional[float] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[SavingsPlanModel]: ...

        @distributed_trace
        def list_by_savings_plan_order(
                self, 
                billing_account_name: str, 
                savings_plan_order_id: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[SavingsPlanModel]: ...

        @overload
        async def validate_update_by_billing_account(
                self, 
                billing_account_name: str, 
                savings_plan_order_id: str, 
                savings_plan_id: str, 
                body: SavingsPlanUpdateValidateRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SavingsPlanValidateResponse: ...

        @overload
        async def validate_update_by_billing_account(
                self, 
                billing_account_name: str, 
                savings_plan_order_id: str, 
                savings_plan_id: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SavingsPlanValidateResponse: ...

        @overload
        async def validate_update_by_billing_account(
                self, 
                billing_account_name: str, 
                savings_plan_order_id: str, 
                savings_plan_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SavingsPlanValidateResponse: ...


    class azure.mgmt.billing.aio.operations.TransactionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_transactions_download_by_invoice(
                self, 
                billing_account_name: str, 
                invoice_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[DocumentDownloadResult]: ...

        @distributed_trace_async
        async def get_transaction_summary_by_invoice(
                self, 
                billing_account_name: str, 
                invoice_name: str, 
                *, 
                filter: Optional[str] = ..., 
                search: Optional[str] = ..., 
                **kwargs: Any
            ) -> TransactionSummary: ...

        @distributed_trace
        def list_by_billing_profile(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                *, 
                count: Optional[bool] = ..., 
                filter: Optional[str] = ..., 
                order_by: Optional[str] = ..., 
                period_end_date: date, 
                period_start_date: date, 
                search: Optional[str] = ..., 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                type: Union[str, TransactionType], 
                **kwargs: Any
            ) -> AsyncItemPaged[Transaction]: ...

        @distributed_trace
        def list_by_customer(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                customer_name: str, 
                *, 
                count: Optional[bool] = ..., 
                filter: Optional[str] = ..., 
                order_by: Optional[str] = ..., 
                period_end_date: date, 
                period_start_date: date, 
                search: Optional[str] = ..., 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                type: Union[str, TransactionType], 
                **kwargs: Any
            ) -> AsyncItemPaged[Transaction]: ...

        @distributed_trace
        def list_by_invoice(
                self, 
                billing_account_name: str, 
                invoice_name: str, 
                *, 
                count: Optional[bool] = ..., 
                filter: Optional[str] = ..., 
                order_by: Optional[str] = ..., 
                search: Optional[str] = ..., 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Transaction]: ...

        @distributed_trace
        def list_by_invoice_section(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                invoice_section_name: str, 
                *, 
                count: Optional[bool] = ..., 
                filter: Optional[str] = ..., 
                order_by: Optional[str] = ..., 
                period_end_date: date, 
                period_start_date: date, 
                search: Optional[str] = ..., 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                type: Union[str, TransactionType], 
                **kwargs: Any
            ) -> AsyncItemPaged[Transaction]: ...


    class azure.mgmt.billing.aio.operations.TransfersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def cancel(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                invoice_section_name: str, 
                transfer_name: str, 
                **kwargs: Any
            ) -> TransferDetails: ...

        @distributed_trace_async
        async def get(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                invoice_section_name: str, 
                transfer_name: str, 
                **kwargs: Any
            ) -> TransferDetails: ...

        @overload
        async def initiate(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                invoice_section_name: str, 
                transfer_name: str, 
                parameters: InitiateTransferRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TransferDetails: ...

        @overload
        async def initiate(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                invoice_section_name: str, 
                transfer_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TransferDetails: ...

        @overload
        async def initiate(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                invoice_section_name: str, 
                transfer_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TransferDetails: ...

        @distributed_trace
        def list(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                invoice_section_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[TransferDetails]: ...


namespace azure.mgmt.billing.models

    class azure.mgmt.billing.models.AcceptTransferProperties(_Model):
        product_details: Optional[list[ProductDetails]]

        @overload
        def __init__(
                self, 
                *, 
                product_details: Optional[list[ProductDetails]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.AcceptTransferRequest(_Model):
        properties: Optional[AcceptTransferProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[AcceptTransferProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.billing.models.AcceptanceMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CLICK_TO_ACCEPT = "ClickToAccept"
        E_SIGN_EMBEDDED = "ESignEmbedded"
        E_SIGN_OFFLINE = "ESignOffline"
        IMPLICIT = "Implicit"
        OFFLINE = "Offline"
        OTHER = "Other"
        PHYSICAL_SIGN = "PhysicalSign"


    class azure.mgmt.billing.models.AccessDecision(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALLOWED = "Allowed"
        NOT_ALLOWED = "NotAllowed"
        OTHER = "Other"


    class azure.mgmt.billing.models.AccountStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        DELETED = "Deleted"
        DISABLED = "Disabled"
        EXPIRED = "Expired"
        EXTENDED = "Extended"
        NEW = "New"
        OTHER = "Other"
        PENDING = "Pending"
        TERMINATED = "Terminated"
        TRANSFERRED = "Transferred"
        UNDER_REVIEW = "UnderReview"


    class azure.mgmt.billing.models.AccountSubType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ENTERPRISE = "Enterprise"
        INDIVIDUAL = "Individual"
        NONE = "None"
        OTHER = "Other"
        PROFESSIONAL = "Professional"


    class azure.mgmt.billing.models.AccountType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BUSINESS = "Business"
        CLASSIC_PARTNER = "ClassicPartner"
        ENTERPRISE = "Enterprise"
        INDIVIDUAL = "Individual"
        INTERNAL = "Internal"
        OTHER = "Other"
        PARTNER = "Partner"
        RESELLER = "Reseller"
        TENANT = "Tenant"


    class azure.mgmt.billing.models.AddressDetails(_Model):
        address_line1: str
        address_line2: Optional[str]
        address_line3: Optional[str]
        city: Optional[str]
        company_name: Optional[str]
        country: str
        district: Optional[str]
        email: Optional[str]
        first_name: Optional[str]
        is_valid_address: Optional[bool]
        last_name: Optional[str]
        middle_name: Optional[str]
        phone_number: Optional[str]
        postal_code: Optional[str]
        region: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                address_line1: str, 
                address_line2: Optional[str] = ..., 
                address_line3: Optional[str] = ..., 
                city: Optional[str] = ..., 
                company_name: Optional[str] = ..., 
                country: str, 
                district: Optional[str] = ..., 
                email: Optional[str] = ..., 
                first_name: Optional[str] = ..., 
                is_valid_address: Optional[bool] = ..., 
                last_name: Optional[str] = ..., 
                middle_name: Optional[str] = ..., 
                phone_number: Optional[str] = ..., 
                postal_code: Optional[str] = ..., 
                region: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.AddressValidationResponse(_Model):
        status: Optional[Union[str, AddressValidationStatus]]
        suggested_addresses: Optional[list[AddressDetails]]
        validation_message: Optional[str]


    class azure.mgmt.billing.models.AddressValidationStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INVALID = "Invalid"
        OTHER = "Other"
        VALID = "Valid"


    class azure.mgmt.billing.models.Agreement(ProxyResource):
        id: str
        name: str
        properties: Optional[AgreementProperties]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[AgreementProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.AgreementProperties(_Model):
        acceptance_mode: Optional[Union[str, AcceptanceMode]]
        agreement_link: Optional[str]
        billing_profile_info: Optional[list[BillingProfileInfo]]
        category: Optional[Union[str, Category]]
        display_name: Optional[str]
        effective_date: Optional[datetime]
        expiration_date: Optional[datetime]
        lead_billing_account_name: Optional[str]
        participants: Optional[list[Participant]]
        status: Optional[str]


    class azure.mgmt.billing.models.AgreementType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ENTERPRISE_AGREEMENT = "EnterpriseAgreement"
        MICROSOFT_CUSTOMER_AGREEMENT = "MicrosoftCustomerAgreement"
        MICROSOFT_ONLINE_SERVICES_PROGRAM = "MicrosoftOnlineServicesProgram"
        MICROSOFT_PARTNER_AGREEMENT = "MicrosoftPartnerAgreement"
        OTHER = "Other"


    class azure.mgmt.billing.models.Amount(_Model):
        currency: Optional[str]
        value: Optional[float]


    class azure.mgmt.billing.models.AppliedScopeProperties(_Model):
        display_name: Optional[str]
        management_group_id: Optional[str]
        resource_group_id: Optional[str]
        subscription_id: Optional[str]
        tenant_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                display_name: Optional[str] = ..., 
                management_group_id: Optional[str] = ..., 
                resource_group_id: Optional[str] = ..., 
                subscription_id: Optional[str] = ..., 
                tenant_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.AppliedScopeType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MANAGEMENT_GROUP = "ManagementGroup"
        SHARED = "Shared"
        SINGLE = "Single"


    class azure.mgmt.billing.models.AssociatedTenant(ProxyResource):
        id: str
        name: str
        properties: Optional[AssociatedTenantProperties]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[AssociatedTenantProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.AssociatedTenantProperties(_Model):
        billing_management_state: Optional[Union[str, BillingManagementTenantState]]
        display_name: Optional[str]
        provisioning_billing_request_id: Optional[str]
        provisioning_management_state: Optional[Union[str, ProvisioningTenantState]]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        tenant_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                billing_management_state: Optional[Union[str, BillingManagementTenantState]] = ..., 
                display_name: Optional[str] = ..., 
                provisioning_management_state: Optional[Union[str, ProvisioningTenantState]] = ..., 
                tenant_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.AutoRenew(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        OFF = "Off"
        ON = "On"


    class azure.mgmt.billing.models.AvailableBalance(ProxyResource):
        id: str
        name: str
        properties: Optional[AvailableBalanceProperties]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[AvailableBalanceProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.AvailableBalanceProperties(_Model):
        amount: Optional[AvailableBalancePropertiesAmount]
        payments_on_account: Optional[list[PaymentOnAccount]]
        total_payments_on_account: Optional[AvailableBalancePropertiesTotalPaymentsOnAccount]

        @overload
        def __init__(
                self, 
                *, 
                amount: Optional[AvailableBalancePropertiesAmount] = ..., 
                total_payments_on_account: Optional[AvailableBalancePropertiesTotalPaymentsOnAccount] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.AvailableBalancePropertiesAmount(Amount):
        currency: str
        value: float


    class azure.mgmt.billing.models.AvailableBalancePropertiesTotalPaymentsOnAccount(Amount):
        currency: str
        value: float


    class azure.mgmt.billing.models.AzurePlan(_Model):
        product_id: Optional[str]
        sku_description: Optional[str]
        sku_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                product_id: Optional[str] = ..., 
                sku_description: Optional[str] = ..., 
                sku_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.Beneficiary(_Model):
        object_id: Optional[str]
        tenant_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                object_id: Optional[str] = ..., 
                tenant_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.BillingAccount(ProxyResource):
        id: str
        name: str
        properties: Optional[BillingAccountProperties]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[BillingAccountProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.BillingAccountPatch(ProxyResourceWithTags):
        id: str
        name: str
        properties: Optional[BillingAccountProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[BillingAccountProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.BillingAccountPolicy(ProxyResource):
        id: str
        name: str
        properties: Optional[BillingAccountPolicyProperties]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[BillingAccountPolicyProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.BillingAccountPolicyProperties(_Model):
        enterprise_agreement_policies: Optional[BillingAccountPolicyPropertiesEnterpriseAgreementPolicies]
        marketplace_purchases: Optional[Union[str, MarketplacePurchasesPolicy]]
        policies: Optional[list[PolicySummary]]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        reservation_purchases: Optional[Union[str, ReservationPurchasesPolicy]]
        savings_plan_purchases: Optional[Union[str, SavingsPlanPurchasesPolicy]]

        @overload
        def __init__(
                self, 
                *, 
                enterprise_agreement_policies: Optional[BillingAccountPolicyPropertiesEnterpriseAgreementPolicies] = ..., 
                marketplace_purchases: Optional[Union[str, MarketplacePurchasesPolicy]] = ..., 
                policies: Optional[list[PolicySummary]] = ..., 
                reservation_purchases: Optional[Union[str, ReservationPurchasesPolicy]] = ..., 
                savings_plan_purchases: Optional[Union[str, SavingsPlanPurchasesPolicy]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.BillingAccountPolicyPropertiesEnterpriseAgreementPolicies(EnterpriseAgreementPolicies):
        account_owner_view_charges: Union[str, EnrollmentAccountOwnerViewCharges]
        authentication_type: Union[str, EnrollmentAuthLevelState]
        department_admin_view_charges: Union[str, EnrollmentDepartmentAdminViewCharges]

        @overload
        def __init__(
                self, 
                *, 
                account_owner_view_charges: Optional[Union[str, EnrollmentAccountOwnerViewCharges]] = ..., 
                authentication_type: Optional[Union[str, EnrollmentAuthLevelState]] = ..., 
                department_admin_view_charges: Optional[Union[str, EnrollmentDepartmentAdminViewCharges]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.BillingAccountProperties(_Model):
        account_status: Optional[Union[str, AccountStatus]]
        account_status_reason_code: Optional[Union[str, BillingAccountStatusReasonCode]]
        account_sub_type: Optional[Union[str, AccountSubType]]
        account_type: Optional[Union[str, AccountType]]
        agreement_type: Optional[Union[str, AgreementType]]
        billing_relationship_types: Optional[list[Union[str, BillingRelationshipType]]]
        display_name: Optional[str]
        enrollment_details: Optional[BillingAccountPropertiesEnrollmentDetails]
        has_no_billing_profiles: Optional[bool]
        has_read_access: Optional[bool]
        notification_email_address: Optional[str]
        primary_billing_tenant_id: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        qualifications: Optional[list[str]]
        registration_number: Optional[BillingAccountPropertiesRegistrationNumber]
        sold_to: Optional[BillingAccountPropertiesSoldTo]
        tax_ids: Optional[list[TaxIdentifier]]

        @overload
        def __init__(
                self, 
                *, 
                display_name: Optional[str] = ..., 
                enrollment_details: Optional[BillingAccountPropertiesEnrollmentDetails] = ..., 
                has_no_billing_profiles: Optional[bool] = ..., 
                has_read_access: Optional[bool] = ..., 
                notification_email_address: Optional[str] = ..., 
                primary_billing_tenant_id: Optional[str] = ..., 
                registration_number: Optional[BillingAccountPropertiesRegistrationNumber] = ..., 
                sold_to: Optional[BillingAccountPropertiesSoldTo] = ..., 
                tax_ids: Optional[list[TaxIdentifier]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.BillingAccountPropertiesEnrollmentDetails(EnrollmentDetails):
        billing_cycle: str
        channel: str
        cloud: str
        country_code: str
        currency: str
        end_date: datetime
        extended_term_option: Union[str, ExtendedTermOption]
        indirect_relationship_info: EnrollmentDetailsIndirectRelationshipInfo
        invoice_recipient: str
        language: str
        markup_status: Union[str, MarkupStatus]
        po_number: str
        start_date: datetime
        support_coverage: str
        support_level: Union[str, SupportLevel]

        @overload
        def __init__(
                self, 
                *, 
                end_date: Optional[datetime] = ..., 
                indirect_relationship_info: Optional[EnrollmentDetailsIndirectRelationshipInfo] = ..., 
                po_number: Optional[str] = ..., 
                start_date: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.BillingAccountPropertiesRegistrationNumber(RegistrationNumber):
        id: str
        required: bool
        type: list[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.BillingAccountPropertiesSoldTo(AddressDetails):
        address_line1: str
        address_line2: str
        address_line3: str
        city: str
        company_name: str
        country: str
        district: str
        email: str
        first_name: str
        is_valid_address: bool
        last_name: str
        middle_name: str
        phone_number: str
        postal_code: str
        region: str

        @overload
        def __init__(
                self, 
                *, 
                address_line1: str, 
                address_line2: Optional[str] = ..., 
                address_line3: Optional[str] = ..., 
                city: Optional[str] = ..., 
                company_name: Optional[str] = ..., 
                country: str, 
                district: Optional[str] = ..., 
                email: Optional[str] = ..., 
                first_name: Optional[str] = ..., 
                is_valid_address: Optional[bool] = ..., 
                last_name: Optional[str] = ..., 
                middle_name: Optional[str] = ..., 
                phone_number: Optional[str] = ..., 
                postal_code: Optional[str] = ..., 
                region: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.BillingAccountStatusReasonCode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EXPIRED = "Expired"
        MANUALLY_TERMINATED = "ManuallyTerminated"
        OTHER = "Other"
        TERMINATE_PROCESSING = "TerminateProcessing"
        TRANSFERRED = "Transferred"
        UNUSUAL_ACTIVITY = "UnusualActivity"


    class azure.mgmt.billing.models.BillingManagementTenantState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        NOT_ALLOWED = "NotAllowed"
        OTHER = "Other"
        REVOKED = "Revoked"


    class azure.mgmt.billing.models.BillingPermission(_Model):
        actions: Optional[list[str]]
        not_actions: Optional[list[str]]


    class azure.mgmt.billing.models.BillingPlan(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        P1_M = "P1M"


    class azure.mgmt.billing.models.BillingPlanInformation(_Model):
        next_payment_due_date: Optional[date]
        pricing_currency_total: Optional[Price]
        start_date: Optional[date]
        transactions: Optional[list[PaymentDetail]]

        @overload
        def __init__(
                self, 
                *, 
                next_payment_due_date: Optional[date] = ..., 
                pricing_currency_total: Optional[Price] = ..., 
                start_date: Optional[date] = ..., 
                transactions: Optional[list[PaymentDetail]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.BillingProfile(ProxyResource):
        id: str
        name: str
        properties: Optional[BillingProfileProperties]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[BillingProfileProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.BillingProfileInfo(_Model):
        billing_account_id: Optional[str]
        billing_profile_display_name: Optional[str]
        billing_profile_id: Optional[str]
        billing_profile_system_id: Optional[str]
        indirect_relationship_organization_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                billing_account_id: Optional[str] = ..., 
                billing_profile_display_name: Optional[str] = ..., 
                billing_profile_id: Optional[str] = ..., 
                billing_profile_system_id: Optional[str] = ..., 
                indirect_relationship_organization_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.BillingProfilePolicy(ProxyResource):
        id: str
        name: str
        properties: Optional[BillingProfilePolicyProperties]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[BillingProfilePolicyProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.BillingProfilePolicyProperties(_Model):
        enterprise_agreement_policies: Optional[BillingProfilePolicyPropertiesEnterpriseAgreementPolicies]
        invoice_section_label_management: Optional[Union[str, InvoiceSectionLabelManagementPolicy]]
        marketplace_purchases: Optional[Union[str, MarketplacePurchasesPolicy]]
        policies: Optional[list[PolicySummary]]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        reservation_purchases: Optional[Union[str, ReservationPurchasesPolicy]]
        savings_plan_purchases: Optional[Union[str, SavingsPlanPurchasesPolicy]]
        view_charges: Optional[Union[str, ViewChargesPolicy]]

        @overload
        def __init__(
                self, 
                *, 
                enterprise_agreement_policies: Optional[BillingProfilePolicyPropertiesEnterpriseAgreementPolicies] = ..., 
                invoice_section_label_management: Optional[Union[str, InvoiceSectionLabelManagementPolicy]] = ..., 
                marketplace_purchases: Optional[Union[str, MarketplacePurchasesPolicy]] = ..., 
                policies: Optional[list[PolicySummary]] = ..., 
                reservation_purchases: Optional[Union[str, ReservationPurchasesPolicy]] = ..., 
                savings_plan_purchases: Optional[Union[str, SavingsPlanPurchasesPolicy]] = ..., 
                view_charges: Optional[Union[str, ViewChargesPolicy]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.BillingProfilePolicyPropertiesEnterpriseAgreementPolicies(EnterpriseAgreementPolicies):
        account_owner_view_charges: Union[str, EnrollmentAccountOwnerViewCharges]
        authentication_type: Union[str, EnrollmentAuthLevelState]
        department_admin_view_charges: Union[str, EnrollmentDepartmentAdminViewCharges]

        @overload
        def __init__(
                self, 
                *, 
                account_owner_view_charges: Optional[Union[str, EnrollmentAccountOwnerViewCharges]] = ..., 
                authentication_type: Optional[Union[str, EnrollmentAuthLevelState]] = ..., 
                department_admin_view_charges: Optional[Union[str, EnrollmentDepartmentAdminViewCharges]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.BillingProfileProperties(_Model):
        bill_to: Optional[BillingProfilePropertiesBillTo]
        billing_relationship_type: Optional[Union[str, BillingRelationshipType]]
        currency: Optional[str]
        current_payment_term: Optional[BillingProfilePropertiesCurrentPaymentTerm]
        display_name: Optional[str]
        enabled_azure_plans: Optional[list[AzurePlan]]
        has_read_access: Optional[bool]
        indirect_relationship_info: Optional[BillingProfilePropertiesIndirectRelationshipInfo]
        invoice_day: Optional[int]
        invoice_email_opt_in: Optional[bool]
        invoice_recipients: Optional[list[str]]
        other_payment_terms: Optional[list[PaymentTerm]]
        po_number: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        ship_to: Optional[BillingProfilePropertiesShipTo]
        sold_to: Optional[BillingProfilePropertiesSoldTo]
        spending_limit: Optional[Union[str, SpendingLimit]]
        spending_limit_details: Optional[list[SpendingLimitDetails]]
        status: Optional[Union[str, BillingProfileStatus]]
        status_reason_code: Optional[Union[str, BillingProfileStatusReasonCode]]
        system_id: Optional[str]
        tags: Optional[dict[str, str]]
        target_clouds: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                bill_to: Optional[BillingProfilePropertiesBillTo] = ..., 
                current_payment_term: Optional[BillingProfilePropertiesCurrentPaymentTerm] = ..., 
                display_name: Optional[str] = ..., 
                enabled_azure_plans: Optional[list[AzurePlan]] = ..., 
                indirect_relationship_info: Optional[BillingProfilePropertiesIndirectRelationshipInfo] = ..., 
                invoice_email_opt_in: Optional[bool] = ..., 
                invoice_recipients: Optional[list[str]] = ..., 
                po_number: Optional[str] = ..., 
                ship_to: Optional[BillingProfilePropertiesShipTo] = ..., 
                sold_to: Optional[BillingProfilePropertiesSoldTo] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.BillingProfilePropertiesBillTo(AddressDetails):
        address_line1: str
        address_line2: str
        address_line3: str
        city: str
        company_name: str
        country: str
        district: str
        email: str
        first_name: str
        is_valid_address: bool
        last_name: str
        middle_name: str
        phone_number: str
        postal_code: str
        region: str

        @overload
        def __init__(
                self, 
                *, 
                address_line1: str, 
                address_line2: Optional[str] = ..., 
                address_line3: Optional[str] = ..., 
                city: Optional[str] = ..., 
                company_name: Optional[str] = ..., 
                country: str, 
                district: Optional[str] = ..., 
                email: Optional[str] = ..., 
                first_name: Optional[str] = ..., 
                is_valid_address: Optional[bool] = ..., 
                last_name: Optional[str] = ..., 
                middle_name: Optional[str] = ..., 
                phone_number: Optional[str] = ..., 
                postal_code: Optional[str] = ..., 
                region: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.BillingProfilePropertiesCurrentPaymentTerm(PaymentTerm):
        end_date: datetime
        is_default: bool
        start_date: datetime
        term: str

        @overload
        def __init__(
                self, 
                *, 
                end_date: Optional[datetime] = ..., 
                start_date: Optional[datetime] = ..., 
                term: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.BillingProfilePropertiesIndirectRelationshipInfo(IndirectRelationshipInfo):
        billing_account_name: str
        billing_profile_name: str
        display_name: str

        @overload
        def __init__(
                self, 
                *, 
                billing_account_name: Optional[str] = ..., 
                billing_profile_name: Optional[str] = ..., 
                display_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.BillingProfilePropertiesShipTo(AddressDetails):
        address_line1: str
        address_line2: str
        address_line3: str
        city: str
        company_name: str
        country: str
        district: str
        email: str
        first_name: str
        is_valid_address: bool
        last_name: str
        middle_name: str
        phone_number: str
        postal_code: str
        region: str

        @overload
        def __init__(
                self, 
                *, 
                address_line1: str, 
                address_line2: Optional[str] = ..., 
                address_line3: Optional[str] = ..., 
                city: Optional[str] = ..., 
                company_name: Optional[str] = ..., 
                country: str, 
                district: Optional[str] = ..., 
                email: Optional[str] = ..., 
                first_name: Optional[str] = ..., 
                is_valid_address: Optional[bool] = ..., 
                last_name: Optional[str] = ..., 
                middle_name: Optional[str] = ..., 
                phone_number: Optional[str] = ..., 
                postal_code: Optional[str] = ..., 
                region: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.BillingProfilePropertiesSoldTo(AddressDetails):
        address_line1: str
        address_line2: str
        address_line3: str
        city: str
        company_name: str
        country: str
        district: str
        email: str
        first_name: str
        is_valid_address: bool
        last_name: str
        middle_name: str
        phone_number: str
        postal_code: str
        region: str

        @overload
        def __init__(
                self, 
                *, 
                address_line1: str, 
                address_line2: Optional[str] = ..., 
                address_line3: Optional[str] = ..., 
                city: Optional[str] = ..., 
                company_name: Optional[str] = ..., 
                country: str, 
                district: Optional[str] = ..., 
                email: Optional[str] = ..., 
                first_name: Optional[str] = ..., 
                is_valid_address: Optional[bool] = ..., 
                last_name: Optional[str] = ..., 
                middle_name: Optional[str] = ..., 
                phone_number: Optional[str] = ..., 
                postal_code: Optional[str] = ..., 
                region: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.BillingProfileStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        DELETED = "Deleted"
        DISABLED = "Disabled"
        OTHER = "Other"
        UNDER_REVIEW = "UnderReview"
        WARNED = "Warned"


    class azure.mgmt.billing.models.BillingProfileStatusReasonCode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        OTHER = "Other"
        PAST_DUE = "PastDue"
        SPENDING_LIMIT_EXPIRED = "SpendingLimitExpired"
        SPENDING_LIMIT_REACHED = "SpendingLimitReached"
        UNUSUAL_ACTIVITY = "UnusualActivity"


    class azure.mgmt.billing.models.BillingProperty(ProxyResource):
        id: str
        name: str
        properties: Optional[BillingPropertyProperties]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[BillingPropertyProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.BillingPropertyProperties(_Model):
        account_admin_notification_email_address: Optional[str]
        billing_account_agreement_type: Optional[Union[str, AgreementType]]
        billing_account_display_name: Optional[str]
        billing_account_id: Optional[str]
        billing_account_sold_to_country: Optional[str]
        billing_account_status: Optional[Union[str, AccountStatus]]
        billing_account_status_reason_code: Optional[Union[str, BillingAccountStatusReasonCode]]
        billing_account_sub_type: Optional[Union[str, AccountSubType]]
        billing_account_type: Optional[Union[str, AccountType]]
        billing_currency: Optional[str]
        billing_profile_display_name: Optional[str]
        billing_profile_id: Optional[str]
        billing_profile_payment_method_family: Optional[Union[str, PaymentMethodFamily]]
        billing_profile_payment_method_type: Optional[str]
        billing_profile_spending_limit: Optional[Union[str, SpendingLimit]]
        billing_profile_spending_limit_details: Optional[list[SpendingLimitDetails]]
        billing_profile_status: Optional[Union[str, BillingProfileStatus]]
        billing_profile_status_reason_code: Optional[Union[str, BillingProfileStatusReasonCode]]
        billing_tenant_id: Optional[str]
        cost_center: Optional[str]
        customer_display_name: Optional[str]
        customer_id: Optional[str]
        customer_status: Optional[Union[str, CustomerStatus]]
        enrollment_details: Optional[BillingPropertyPropertiesEnrollmentDetails]
        invoice_section_display_name: Optional[str]
        invoice_section_id: Optional[str]
        invoice_section_status: Optional[Union[str, InvoiceSectionState]]
        invoice_section_status_reason_code: Optional[Union[str, InvoiceSectionStateReasonCode]]
        is_account_admin: Optional[bool]
        is_transitioned_billing_account: Optional[bool]
        product_id: Optional[str]
        product_name: Optional[str]
        sku_description: Optional[str]
        sku_id: Optional[str]
        subscription_billing_status: Optional[Union[str, BillingSubscriptionStatus]]
        subscription_billing_status_details: Optional[list[BillingSubscriptionStatusDetails]]
        subscription_billing_type: Optional[Union[str, SubscriptionBillingType]]
        subscription_service_usage_address: Optional[BillingPropertyPropertiesSubscriptionServiceUsageAddress]
        subscription_workload_type: Optional[Union[str, SubscriptionWorkloadType]]

        @overload
        def __init__(
                self, 
                *, 
                cost_center: Optional[str] = ..., 
                enrollment_details: Optional[BillingPropertyPropertiesEnrollmentDetails] = ..., 
                subscription_service_usage_address: Optional[BillingPropertyPropertiesSubscriptionServiceUsageAddress] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.BillingPropertyPropertiesEnrollmentDetails(SubscriptionEnrollmentDetails):
        department_display_name: str
        department_id: str
        enrollment_account_display_name: str
        enrollment_account_id: str
        enrollment_account_status: str

        @overload
        def __init__(
                self, 
                *, 
                department_display_name: Optional[str] = ..., 
                department_id: Optional[str] = ..., 
                enrollment_account_display_name: Optional[str] = ..., 
                enrollment_account_id: Optional[str] = ..., 
                enrollment_account_status: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.BillingPropertyPropertiesSubscriptionServiceUsageAddress(AddressDetails):
        address_line1: str
        address_line2: str
        address_line3: str
        city: str
        company_name: str
        country: str
        district: str
        email: str
        first_name: str
        is_valid_address: bool
        last_name: str
        middle_name: str
        phone_number: str
        postal_code: str
        region: str

        @overload
        def __init__(
                self, 
                *, 
                address_line1: str, 
                address_line2: Optional[str] = ..., 
                address_line3: Optional[str] = ..., 
                city: Optional[str] = ..., 
                company_name: Optional[str] = ..., 
                country: str, 
                district: Optional[str] = ..., 
                email: Optional[str] = ..., 
                first_name: Optional[str] = ..., 
                is_valid_address: Optional[bool] = ..., 
                last_name: Optional[str] = ..., 
                middle_name: Optional[str] = ..., 
                phone_number: Optional[str] = ..., 
                postal_code: Optional[str] = ..., 
                region: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.BillingRelationshipType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CSP_CUSTOMER = "CSPCustomer"
        CSP_PARTNER = "CSPPartner"
        DIRECT = "Direct"
        INDIRECT_CUSTOMER = "IndirectCustomer"
        INDIRECT_PARTNER = "IndirectPartner"
        OTHER = "Other"


    class azure.mgmt.billing.models.BillingRequest(ProxyResource):
        id: str
        name: str
        properties: Optional[BillingRequestProperties]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[BillingRequestProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.BillingRequestProperties(_Model):
        additional_information: Optional[dict[str, str]]
        billing_account_display_name: Optional[str]
        billing_account_id: Optional[str]
        billing_account_name: Optional[str]
        billing_account_primary_billing_tenant_id: Optional[str]
        billing_profile_display_name: Optional[str]
        billing_profile_id: Optional[str]
        billing_profile_name: Optional[str]
        billing_scope: Optional[str]
        created_by: Optional[BillingRequestPropertiesCreatedBy]
        creation_date: Optional[datetime]
        customer_display_name: Optional[str]
        customer_id: Optional[str]
        customer_name: Optional[str]
        decision_reason: Optional[str]
        expiration_date: Optional[datetime]
        invoice_section_display_name: Optional[str]
        invoice_section_id: Optional[str]
        invoice_section_name: Optional[str]
        justification: Optional[str]
        last_updated_by: Optional[BillingRequestPropertiesLastUpdatedBy]
        last_updated_date: Optional[datetime]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        recipients: Optional[list[Principal]]
        request_scope: Optional[str]
        reviewal_date: Optional[datetime]
        reviewed_by: Optional[BillingRequestPropertiesReviewedBy]
        status: Optional[Union[str, BillingRequestStatus]]
        subscription_display_name: Optional[str]
        subscription_id: Optional[str]
        subscription_name: Optional[str]
        type: Optional[Union[str, BillingRequestType]]

        @overload
        def __init__(
                self, 
                *, 
                additional_information: Optional[dict[str, str]] = ..., 
                created_by: Optional[BillingRequestPropertiesCreatedBy] = ..., 
                decision_reason: Optional[str] = ..., 
                justification: Optional[str] = ..., 
                last_updated_by: Optional[BillingRequestPropertiesLastUpdatedBy] = ..., 
                recipients: Optional[list[Principal]] = ..., 
                request_scope: Optional[str] = ..., 
                reviewed_by: Optional[BillingRequestPropertiesReviewedBy] = ..., 
                status: Optional[Union[str, BillingRequestStatus]] = ..., 
                type: Optional[Union[str, BillingRequestType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.BillingRequestPropertiesCreatedBy(Principal):
        object_id: str
        tenant_id: str
        upn: str

        @overload
        def __init__(
                self, 
                *, 
                object_id: Optional[str] = ..., 
                tenant_id: Optional[str] = ..., 
                upn: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.BillingRequestPropertiesLastUpdatedBy(Principal):
        object_id: str
        tenant_id: str
        upn: str

        @overload
        def __init__(
                self, 
                *, 
                object_id: Optional[str] = ..., 
                tenant_id: Optional[str] = ..., 
                upn: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.BillingRequestPropertiesReviewedBy(Principal):
        object_id: str
        tenant_id: str
        upn: str

        @overload
        def __init__(
                self, 
                *, 
                object_id: Optional[str] = ..., 
                tenant_id: Optional[str] = ..., 
                upn: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.BillingRequestStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPROVED = "Approved"
        CANCELLED = "Cancelled"
        COMPLETED = "Completed"
        DECLINED = "Declined"
        EXPIRED = "Expired"
        OTHER = "Other"
        PENDING = "Pending"


    class azure.mgmt.billing.models.BillingRequestType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INVOICE_ACCESS = "InvoiceAccess"
        OTHER = "Other"
        PROVISIONING_ACCESS = "ProvisioningAccess"
        ROLE_ASSIGNMENT = "RoleAssignment"
        UPDATE_BILLING_POLICY = "UpdateBillingPolicy"


    class azure.mgmt.billing.models.BillingRoleAssignment(ProxyResource):
        id: str
        name: str
        properties: Optional[BillingRoleAssignmentProperties]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[BillingRoleAssignmentProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.BillingRoleAssignmentListResult(_Model):
        next_link: Optional[str]
        value: list[BillingRoleAssignment]

        @overload
        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.BillingRoleAssignmentProperties(_Model):
        billing_account_display_name: Optional[str]
        billing_account_id: Optional[str]
        billing_profile_display_name: Optional[str]
        billing_profile_id: Optional[str]
        billing_request_id: Optional[str]
        created_by_principal_id: Optional[str]
        created_by_principal_puid: Optional[str]
        created_by_principal_tenant_id: Optional[str]
        created_by_user_email_address: Optional[str]
        created_on: Optional[datetime]
        customer_display_name: Optional[str]
        customer_id: Optional[str]
        invoice_section_display_name: Optional[str]
        invoice_section_id: Optional[str]
        modified_by_principal_id: Optional[str]
        modified_by_principal_puid: Optional[str]
        modified_by_principal_tenant_id: Optional[str]
        modified_by_user_email_address: Optional[str]
        modified_on: Optional[datetime]
        principal_display_name: Optional[str]
        principal_id: Optional[str]
        principal_puid: Optional[str]
        principal_tenant_id: Optional[str]
        principal_tenant_name: Optional[str]
        principal_type: Optional[Union[str, PrincipalType]]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        role_definition_id: str
        scope: Optional[str]
        user_authentication_type: Optional[str]
        user_email_address: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                principal_id: Optional[str] = ..., 
                principal_puid: Optional[str] = ..., 
                principal_tenant_id: Optional[str] = ..., 
                role_definition_id: str, 
                scope: Optional[str] = ..., 
                user_authentication_type: Optional[str] = ..., 
                user_email_address: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.BillingRoleDefinition(ProxyResource):
        id: str
        name: str
        properties: Optional[BillingRoleDefinitionProperties]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[BillingRoleDefinitionProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.BillingRoleDefinitionProperties(_Model):
        description: Optional[str]
        permissions: Optional[list[BillingPermission]]
        role_name: str

        @overload
        def __init__(
                self, 
                *, 
                role_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.BillingSubscription(ProxyResource):
        id: str
        name: str
        properties: Optional[BillingSubscriptionProperties]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[BillingSubscriptionProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.BillingSubscriptionAlias(ProxyResource):
        id: str
        name: str
        properties: Optional[BillingSubscriptionAliasProperties]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[BillingSubscriptionAliasProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.BillingSubscriptionAliasProperties(BillingSubscriptionProperties):
        auto_renew: Union[str, AutoRenew]
        beneficiary: Beneficiary
        beneficiary_tenant_id: str
        billing_frequency: str
        billing_policies: dict[str, str]
        billing_profile_display_name: str
        billing_profile_id: str
        billing_profile_name: str
        billing_subscription_id: Optional[str]
        consumption_cost_center: str
        customer_display_name: str
        customer_id: str
        customer_name: str
        display_name: str
        enrollment_account_display_name: str
        enrollment_account_id: str
        enrollment_account_subscription_details: EnrollmentAccountSubscriptionDetails
        invoice_section_display_name: str
        invoice_section_id: str
        invoice_section_name: str
        last_month_charges: Amount
        month_to_date_charges: Amount
        next_billing_cycle_details: NextBillingCycleDetails
        offer_id: str
        operation_status: Union[str, BillingSubscriptionOperationStatus]
        product_category: str
        product_type: str
        product_type_id: str
        provisioning_state: Union[str, ProvisioningState]
        provisioning_tenant_id: str
        purchase_date: datetime
        quantity: int
        renewal_term_details: RenewalTermDetails
        reseller: Reseller
        resource_uri: str
        sku_description: str
        sku_id: str
        status: Union[str, BillingSubscriptionStatus]
        subscription_id: str
        suspension_reason_details: list[BillingSubscriptionStatusDetails]
        suspension_reasons: list[str]
        system_overrides: SystemOverrides
        term_duration: str
        term_end_date: datetime
        term_start_date: datetime

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                auto_renew: Optional[Union[str, AutoRenew]] = ..., 
                beneficiary: Optional[Beneficiary] = ..., 
                beneficiary_tenant_id: Optional[str] = ..., 
                billing_frequency: Optional[str] = ..., 
                billing_profile_id: Optional[str] = ..., 
                consumption_cost_center: Optional[str] = ..., 
                customer_id: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                invoice_section_id: Optional[str] = ..., 
                product_type_id: Optional[str] = ..., 
                provisioning_tenant_id: Optional[str] = ..., 
                quantity: Optional[int] = ..., 
                sku_id: Optional[str] = ..., 
                system_overrides: Optional[SystemOverrides] = ..., 
                term_duration: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.billing.models.BillingSubscriptionMergeRequest(_Model):
        quantity: Optional[int]
        target_billing_subscription_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                quantity: Optional[int] = ..., 
                target_billing_subscription_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.BillingSubscriptionOperationStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LOCKED_FOR_UPDATE = "LockedForUpdate"
        NONE = "None"
        OTHER = "Other"


    class azure.mgmt.billing.models.BillingSubscriptionPatch(ProxyResourceWithTags):
        id: str
        name: str
        properties: Optional[BillingSubscriptionProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[BillingSubscriptionProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.BillingSubscriptionProperties(_Model):
        auto_renew: Optional[Union[str, AutoRenew]]
        beneficiary: Optional[Beneficiary]
        beneficiary_tenant_id: Optional[str]
        billing_frequency: Optional[str]
        billing_policies: Optional[dict[str, str]]
        billing_profile_display_name: Optional[str]
        billing_profile_id: Optional[str]
        billing_profile_name: Optional[str]
        consumption_cost_center: Optional[str]
        customer_display_name: Optional[str]
        customer_id: Optional[str]
        customer_name: Optional[str]
        display_name: Optional[str]
        enrollment_account_display_name: Optional[str]
        enrollment_account_id: Optional[str]
        enrollment_account_subscription_details: Optional[EnrollmentAccountSubscriptionDetails]
        invoice_section_display_name: Optional[str]
        invoice_section_id: Optional[str]
        invoice_section_name: Optional[str]
        last_month_charges: Optional[Amount]
        month_to_date_charges: Optional[Amount]
        next_billing_cycle_details: Optional[NextBillingCycleDetails]
        offer_id: Optional[str]
        operation_status: Optional[Union[str, BillingSubscriptionOperationStatus]]
        product_category: Optional[str]
        product_type: Optional[str]
        product_type_id: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        provisioning_tenant_id: Optional[str]
        purchase_date: Optional[datetime]
        quantity: Optional[int]
        renewal_term_details: Optional[RenewalTermDetails]
        reseller: Optional[Reseller]
        resource_uri: Optional[str]
        sku_description: Optional[str]
        sku_id: Optional[str]
        status: Optional[Union[str, BillingSubscriptionStatus]]
        subscription_id: Optional[str]
        suspension_reason_details: Optional[list[BillingSubscriptionStatusDetails]]
        suspension_reasons: Optional[list[str]]
        system_overrides: Optional[SystemOverrides]
        term_duration: Optional[str]
        term_end_date: Optional[datetime]
        term_start_date: Optional[datetime]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                auto_renew: Optional[Union[str, AutoRenew]] = ..., 
                beneficiary: Optional[Beneficiary] = ..., 
                beneficiary_tenant_id: Optional[str] = ..., 
                billing_frequency: Optional[str] = ..., 
                billing_profile_id: Optional[str] = ..., 
                consumption_cost_center: Optional[str] = ..., 
                customer_id: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                invoice_section_id: Optional[str] = ..., 
                product_type_id: Optional[str] = ..., 
                provisioning_tenant_id: Optional[str] = ..., 
                quantity: Optional[int] = ..., 
                sku_id: Optional[str] = ..., 
                system_overrides: Optional[SystemOverrides] = ..., 
                term_duration: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.billing.models.BillingSubscriptionSplitRequest(_Model):
        billing_frequency: Optional[str]
        quantity: Optional[int]
        target_product_type_id: Optional[str]
        target_sku_id: Optional[str]
        term_duration: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                billing_frequency: Optional[str] = ..., 
                quantity: Optional[int] = ..., 
                target_product_type_id: Optional[str] = ..., 
                target_sku_id: Optional[str] = ..., 
                term_duration: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.BillingSubscriptionStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        AUTO_RENEW = "AutoRenew"
        CANCELLED = "Cancelled"
        DELETED = "Deleted"
        DISABLED = "Disabled"
        EXPIRED = "Expired"
        EXPIRING = "Expiring"
        FAILED = "Failed"
        OTHER = "Other"
        SUSPENDED = "Suspended"
        UNKNOWN = "Unknown"
        WARNED = "Warned"


    class azure.mgmt.billing.models.BillingSubscriptionStatusDetails(_Model):
        effective_date: Optional[datetime]
        reason: Optional[Union[str, SubscriptionStatusReason]]


    class azure.mgmt.billing.models.CancelSubscriptionRequest(_Model):
        cancellation_reason: Union[str, CancellationReason]
        customer_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                cancellation_reason: Union[str, CancellationReason], 
                customer_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.Cancellation(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALLOWED = "Allowed"
        NOT_ALLOWED = "NotAllowed"


    class azure.mgmt.billing.models.CancellationReason(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPROMISE = "Compromise"
        DISPUTE = "Dispute"
        OTHER = "Other"


    class azure.mgmt.billing.models.Category(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AFFILIATE_PURCHASE_TERMS = "AffiliatePurchaseTerms"
        INDIRECT_FOR_GOVERNMENT_AGREEMENT = "IndirectForGovernmentAgreement"
        MICROSOFT_CUSTOMER_AGREEMENT = "MicrosoftCustomerAgreement"
        MICROSOFT_PARTNER_AGREEMENT = "MicrosoftPartnerAgreement"
        OTHER = "Other"
        UK_CLOUD_COMPUTE_FRAMEWORK = "UKCloudComputeFramework"


    class azure.mgmt.billing.models.CheckAccessRequest(_Model):
        actions: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                actions: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.CheckAccessResponse(_Model):
        access_decision: Optional[Union[str, AccessDecision]]
        action: Optional[str]


    class azure.mgmt.billing.models.Commitment(Price):
        amount: float
        currency_code: str
        grain: Optional[Union[str, CommitmentGrain]]

        @overload
        def __init__(
                self, 
                *, 
                amount: Optional[float] = ..., 
                currency_code: Optional[str] = ..., 
                grain: Optional[Union[str, CommitmentGrain]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.CommitmentGrain(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HOURLY = "Hourly"


    class azure.mgmt.billing.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.billing.models.CreditType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_CREDIT_OFFER = "AzureCreditOffer"
        AZURE_FREE_CREDIT = "AzureFreeCredit"
        OTHER = "Other"
        REFUND = "Refund"
        SERVICE_INTERRUPTION = "ServiceInterruption"


    class azure.mgmt.billing.models.Customer(ProxyResource):
        id: str
        name: str
        properties: Optional[CustomerProperties]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[CustomerProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.CustomerPolicy(ProxyResource):
        id: str
        name: str
        properties: Optional[CustomerPolicyProperties]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[CustomerPolicyProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.CustomerPolicyProperties(_Model):
        policies: Optional[list[PolicySummary]]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        view_charges: Union[str, ViewChargesPolicy]

        @overload
        def __init__(
                self, 
                *, 
                policies: Optional[list[PolicySummary]] = ..., 
                view_charges: Union[str, ViewChargesPolicy]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.CustomerProperties(_Model):
        billing_profile_display_name: Optional[str]
        billing_profile_id: Optional[str]
        display_name: Optional[str]
        enabled_azure_plans: Optional[list[AzurePlan]]
        resellers: Optional[list[Reseller]]
        status: Optional[Union[str, CustomerStatus]]
        system_id: Optional[str]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                enabled_azure_plans: Optional[list[AzurePlan]] = ..., 
                resellers: Optional[list[Reseller]] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.CustomerStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        DELETED = "Deleted"
        DISABLED = "Disabled"
        OTHER = "Other"
        PENDING = "Pending"
        UNDER_REVIEW = "UnderReview"
        WARNED = "Warned"


    class azure.mgmt.billing.models.DeleteBillingProfileEligibilityCode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE_BILLING_SUBSCRIPTIONS = "ActiveBillingSubscriptions"
        ACTIVE_CREDITS = "ActiveCredits"
        ACTIVE_CREDIT_CARD = "ActiveCreditCard"
        LAST_BILLING_PROFILE = "LastBillingProfile"
        NONE = "None"
        NOT_SUPPORTED = "NotSupported"
        OUTSTANDING_CHARGES = "OutstandingCharges"
        PENDING_CHARGES = "PendingCharges"
        RESERVED_INSTANCES = "ReservedInstances"


    class azure.mgmt.billing.models.DeleteBillingProfileEligibilityDetail(_Model):
        code: Optional[Union[str, DeleteBillingProfileEligibilityCode]]
        message: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                code: Optional[Union[str, DeleteBillingProfileEligibilityCode]] = ..., 
                message: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.DeleteBillingProfileEligibilityResult(_Model):
        eligibility_details: Optional[list[DeleteBillingProfileEligibilityDetail]]
        eligibility_status: Optional[Union[str, DeleteBillingProfileEligibilityStatus]]

        @overload
        def __init__(
                self, 
                *, 
                eligibility_details: Optional[list[DeleteBillingProfileEligibilityDetail]] = ..., 
                eligibility_status: Optional[Union[str, DeleteBillingProfileEligibilityStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.DeleteBillingProfileEligibilityStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALLOWED = "Allowed"
        NOT_ALLOWED = "NotAllowed"


    class azure.mgmt.billing.models.DeleteInvoiceSectionEligibilityCode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE_AZURE_PLANS = "ActiveAzurePlans"
        ACTIVE_BILLING_SUBSCRIPTIONS = "ActiveBillingSubscriptions"
        LAST_INVOICE_SECTION = "LastInvoiceSection"
        OTHER = "Other"
        RESERVED_INSTANCES = "ReservedInstances"


    class azure.mgmt.billing.models.DeleteInvoiceSectionEligibilityDetail(_Model):
        code: Optional[Union[str, DeleteInvoiceSectionEligibilityCode]]
        message: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                code: Optional[Union[str, DeleteInvoiceSectionEligibilityCode]] = ..., 
                message: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.DeleteInvoiceSectionEligibilityResult(_Model):
        eligibility_details: Optional[list[DeleteInvoiceSectionEligibilityDetail]]
        eligibility_status: Optional[Union[str, DeleteInvoiceSectionEligibilityStatus]]

        @overload
        def __init__(
                self, 
                *, 
                eligibility_details: Optional[list[DeleteInvoiceSectionEligibilityDetail]] = ..., 
                eligibility_status: Optional[Union[str, DeleteInvoiceSectionEligibilityStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.DeleteInvoiceSectionEligibilityStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALLOWED = "Allowed"
        NOT_ALLOWED = "NotAllowed"


    class azure.mgmt.billing.models.Department(ProxyResource):
        id: str
        name: str
        properties: Optional[DepartmentProperties]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[DepartmentProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.DepartmentProperties(_Model):
        cost_center: Optional[str]
        display_name: Optional[str]
        id: Optional[str]
        status: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                cost_center: Optional[str] = ..., 
                display_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.DetailedTransferStatus(_Model):
        error_details: Optional[TransferError]
        product_id: Optional[str]
        product_name: Optional[str]
        product_type: Optional[Union[str, ProductType]]
        sku_description: Optional[str]
        transfer_status: Optional[Union[str, ProductTransferStatus]]

        @overload
        def __init__(
                self, 
                *, 
                error_details: Optional[TransferError] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.DocumentDownloadRequest(_Model):
        document_name: Optional[str]
        invoice_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                document_name: Optional[str] = ..., 
                invoice_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.DocumentDownloadResult(_Model):
        expiry_time: Optional[str]
        url: Optional[str]


    class azure.mgmt.billing.models.DocumentSource(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DRS = "DRS"
        ENF = "ENF"
        OTHER = "Other"


    class azure.mgmt.billing.models.EligibleProductType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_RESERVATION = "AzureReservation"
        DEV_TEST_AZURE_SUBSCRIPTION = "DevTestAzureSubscription"
        STANDARD_AZURE_SUBSCRIPTION = "StandardAzureSubscription"


    class azure.mgmt.billing.models.EnrollmentAccount(ProxyResource):
        id: str
        name: str
        properties: Optional[EnrollmentAccountProperties]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[EnrollmentAccountProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.EnrollmentAccountOwnerViewCharges(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALLOWED = "Allowed"
        DISABLED = "Disabled"
        NOT_ALLOWED = "NotAllowed"
        OTHER = "Other"


    class azure.mgmt.billing.models.EnrollmentAccountProperties(_Model):
        account_owner: Optional[str]
        auth_type: Optional[str]
        cost_center: Optional[str]
        department_display_name: Optional[str]
        department_id: Optional[str]
        display_name: Optional[str]
        end_date: Optional[datetime]
        is_dev_test_enabled: Optional[bool]
        start_date: Optional[datetime]
        status: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                cost_center: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                is_dev_test_enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.EnrollmentAccountSubscriptionDetails(_Model):
        enrollment_account_start_date: Optional[datetime]
        subscription_enrollment_account_status: Optional[Union[str, SubscriptionEnrollmentAccountStatus]]


    class azure.mgmt.billing.models.EnrollmentAuthLevelState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MICROSOFT_ACCOUNT_ONLY = "MicrosoftAccountOnly"
        MIXED_ACCOUNT = "MixedAccount"
        ORGANIZATIONAL_ACCOUNT_CROSS_TENANT = "OrganizationalAccountCrossTenant"
        ORGANIZATIONAL_ACCOUNT_ONLY = "OrganizationalAccountOnly"
        OTHER = "Other"


    class azure.mgmt.billing.models.EnrollmentDepartmentAdminViewCharges(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALLOWED = "Allowed"
        DISABLED = "Disabled"
        NOT_ALLOWED = "NotAllowed"
        OTHER = "Other"


    class azure.mgmt.billing.models.EnrollmentDetails(_Model):
        billing_cycle: Optional[str]
        channel: Optional[str]
        cloud: Optional[str]
        country_code: Optional[str]
        currency: Optional[str]
        end_date: Optional[datetime]
        extended_term_option: Optional[Union[str, ExtendedTermOption]]
        indirect_relationship_info: Optional[EnrollmentDetailsIndirectRelationshipInfo]
        invoice_recipient: Optional[str]
        language: Optional[str]
        markup_status: Optional[Union[str, MarkupStatus]]
        po_number: Optional[str]
        start_date: Optional[datetime]
        support_coverage: Optional[str]
        support_level: Optional[Union[str, SupportLevel]]

        @overload
        def __init__(
                self, 
                *, 
                end_date: Optional[datetime] = ..., 
                indirect_relationship_info: Optional[EnrollmentDetailsIndirectRelationshipInfo] = ..., 
                po_number: Optional[str] = ..., 
                start_date: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.EnrollmentDetailsIndirectRelationshipInfo(IndirectRelationshipInfo):
        billing_account_name: str
        billing_profile_name: str
        display_name: str

        @overload
        def __init__(
                self, 
                *, 
                billing_account_name: Optional[str] = ..., 
                billing_profile_name: Optional[str] = ..., 
                display_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.EnterpriseAgreementPolicies(_Model):
        account_owner_view_charges: Optional[Union[str, EnrollmentAccountOwnerViewCharges]]
        authentication_type: Optional[Union[str, EnrollmentAuthLevelState]]
        department_admin_view_charges: Optional[Union[str, EnrollmentDepartmentAdminViewCharges]]

        @overload
        def __init__(
                self, 
                *, 
                account_owner_view_charges: Optional[Union[str, EnrollmentAccountOwnerViewCharges]] = ..., 
                authentication_type: Optional[Union[str, EnrollmentAuthLevelState]] = ..., 
                department_admin_view_charges: Optional[Union[str, EnrollmentDepartmentAdminViewCharges]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.billing.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.billing.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.ExtendedStatusDefinitionProperties(_Model):
        subscription_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                subscription_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.ExtendedStatusInfo(_Model):
        message: Optional[str]
        properties: Optional[ExtendedStatusInfoProperties]
        status_code: Optional[str]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                message: Optional[str] = ..., 
                properties: Optional[ExtendedStatusInfoProperties] = ..., 
                status_code: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.billing.models.ExtendedStatusInfoProperties(_Model):
        subscription_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                subscription_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.ExtendedTermOption(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        OPTED_IN = "Opted-In"
        OPTED_OUT = "Opted-Out"
        OTHER = "Other"


    class azure.mgmt.billing.models.FailedPayment(_Model):
        date: Optional[datetime]
        failed_payment_reason: Optional[Union[str, FailedPaymentReason]]


    class azure.mgmt.billing.models.FailedPaymentReason(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BANK_DECLINED = "BankDeclined"
        CARD_EXPIRED = "CardExpired"
        INCORRECT_CARD_DETAILS = "IncorrectCardDetails"
        OTHER = "Other"


    class azure.mgmt.billing.models.IndirectRelationshipInfo(_Model):
        billing_account_name: Optional[str]
        billing_profile_name: Optional[str]
        display_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                billing_account_name: Optional[str] = ..., 
                billing_profile_name: Optional[str] = ..., 
                display_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.InitiateTransferProperties(_Model):
        recipient_email_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                recipient_email_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.InitiateTransferRequest(_Model):
        properties: Optional[InitiateTransferProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[InitiateTransferProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.billing.models.InitiatorCustomerType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EA = "EA"
        PARTNER = "Partner"


    class azure.mgmt.billing.models.InstanceFlexibility(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        OFF = "Off"
        ON = "On"


    class azure.mgmt.billing.models.Invoice(ProxyResource):
        id: str
        name: str
        properties: Optional[InvoiceProperties]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[InvoiceProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.InvoiceDocument(_Model):
        document_numbers: Optional[list[str]]
        external_url: Optional[str]
        kind: Optional[Union[str, InvoiceDocumentType]]
        name: Optional[str]
        source: Optional[Union[str, DocumentSource]]
        url: Optional[str]


    class azure.mgmt.billing.models.InvoiceDocumentType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CREDIT_NOTE = "CreditNote"
        INVOICE = "Invoice"
        OTHER = "Other"
        SUMMARY = "Summary"
        TAX_RECEIPT = "TaxReceipt"
        TRANSACTIONS = "Transactions"
        VOID_NOTE = "VoidNote"


    class azure.mgmt.billing.models.InvoiceProperties(_Model):
        amount_due: Optional[InvoicePropertiesAmountDue]
        azure_prepayment_applied: Optional[InvoicePropertiesAzurePrepaymentApplied]
        billed_amount: Optional[InvoicePropertiesBilledAmount]
        billed_document_id: Optional[str]
        billing_profile_display_name: Optional[str]
        billing_profile_id: Optional[str]
        credit_amount: Optional[InvoicePropertiesCreditAmount]
        credit_for_document_id: Optional[str]
        document_type: Optional[Union[str, InvoiceDocumentType]]
        documents: Optional[list[InvoiceDocument]]
        due_date: Optional[datetime]
        failed_payments: Optional[list[FailedPayment]]
        free_azure_credit_applied: Optional[InvoicePropertiesFreeAzureCreditApplied]
        invoice_date: Optional[datetime]
        invoice_period_end_date: Optional[datetime]
        invoice_period_start_date: Optional[datetime]
        invoice_type: Optional[Union[str, InvoiceType]]
        is_monthly_invoice: Optional[bool]
        payments: Optional[list[Payment]]
        purchase_order_number: Optional[str]
        rebill_details: Optional[InvoicePropertiesRebillDetails]
        refund_details: Optional[InvoicePropertiesRefundDetails]
        special_taxation_type: Optional[Union[str, SpecialTaxationType]]
        status: Optional[Union[str, InvoiceStatus]]
        sub_total: Optional[InvoicePropertiesSubTotal]
        subscription_display_name: Optional[str]
        subscription_id: Optional[str]
        tax_amount: Optional[InvoicePropertiesTaxAmount]
        total_amount: Optional[InvoicePropertiesTotalAmount]

        @overload
        def __init__(
                self, 
                *, 
                amount_due: Optional[InvoicePropertiesAmountDue] = ..., 
                azure_prepayment_applied: Optional[InvoicePropertiesAzurePrepaymentApplied] = ..., 
                billed_amount: Optional[InvoicePropertiesBilledAmount] = ..., 
                credit_amount: Optional[InvoicePropertiesCreditAmount] = ..., 
                free_azure_credit_applied: Optional[InvoicePropertiesFreeAzureCreditApplied] = ..., 
                rebill_details: Optional[InvoicePropertiesRebillDetails] = ..., 
                refund_details: Optional[InvoicePropertiesRefundDetails] = ..., 
                sub_total: Optional[InvoicePropertiesSubTotal] = ..., 
                tax_amount: Optional[InvoicePropertiesTaxAmount] = ..., 
                total_amount: Optional[InvoicePropertiesTotalAmount] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.InvoicePropertiesAmountDue(Amount):
        currency: str
        value: float


    class azure.mgmt.billing.models.InvoicePropertiesAzurePrepaymentApplied(Amount):
        currency: str
        value: float


    class azure.mgmt.billing.models.InvoicePropertiesBilledAmount(Amount):
        currency: str
        value: float


    class azure.mgmt.billing.models.InvoicePropertiesCreditAmount(Amount):
        currency: str
        value: float


    class azure.mgmt.billing.models.InvoicePropertiesFreeAzureCreditApplied(Amount):
        currency: str
        value: float


    class azure.mgmt.billing.models.InvoicePropertiesRebillDetails(RebillDetails):
        credit_note_document_id: str
        invoice_document_id: str
        rebill_details: RebillDetails


    class azure.mgmt.billing.models.InvoicePropertiesRefundDetails(RefundDetailsSummary):
        amount_refunded: RefundDetailsSummaryAmountRefunded
        amount_requested: RefundDetailsSummaryAmountRequested
        approved_on: datetime
        completed_on: datetime
        rebill_invoice_id: str
        refund_operation_id: str
        refund_reason: Union[str, RefundReasonCode]
        refund_status: Union[str, RefundStatus]
        requested_on: datetime
        transaction_count: int

        @overload
        def __init__(
                self, 
                *, 
                amount_refunded: Optional[RefundDetailsSummaryAmountRefunded] = ..., 
                amount_requested: Optional[RefundDetailsSummaryAmountRequested] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.InvoicePropertiesSubTotal(Amount):
        currency: str
        value: float


    class azure.mgmt.billing.models.InvoicePropertiesTaxAmount(Amount):
        currency: str
        value: float


    class azure.mgmt.billing.models.InvoicePropertiesTotalAmount(Amount):
        currency: str
        value: float


    class azure.mgmt.billing.models.InvoiceSection(ProxyResource):
        id: str
        name: str
        properties: Optional[InvoiceSectionProperties]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[InvoiceSectionProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.InvoiceSectionLabelManagementPolicy(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALLOWED = "Allowed"
        NOT_ALLOWED = "NotAllowed"
        OTHER = "Other"


    class azure.mgmt.billing.models.InvoiceSectionProperties(_Model):
        display_name: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        reason_code: Optional[Union[str, InvoiceSectionStateReasonCode]]
        state: Optional[Union[str, InvoiceSectionState]]
        system_id: Optional[str]
        tags: Optional[dict[str, str]]
        target_cloud: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                display_name: Optional[str] = ..., 
                reason_code: Optional[Union[str, InvoiceSectionStateReasonCode]] = ..., 
                state: Optional[Union[str, InvoiceSectionState]] = ..., 
                tags: Optional[dict[str, str]] = ..., 
                target_cloud: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.InvoiceSectionState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        DELETED = "Deleted"
        DISABLED = "Disabled"
        OTHER = "Other"
        RESTRICTED = "Restricted"
        UNDER_REVIEW = "UnderReview"
        WARNED = "Warned"


    class azure.mgmt.billing.models.InvoiceSectionStateReasonCode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        OTHER = "Other"
        PAST_DUE = "PastDue"
        SPENDING_LIMIT_EXPIRED = "SpendingLimitExpired"
        SPENDING_LIMIT_REACHED = "SpendingLimitReached"
        UNUSUAL_ACTIVITY = "UnusualActivity"


    class azure.mgmt.billing.models.InvoiceSectionWithCreateSubPermission(_Model):
        billing_profile_display_name: Optional[str]
        billing_profile_id: Optional[str]
        billing_profile_spending_limit: Optional[Union[str, SpendingLimit]]
        billing_profile_status: Optional[Union[str, BillingProfileStatus]]
        billing_profile_status_reason_code: Optional[Union[str, BillingProfileStatusReasonCode]]
        billing_profile_system_id: Optional[str]
        enabled_azure_plans: Optional[list[AzurePlan]]
        invoice_section_display_name: Optional[str]
        invoice_section_id: Optional[str]
        invoice_section_system_id: Optional[str]


    class azure.mgmt.billing.models.InvoiceStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DUE = "Due"
        LOCKED = "Locked"
        OTHER = "Other"
        OVER_DUE = "OverDue"
        PAID = "Paid"
        VOID = "Void"


    class azure.mgmt.billing.models.InvoiceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_MARKETPLACE = "AzureMarketplace"
        AZURE_SERVICES = "AzureServices"
        AZURE_SUPPORT = "AzureSupport"
        OTHER = "Other"


    class azure.mgmt.billing.models.MarketplacePurchasesPolicy(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALL_ALLOWED = "AllAllowed"
        DISABLED = "Disabled"
        NOT_ALLOWED = "NotAllowed"
        ONLY_FREE_ALLOWED = "OnlyFreeAllowed"
        OTHER = "Other"


    class azure.mgmt.billing.models.MarkupStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        LOCKED = "Locked"
        OTHER = "Other"
        PREVIEW = "Preview"
        PUBLISHED = "Published"


    class azure.mgmt.billing.models.MoveBillingSubscriptionEligibilityResult(_Model):
        error_details: Optional[MoveBillingSubscriptionErrorDetails]
        is_move_eligible: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                error_details: Optional[MoveBillingSubscriptionErrorDetails] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.MoveBillingSubscriptionErrorDetails(_Model):
        code: Optional[Union[str, SubscriptionTransferValidationErrorCode]]
        details: Optional[str]
        message: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                code: Optional[Union[str, SubscriptionTransferValidationErrorCode]] = ..., 
                details: Optional[str] = ..., 
                message: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.MoveBillingSubscriptionRequest(_Model):
        destination_enrollment_account_id: Optional[str]
        destination_invoice_section_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                destination_enrollment_account_id: Optional[str] = ..., 
                destination_invoice_section_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.MoveProductEligibilityResult(_Model):
        error_details: Optional[MoveProductEligibilityResultErrorDetails]
        is_move_eligible: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                error_details: Optional[MoveProductEligibilityResultErrorDetails] = ..., 
                is_move_eligible: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.MoveProductEligibilityResultErrorDetails(MoveProductErrorDetails):
        code: Union[str, MoveValidationErrorCode]
        details: str
        message: str


    class azure.mgmt.billing.models.MoveProductErrorDetails(_Model):
        code: Optional[Union[str, MoveValidationErrorCode]]
        details: Optional[str]
        message: Optional[str]


    class azure.mgmt.billing.models.MoveProductRequest(_Model):
        destination_invoice_section_id: str

        @overload
        def __init__(
                self, 
                *, 
                destination_invoice_section_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.MoveValidationErrorCode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BILLING_ACCOUNT_INACTIVE = "BillingAccountInactive"
        DESTINATION_BILLING_PROFILE_INACTIVE = "DestinationBillingProfileInactive"
        DESTINATION_BILLING_PROFILE_NOT_FOUND = "DestinationBillingProfileNotFound"
        DESTINATION_BILLING_PROFILE_PAST_DUE = "DestinationBillingProfilePastDue"
        DESTINATION_INVOICE_SECTION_INACTIVE = "DestinationInvoiceSectionInactive"
        DESTINATION_INVOICE_SECTION_NOT_FOUND = "DestinationInvoiceSectionNotFound"
        INSUFFICIENT_PERMISSION_ON_DESTINATION = "InsufficientPermissionOnDestination"
        INSUFFICIENT_PERMISSION_ON_SOURCE = "InsufficientPermissionOnSource"
        INVALID_DESTINATION = "InvalidDestination"
        INVALID_SOURCE = "InvalidSource"
        MARKETPLACE_NOT_ENABLED_ON_DESTINATION = "MarketplaceNotEnabledOnDestination"
        OTHER = "Other"
        PRODUCT_INACTIVE = "ProductInactive"
        PRODUCT_NOT_FOUND = "ProductNotFound"
        PRODUCT_TYPE_NOT_SUPPORTED = "ProductTypeNotSupported"
        SOURCE_BILLING_PROFILE_PAST_DUE = "SourceBillingProfilePastDue"
        SOURCE_INVOICE_SECTION_INACTIVE = "SourceInvoiceSectionInactive"


    class azure.mgmt.billing.models.NextBillingCycleDetails(_Model):
        billing_frequency: Optional[str]


    class azure.mgmt.billing.models.Operation(_Model):
        display: Optional[OperationDisplay]
        is_data_action: Optional[bool]
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                display: Optional[OperationDisplay] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.billing.models.Participant(_Model):
        email: Optional[str]
        status: Optional[str]
        status_date: Optional[datetime]


    class azure.mgmt.billing.models.PartnerInitiateTransferProperties(_Model):
        recipient_email_id: Optional[str]
        reseller_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                recipient_email_id: Optional[str] = ..., 
                reseller_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.PartnerInitiateTransferRequest(_Model):
        properties: Optional[PartnerInitiateTransferProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[PartnerInitiateTransferProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.billing.models.PartnerTransferDetails(ProxyResource):
        id: str
        name: str
        properties: Optional[PartnerTransferProperties]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[PartnerTransferProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.billing.models.PartnerTransferProperties(_Model):
        canceled_by: Optional[str]
        detailed_transfer_status: Optional[list[DetailedTransferStatus]]
        expiration_time: Optional[datetime]
        initiator_customer_type: Optional[Union[str, InitiatorCustomerType]]
        initiator_email_id: Optional[str]
        recipient_email_id: Optional[str]
        reseller_id: Optional[str]
        reseller_name: Optional[str]
        transfer_status: Optional[Union[str, TransferStatus]]


    class azure.mgmt.billing.models.Patch(_Model):
        properties: Optional[PatchProperties]
        sku: Optional[ReservationSkuProperty]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[PatchProperties] = ..., 
                sku: Optional[ReservationSkuProperty] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.PatchProperties(_Model):
        applied_scope_properties: Optional[ReservationAppliedScopeProperties]
        applied_scope_type: Optional[Union[str, AppliedScopeType]]
        display_name: Optional[str]
        instance_flexibility: Optional[Union[str, InstanceFlexibility]]
        renew: Optional[bool]
        renew_properties: Optional[PatchPropertiesRenewProperties]
        review_date_time: Optional[datetime]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                applied_scope_properties: Optional[ReservationAppliedScopeProperties] = ..., 
                applied_scope_type: Optional[Union[str, AppliedScopeType]] = ..., 
                display_name: Optional[str] = ..., 
                instance_flexibility: Optional[Union[str, InstanceFlexibility]] = ..., 
                renew: Optional[bool] = ..., 
                renew_properties: Optional[PatchPropertiesRenewProperties] = ..., 
                review_date_time: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.billing.models.PatchPropertiesRenewProperties(_Model):
        purchase_properties: Optional[ReservationPurchaseRequest]

        @overload
        def __init__(
                self, 
                *, 
                purchase_properties: Optional[ReservationPurchaseRequest] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.Payment(_Model):
        amount: Optional[PaymentAmount]
        date: Optional[datetime]
        payment_method_family: Optional[Union[str, PaymentMethodFamily]]
        payment_method_id: Optional[str]
        payment_method_type: Optional[str]
        payment_type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                amount: Optional[PaymentAmount] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.PaymentAmount(Amount):
        currency: str
        value: float


    class azure.mgmt.billing.models.PaymentDetail(_Model):
        billing_currency_total: Optional[Price]
        due_date: Optional[date]
        extended_status_info: Optional[ExtendedStatusInfo]
        payment_date: Optional[date]
        pricing_currency_total: Optional[Price]
        status: Optional[Union[str, PaymentStatus]]

        @overload
        def __init__(
                self, 
                *, 
                billing_currency_total: Optional[Price] = ..., 
                due_date: Optional[date] = ..., 
                payment_date: Optional[date] = ..., 
                pricing_currency_total: Optional[Price] = ..., 
                status: Optional[Union[str, PaymentStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.PaymentMethod(ProxyResource):
        id: str
        name: str
        properties: Optional[PaymentMethodProperties]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[PaymentMethodProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.billing.models.PaymentMethodFamily(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CHECK_WIRE = "CheckWire"
        CREDITS = "Credits"
        CREDIT_CARD = "CreditCard"
        DIRECT_DEBIT = "DirectDebit"
        E_WALLET = "EWallet"
        NONE = "None"
        OTHER = "Other"
        TASK_ORDER = "TaskOrder"


    class azure.mgmt.billing.models.PaymentMethodLink(ProxyResource):
        id: str
        name: str
        properties: Optional[PaymentMethodLinkProperties]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[PaymentMethodLinkProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.billing.models.PaymentMethodLinkProperties(_Model):
        account_holder_name: Optional[str]
        display_name: Optional[str]
        expiration: Optional[str]
        family: Optional[Union[str, PaymentMethodFamily]]
        last_four_digits: Optional[str]
        logos: Optional[list[PaymentMethodLogo]]
        payment_method: Optional[PaymentMethodProperties]
        payment_method_id: Optional[str]
        payment_method_type: Optional[str]
        status: Optional[Union[str, PaymentMethodStatus]]

        @overload
        def __init__(
                self, 
                *, 
                payment_method: Optional[PaymentMethodProperties] = ..., 
                payment_method_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.PaymentMethodLogo(_Model):
        mime_type: Optional[str]
        url: Optional[str]


    class azure.mgmt.billing.models.PaymentMethodProperties(_Model):
        account_holder_name: Optional[str]
        display_name: Optional[str]
        expiration: Optional[str]
        family: Optional[Union[str, PaymentMethodFamily]]
        id: Optional[str]
        last_four_digits: Optional[str]
        logos: Optional[list[PaymentMethodLogo]]
        payment_method_type: Optional[str]
        status: Optional[Union[str, PaymentMethodStatus]]

        @overload
        def __init__(
                self, 
                *, 
                family: Optional[Union[str, PaymentMethodFamily]] = ..., 
                logos: Optional[list[PaymentMethodLogo]] = ..., 
                status: Optional[Union[str, PaymentMethodStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.PaymentMethodStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "active"
        INACTIVE = "inactive"


    class azure.mgmt.billing.models.PaymentOnAccount(_Model):
        amount: Optional[PaymentOnAccountAmount]
        billing_profile_display_name: Optional[str]
        billing_profile_id: Optional[str]
        date: Optional[datetime]
        invoice_id: Optional[str]
        invoice_name: Optional[str]
        payment_method_type: Optional[Union[str, PaymentMethodFamily]]

        @overload
        def __init__(
                self, 
                *, 
                amount: Optional[PaymentOnAccountAmount] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.PaymentOnAccountAmount(Amount):
        currency: str
        value: float


    class azure.mgmt.billing.models.PaymentStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELLED = "Cancelled"
        COMPLETED = "Completed"
        FAILED = "Failed"
        PENDING = "Pending"
        SCHEDULED = "Scheduled"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.billing.models.PaymentTerm(_Model):
        end_date: Optional[datetime]
        is_default: Optional[bool]
        start_date: Optional[datetime]
        term: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                end_date: Optional[datetime] = ..., 
                start_date: Optional[datetime] = ..., 
                term: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.PaymentTermsEligibilityCode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BILLING_ACCOUNT_NOT_FOUND = "BillingAccountNotFound"
        INACTIVE_BILLING_ACCOUNT = "InactiveBillingAccount"
        INELIGIBLE_BILLING_ACCOUNT_STATUS = "IneligibleBillingAccountStatus"
        INVALID_BILLING_ACCOUNT_TYPE = "InvalidBillingAccountType"
        INVALID_DATE_FORMAT = "InvalidDateFormat"
        INVALID_DATE_RANGE = "InvalidDateRange"
        INVALID_TERMS = "InvalidTerms"
        NULL_OR_EMPTY_PAYMENT_TERMS = "NullOrEmptyPaymentTerms"
        OTHER = "Other"
        OVERLAPPING_PAYMENT_TERMS = "OverlappingPaymentTerms"


    class azure.mgmt.billing.models.PaymentTermsEligibilityDetail(_Model):
        code: Optional[Union[str, PaymentTermsEligibilityCode]]
        message: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                code: Optional[Union[str, PaymentTermsEligibilityCode]] = ..., 
                message: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.PaymentTermsEligibilityResult(_Model):
        eligibility_details: Optional[list[PaymentTermsEligibilityDetail]]
        eligibility_status: Optional[Union[str, PaymentTermsEligibilityStatus]]

        @overload
        def __init__(
                self, 
                *, 
                eligibility_details: Optional[list[PaymentTermsEligibilityDetail]] = ..., 
                eligibility_status: Optional[Union[str, PaymentTermsEligibilityStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.PaymentTermsEligibilityStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INVALID = "Invalid"
        OTHER = "Other"
        VALID = "Valid"


    class azure.mgmt.billing.models.PolicySummary(_Model):
        name: Optional[str]
        policy_type: Optional[Union[str, PolicyType]]
        scope: Optional[str]
        value: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                policy_type: Optional[Union[str, PolicyType]] = ..., 
                scope: Optional[str] = ..., 
                value: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.PolicyType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        OTHER = "Other"
        SYSTEM_CONTROLLED = "SystemControlled"
        USER_CONTROLLED = "UserControlled"


    class azure.mgmt.billing.models.Price(_Model):
        amount: Optional[float]
        currency_code: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                amount: Optional[float] = ..., 
                currency_code: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.Principal(_Model):
        object_id: Optional[str]
        tenant_id: Optional[str]
        upn: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                object_id: Optional[str] = ..., 
                tenant_id: Optional[str] = ..., 
                upn: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.PrincipalType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DIRECTORY_ROLE = "DirectoryRole"
        EVERYONE = "Everyone"
        GROUP = "Group"
        NONE = "None"
        SERVICE_PRINCIPAL = "ServicePrincipal"
        UNKNOWN = "Unknown"
        USER = "User"


    class azure.mgmt.billing.models.Product(ProxyResource):
        id: str
        name: str
        properties: Optional[ProductProperties]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ProductProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.ProductDetails(_Model):
        product_id: Optional[str]
        product_type: Optional[Union[str, ProductType]]

        @overload
        def __init__(
                self, 
                *, 
                product_id: Optional[str] = ..., 
                product_type: Optional[Union[str, ProductType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.ProductPatch(ProxyResourceWithTags):
        id: str
        name: str
        properties: Optional[ProductProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ProductProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.ProductProperties(_Model):
        auto_renew: Optional[Union[str, AutoRenew]]
        availability_id: Optional[str]
        billing_frequency: Optional[str]
        billing_profile_display_name: Optional[str]
        billing_profile_id: Optional[str]
        customer_display_name: Optional[str]
        customer_id: Optional[str]
        display_name: Optional[str]
        end_date: Optional[str]
        invoice_section_display_name: Optional[str]
        invoice_section_id: Optional[str]
        last_charge: Optional[ProductPropertiesLastCharge]
        last_charge_date: Optional[str]
        product_type: Optional[str]
        product_type_id: Optional[str]
        purchase_date: Optional[str]
        quantity: Optional[int]
        reseller: Optional[ProductPropertiesReseller]
        sku_description: Optional[str]
        sku_id: Optional[str]
        status: Optional[Union[str, ProductStatus]]
        tenant_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                auto_renew: Optional[Union[str, AutoRenew]] = ..., 
                last_charge: Optional[ProductPropertiesLastCharge] = ..., 
                reseller: Optional[ProductPropertiesReseller] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.ProductPropertiesLastCharge(Amount):
        currency: str
        value: float


    class azure.mgmt.billing.models.ProductPropertiesReseller(Reseller):
        description: str
        reseller_id: str


    class azure.mgmt.billing.models.ProductStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        AUTO_RENEW = "AutoRenew"
        CANCELED = "Canceled"
        DELETED = "Deleted"
        DISABLED = "Disabled"
        EXPIRED = "Expired"
        EXPIRING = "Expiring"
        OTHER = "Other"
        PAST_DUE = "PastDue"
        SUSPENDED = "Suspended"


    class azure.mgmt.billing.models.ProductTransferStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPLETED = "Completed"
        FAILED = "Failed"
        IN_PROGRESS = "InProgress"
        NOT_STARTED = "NotStarted"


    class azure.mgmt.billing.models.ProductType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_RESERVATION = "AzureReservation"
        AZURE_SUBSCRIPTION = "AzureSubscription"
        DEPARTMENT = "Department"
        SAAS = "SAAS"
        SAVINGS_PLAN = "SavingsPlan"


    class azure.mgmt.billing.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CONFIRMED_BILLING = "ConfirmedBilling"
        CREATED = "Created"
        CREATING = "Creating"
        EXPIRED = "Expired"
        FAILED = "Failed"
        NEW = "New"
        PENDING = "Pending"
        PENDING_BILLING = "PendingBilling"
        PROVISIONING = "Provisioning"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.billing.models.ProvisioningTenantState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        BILLING_REQUEST_DECLINED = "BillingRequestDeclined"
        BILLING_REQUEST_EXPIRED = "BillingRequestExpired"
        NOT_REQUESTED = "NotRequested"
        OTHER = "Other"
        PENDING = "Pending"
        REVOKED = "Revoked"


    class azure.mgmt.billing.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.billing.models.ProxyResourceWithTags(ProxyResource):
        id: str
        name: str
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.PurchaseRequest(_Model):
        properties: Optional[PurchaseRequestProperties]
        sku: Optional[Sku]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[PurchaseRequestProperties] = ..., 
                sku: Optional[Sku] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.billing.models.PurchaseRequestProperties(_Model):
        applied_scope_properties: Optional[AppliedScopeProperties]
        applied_scope_type: Optional[Union[str, AppliedScopeType]]
        billing_plan: Optional[Union[str, BillingPlan]]
        billing_scope_id: Optional[str]
        commitment: Optional[Commitment]
        display_name: Optional[str]
        renew: Optional[bool]
        term: Optional[Union[str, SavingsPlanTerm]]

        @overload
        def __init__(
                self, 
                *, 
                applied_scope_properties: Optional[AppliedScopeProperties] = ..., 
                applied_scope_type: Optional[Union[str, AppliedScopeType]] = ..., 
                billing_plan: Optional[Union[str, BillingPlan]] = ..., 
                billing_scope_id: Optional[str] = ..., 
                commitment: Optional[Commitment] = ..., 
                display_name: Optional[str] = ..., 
                renew: Optional[bool] = ..., 
                term: Optional[Union[str, SavingsPlanTerm]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.RebillDetails(_Model):
        credit_note_document_id: Optional[str]
        invoice_document_id: Optional[str]
        rebill_details: Optional[RebillDetails]


    class azure.mgmt.billing.models.RecipientTransferDetails(ProxyResource):
        id: str
        name: str
        properties: Optional[RecipientTransferProperties]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[RecipientTransferProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.billing.models.RecipientTransferProperties(_Model):
        allowed_product_type: Optional[list[Union[str, EligibleProductType]]]
        canceled_by: Optional[str]
        customer_tenant_id: Optional[str]
        detailed_transfer_status: Optional[list[DetailedTransferStatus]]
        expiration_time: Optional[datetime]
        initiator_customer_type: Optional[Union[str, InitiatorCustomerType]]
        initiator_email_id: Optional[str]
        recipient_email_id: Optional[str]
        reseller_id: Optional[str]
        reseller_name: Optional[str]
        supported_accounts: Optional[list[Union[str, SupportedAccountType]]]
        transfer_status: Optional[Union[str, TransferStatus]]


    class azure.mgmt.billing.models.RefundDetailsSummary(_Model):
        amount_refunded: Optional[RefundDetailsSummaryAmountRefunded]
        amount_requested: Optional[RefundDetailsSummaryAmountRequested]
        approved_on: Optional[datetime]
        completed_on: Optional[datetime]
        rebill_invoice_id: Optional[str]
        refund_operation_id: Optional[str]
        refund_reason: Optional[Union[str, RefundReasonCode]]
        refund_status: Optional[Union[str, RefundStatus]]
        requested_on: Optional[datetime]
        transaction_count: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                amount_refunded: Optional[RefundDetailsSummaryAmountRefunded] = ..., 
                amount_requested: Optional[RefundDetailsSummaryAmountRequested] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.RefundDetailsSummaryAmountRefunded(Amount):
        currency: str
        value: float


    class azure.mgmt.billing.models.RefundDetailsSummaryAmountRequested(Amount):
        currency: str
        value: float


    class azure.mgmt.billing.models.RefundReasonCode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCIDENTAL_CONVERSION = "AccidentalConversion"
        ACCIDENTAL_PURCHASE = "AccidentalPurchase"
        FORGOT_TO_CANCEL = "ForgotToCancel"
        OTHER = "Other"
        UNCLEAR_DOCUMENTATION = "UnclearDocumentation"
        UNCLEAR_PRICING = "UnclearPricing"


    class azure.mgmt.billing.models.RefundStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPROVED = "Approved"
        CANCELLED = "Cancelled"
        COMPLETED = "Completed"
        DECLINED = "Declined"
        EXPIRED = "Expired"
        OTHER = "Other"
        PENDING = "Pending"


    class azure.mgmt.billing.models.RefundTransactionDetails(_Model):
        amount_refunded: Optional[RefundTransactionDetailsAmountRefunded]
        amount_requested: Optional[RefundTransactionDetailsAmountRequested]
        refund_operation_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                amount_refunded: Optional[RefundTransactionDetailsAmountRefunded] = ..., 
                amount_requested: Optional[RefundTransactionDetailsAmountRequested] = ..., 
                refund_operation_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.RefundTransactionDetailsAmountRefunded(Amount):
        currency: str
        value: float


    class azure.mgmt.billing.models.RefundTransactionDetailsAmountRequested(Amount):
        currency: str
        value: float


    class azure.mgmt.billing.models.RegistrationNumber(_Model):
        id: Optional[str]
        required: Optional[bool]
        type: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.RenewProperties(_Model):
        purchase_properties: Optional[PurchaseRequest]

        @overload
        def __init__(
                self, 
                *, 
                purchase_properties: Optional[PurchaseRequest] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.RenewPropertiesResponse(_Model):
        billing_currency_total: Optional[Price]
        pricing_currency_total: Optional[Price]
        purchase_properties: Optional[ReservationPurchaseRequest]

        @overload
        def __init__(
                self, 
                *, 
                billing_currency_total: Optional[Price] = ..., 
                pricing_currency_total: Optional[Price] = ..., 
                purchase_properties: Optional[ReservationPurchaseRequest] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.RenewalTermDetails(_Model):
        billing_frequency: Optional[str]
        product_id: Optional[str]
        product_type_id: Optional[str]
        quantity: Optional[int]
        sku_id: Optional[str]
        term_duration: Optional[str]
        term_end_date: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                quantity: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.Reseller(_Model):
        description: Optional[str]
        reseller_id: Optional[str]


    class azure.mgmt.billing.models.Reservation(ProxyResource):
        etag: Optional[int]
        id: str
        location: Optional[str]
        name: str
        properties: Optional[ReservationProperty]
        sku: Optional[ReservationSkuProperty]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[int] = ..., 
                location: Optional[str] = ..., 
                properties: Optional[ReservationProperty] = ..., 
                sku: Optional[ReservationSkuProperty] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.ReservationAppliedScopeProperties(_Model):
        display_name: Optional[str]
        management_group_id: Optional[str]
        resource_group_id: Optional[str]
        subscription_id: Optional[str]
        tenant_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                display_name: Optional[str] = ..., 
                management_group_id: Optional[str] = ..., 
                resource_group_id: Optional[str] = ..., 
                subscription_id: Optional[str] = ..., 
                tenant_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.ReservationBillingPlan(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MONTHLY = "Monthly"
        UPFRONT = "Upfront"


    class azure.mgmt.billing.models.ReservationExtendedStatusInfo(_Model):
        message: Optional[str]
        properties: Optional[ExtendedStatusDefinitionProperties]
        status_code: Optional[Union[str, ReservationStatusCode]]

        @overload
        def __init__(
                self, 
                *, 
                message: Optional[str] = ..., 
                properties: Optional[ExtendedStatusDefinitionProperties] = ..., 
                status_code: Optional[Union[str, ReservationStatusCode]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.ReservationMergeProperties(_Model):
        merge_destination: Optional[str]
        merge_sources: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                merge_destination: Optional[str] = ..., 
                merge_sources: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.ReservationOrder(ProxyResource):
        etag: Optional[int]
        id: str
        name: str
        properties: Optional[ReservationOrderProperty]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[int] = ..., 
                properties: Optional[ReservationOrderProperty] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.billing.models.ReservationOrderBillingPlanInformation(_Model):
        next_payment_due_date: Optional[date]
        pricing_currency_total: Optional[Price]
        start_date: Optional[date]
        transactions: Optional[list[ReservationPaymentDetail]]

        @overload
        def __init__(
                self, 
                *, 
                next_payment_due_date: Optional[date] = ..., 
                pricing_currency_total: Optional[Price] = ..., 
                start_date: Optional[date] = ..., 
                transactions: Optional[list[ReservationPaymentDetail]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.ReservationOrderProperty(_Model):
        benefit_start_time: Optional[datetime]
        billing_account_id: Optional[str]
        billing_plan: Optional[Union[str, ReservationBillingPlan]]
        billing_profile_id: Optional[str]
        created_date_time: Optional[datetime]
        customer_id: Optional[str]
        display_name: Optional[str]
        enrollment_id: Optional[str]
        expiry_date: Optional[date]
        expiry_date_time: Optional[datetime]
        extended_status_info: Optional[ReservationExtendedStatusInfo]
        original_quantity: Optional[int]
        plan_information: Optional[ReservationOrderBillingPlanInformation]
        product_code: Optional[str]
        provisioning_state: Optional[str]
        request_date_time: Optional[datetime]
        reservations: Optional[list[Reservation]]
        review_date_time: Optional[datetime]
        term: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                benefit_start_time: Optional[datetime] = ..., 
                billing_account_id: Optional[str] = ..., 
                billing_plan: Optional[Union[str, ReservationBillingPlan]] = ..., 
                billing_profile_id: Optional[str] = ..., 
                created_date_time: Optional[datetime] = ..., 
                customer_id: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                enrollment_id: Optional[str] = ..., 
                expiry_date: Optional[date] = ..., 
                expiry_date_time: Optional[datetime] = ..., 
                extended_status_info: Optional[ReservationExtendedStatusInfo] = ..., 
                original_quantity: Optional[int] = ..., 
                plan_information: Optional[ReservationOrderBillingPlanInformation] = ..., 
                product_code: Optional[str] = ..., 
                request_date_time: Optional[datetime] = ..., 
                reservations: Optional[list[Reservation]] = ..., 
                review_date_time: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.ReservationPaymentDetail(_Model):
        billing_account: Optional[str]
        billing_currency_total: Optional[Price]
        due_date: Optional[date]
        extended_status_info: Optional[ReservationExtendedStatusInfo]
        payment_date: Optional[date]
        pricing_currency_total: Optional[Price]
        status: Optional[Union[str, PaymentStatus]]

        @overload
        def __init__(
                self, 
                *, 
                billing_account: Optional[str] = ..., 
                billing_currency_total: Optional[Price] = ..., 
                due_date: Optional[date] = ..., 
                extended_status_info: Optional[ReservationExtendedStatusInfo] = ..., 
                payment_date: Optional[date] = ..., 
                pricing_currency_total: Optional[Price] = ..., 
                status: Optional[Union[str, PaymentStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.ReservationProperty(_Model):
        applied_scope_properties: Optional[ReservationAppliedScopeProperties]
        applied_scope_type: Optional[str]
        applied_scopes: Optional[list[str]]
        archived: Optional[bool]
        benefit_start_time: Optional[datetime]
        billing_plan: Optional[Union[str, ReservationBillingPlan]]
        billing_scope_id: Optional[str]
        capabilities: Optional[str]
        display_name: Optional[str]
        display_provisioning_state: Optional[str]
        effective_date_time: Optional[datetime]
        expiry_date: Optional[str]
        expiry_date_time: Optional[datetime]
        extended_status_info: Optional[ReservationExtendedStatusInfo]
        instance_flexibility: Optional[Union[str, InstanceFlexibility]]
        last_updated_date_time: Optional[datetime]
        merge_properties: Optional[ReservationMergeProperties]
        product_code: Optional[str]
        provisioning_state: Optional[str]
        provisioning_sub_state: Optional[str]
        purchase_date: Optional[date]
        purchase_date_time: Optional[datetime]
        quantity: Optional[float]
        renew: Optional[bool]
        renew_destination: Optional[str]
        renew_properties: Optional[RenewPropertiesResponse]
        renew_source: Optional[str]
        reserved_resource_type: Optional[str]
        review_date_time: Optional[datetime]
        sku_description: Optional[str]
        split_properties: Optional[ReservationSplitProperties]
        swap_properties: Optional[ReservationSwapProperties]
        term: Optional[str]
        user_friendly_applied_scope_type: Optional[str]
        user_friendly_renew_state: Optional[str]
        utilization: Optional[ReservationPropertyUtilization]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                applied_scope_properties: Optional[ReservationAppliedScopeProperties] = ..., 
                applied_scopes: Optional[list[str]] = ..., 
                archived: Optional[bool] = ..., 
                benefit_start_time: Optional[datetime] = ..., 
                billing_plan: Optional[Union[str, ReservationBillingPlan]] = ..., 
                capabilities: Optional[str] = ..., 
                expiry_date_time: Optional[datetime] = ..., 
                extended_status_info: Optional[ReservationExtendedStatusInfo] = ..., 
                instance_flexibility: Optional[Union[str, InstanceFlexibility]] = ..., 
                merge_properties: Optional[ReservationMergeProperties] = ..., 
                product_code: Optional[str] = ..., 
                purchase_date: Optional[date] = ..., 
                purchase_date_time: Optional[datetime] = ..., 
                renew_destination: Optional[str] = ..., 
                renew_properties: Optional[RenewPropertiesResponse] = ..., 
                review_date_time: Optional[datetime] = ..., 
                split_properties: Optional[ReservationSplitProperties] = ..., 
                swap_properties: Optional[ReservationSwapProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.billing.models.ReservationPropertyUtilization(_Model):
        aggregates: Optional[list[ReservationUtilizationAggregates]]
        trend: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                aggregates: Optional[list[ReservationUtilizationAggregates]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.ReservationPurchaseRequest(_Model):
        location: Optional[str]
        properties: Optional[ReservationPurchaseRequestProperties]
        sku: Optional[SkuName]

        @overload
        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                properties: Optional[ReservationPurchaseRequestProperties] = ..., 
                sku: Optional[SkuName] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.ReservationPurchaseRequestProperties(_Model):
        applied_scope_properties: Optional[ReservationAppliedScopeProperties]
        applied_scope_type: Optional[Union[str, AppliedScopeType]]
        applied_scopes: Optional[list[str]]
        billing_plan: Optional[Union[str, ReservationBillingPlan]]
        billing_scope_id: Optional[str]
        display_name: Optional[str]
        instance_flexibility: Optional[Union[str, InstanceFlexibility]]
        quantity: Optional[int]
        renew: Optional[bool]
        reserved_resource_properties: Optional[ReservationPurchaseRequestPropertiesReservedResourceProperties]
        reserved_resource_type: Optional[str]
        review_date_time: Optional[datetime]
        term: Optional[str]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                applied_scope_properties: Optional[ReservationAppliedScopeProperties] = ..., 
                applied_scope_type: Optional[Union[str, AppliedScopeType]] = ..., 
                applied_scopes: Optional[list[str]] = ..., 
                billing_plan: Optional[Union[str, ReservationBillingPlan]] = ..., 
                display_name: Optional[str] = ..., 
                instance_flexibility: Optional[Union[str, InstanceFlexibility]] = ..., 
                quantity: Optional[int] = ..., 
                renew: Optional[bool] = ..., 
                reserved_resource_properties: Optional[ReservationPurchaseRequestPropertiesReservedResourceProperties] = ..., 
                review_date_time: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.billing.models.ReservationPurchaseRequestPropertiesReservedResourceProperties(_Model):
        instance_flexibility: Optional[Union[str, InstanceFlexibility]]

        @overload
        def __init__(
                self, 
                *, 
                instance_flexibility: Optional[Union[str, InstanceFlexibility]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.ReservationPurchasesPolicy(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALLOWED = "Allowed"
        DISABLED = "Disabled"
        NOT_ALLOWED = "NotAllowed"
        OTHER = "Other"


    class azure.mgmt.billing.models.ReservationSkuProperty(_Model):
        name: Optional[str]


    class azure.mgmt.billing.models.ReservationSplitProperties(_Model):
        split_destinations: Optional[list[str]]
        split_source: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                split_destinations: Optional[list[str]] = ..., 
                split_source: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.ReservationStatusCode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        CAPACITY_ERROR = "CapacityError"
        CAPACITY_RESTRICTED = "CapacityRestricted"
        CREDIT_LINE_CHECK_FAILED = "CreditLineCheckFailed"
        EXCHANGED = "Exchanged"
        EXPIRED = "Expired"
        MERGED = "Merged"
        NONE = "None"
        NO_BENEFIT = "NoBenefit"
        NO_BENEFIT_DUE_TO_SUBSCRIPTION_DELETION = "NoBenefitDueToSubscriptionDeletion"
        NO_BENEFIT_DUE_TO_SUBSCRIPTION_TRANSFER = "NoBenefitDueToSubscriptionTransfer"
        PAYMENT_INSTRUMENT_ERROR = "PaymentInstrumentError"
        PENDING = "Pending"
        PROCESSING = "Processing"
        PURCHASE_ERROR = "PurchaseError"
        RISK_CHECK_FAILED = "RiskCheckFailed"
        SPLIT = "Split"
        SUCCEEDED = "Succeeded"
        UNKNOWN_ERROR = "UnknownError"
        WARNING = "Warning"


    class azure.mgmt.billing.models.ReservationSummary(_Model):
        cancelled_count: Optional[float]
        expired_count: Optional[float]
        expiring_count: Optional[float]
        failed_count: Optional[float]
        no_benefit_count: Optional[float]
        pending_count: Optional[float]
        processing_count: Optional[float]
        succeeded_count: Optional[float]
        warning_count: Optional[float]


    class azure.mgmt.billing.models.ReservationSwapProperties(_Model):
        swap_destination: Optional[str]
        swap_source: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                swap_destination: Optional[str] = ..., 
                swap_source: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.ReservationUtilizationAggregates(_Model):
        grain: Optional[float]
        grain_unit: Optional[str]
        value: Optional[float]
        value_unit: Optional[str]


    class azure.mgmt.billing.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.billing.models.SavingsPlanModel(ProxyResource):
        id: str
        name: str
        properties: Optional[SavingsPlanModelProperties]
        sku: Sku
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SavingsPlanModelProperties] = ..., 
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


    class azure.mgmt.billing.models.SavingsPlanModelProperties(_Model):
        applied_scope_properties: Optional[AppliedScopeProperties]
        applied_scope_type: Optional[Union[str, AppliedScopeType]]
        benefit_start_time: Optional[datetime]
        billing_account_id: Optional[str]
        billing_plan: Optional[Union[str, BillingPlan]]
        billing_profile_id: Optional[str]
        billing_scope_id: Optional[str]
        commitment: Optional[Commitment]
        customer_id: Optional[str]
        display_name: Optional[str]
        display_provisioning_state: Optional[str]
        effective_date_time: Optional[datetime]
        expiry_date_time: Optional[datetime]
        extended_status_info: Optional[ExtendedStatusInfo]
        product_code: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        purchase_date_time: Optional[datetime]
        renew: Optional[bool]
        renew_destination: Optional[str]
        renew_properties: Optional[RenewProperties]
        renew_source: Optional[str]
        term: Optional[Union[str, SavingsPlanTerm]]
        user_friendly_applied_scope_type: Optional[str]
        utilization: Optional[Utilization]

        @overload
        def __init__(
                self, 
                *, 
                applied_scope_properties: Optional[AppliedScopeProperties] = ..., 
                applied_scope_type: Optional[Union[str, AppliedScopeType]] = ..., 
                billing_plan: Optional[Union[str, BillingPlan]] = ..., 
                billing_scope_id: Optional[str] = ..., 
                commitment: Optional[Commitment] = ..., 
                display_name: Optional[str] = ..., 
                product_code: Optional[str] = ..., 
                renew: Optional[bool] = ..., 
                renew_destination: Optional[str] = ..., 
                renew_properties: Optional[RenewProperties] = ..., 
                renew_source: Optional[str] = ..., 
                term: Optional[Union[str, SavingsPlanTerm]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.SavingsPlanOrderModel(ProxyResource):
        id: str
        name: str
        properties: Optional[SavingsPlanOrderModelProperties]
        sku: Sku
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SavingsPlanOrderModelProperties] = ..., 
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


    class azure.mgmt.billing.models.SavingsPlanOrderModelProperties(_Model):
        benefit_start_time: Optional[datetime]
        billing_account_id: Optional[str]
        billing_plan: Optional[Union[str, BillingPlan]]
        billing_profile_id: Optional[str]
        billing_scope_id: Optional[str]
        customer_id: Optional[str]
        display_name: Optional[str]
        expiry_date_time: Optional[datetime]
        extended_status_info: Optional[ExtendedStatusInfo]
        plan_information: Optional[BillingPlanInformation]
        product_code: Optional[str]
        provisioning_state: Optional[str]
        savings_plans: Optional[list[str]]
        term: Optional[Union[str, SavingsPlanTerm]]

        @overload
        def __init__(
                self, 
                *, 
                billing_plan: Optional[Union[str, BillingPlan]] = ..., 
                billing_scope_id: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                plan_information: Optional[BillingPlanInformation] = ..., 
                product_code: Optional[str] = ..., 
                savings_plans: Optional[list[str]] = ..., 
                term: Optional[Union[str, SavingsPlanTerm]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.SavingsPlanPurchasesPolicy(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALLOWED = "Allowed"
        DISABLED = "Disabled"
        NOT_ALLOWED = "NotAllowed"
        OTHER = "Other"


    class azure.mgmt.billing.models.SavingsPlanSummaryCount(_Model):
        cancelled_count: Optional[float]
        expired_count: Optional[float]
        expiring_count: Optional[float]
        failed_count: Optional[float]
        no_benefit_count: Optional[float]
        pending_count: Optional[float]
        processing_count: Optional[float]
        succeeded_count: Optional[float]
        warning_count: Optional[float]


    class azure.mgmt.billing.models.SavingsPlanTerm(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        P1_Y = "P1Y"
        P3_Y = "P3Y"
        P5_Y = "P5Y"


    class azure.mgmt.billing.models.SavingsPlanUpdateRequest(_Model):
        properties: Optional[SavingsPlanUpdateRequestProperties]
        sku: Optional[Sku]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SavingsPlanUpdateRequestProperties] = ..., 
                sku: Optional[Sku] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.SavingsPlanUpdateRequestProperties(_Model):
        applied_scope_properties: Optional[AppliedScopeProperties]
        applied_scope_type: Optional[Union[str, AppliedScopeType]]
        display_name: Optional[str]
        renew: Optional[bool]
        renew_properties: Optional[RenewProperties]

        @overload
        def __init__(
                self, 
                *, 
                applied_scope_properties: Optional[AppliedScopeProperties] = ..., 
                applied_scope_type: Optional[Union[str, AppliedScopeType]] = ..., 
                display_name: Optional[str] = ..., 
                renew: Optional[bool] = ..., 
                renew_properties: Optional[RenewProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.SavingsPlanUpdateValidateRequest(_Model):
        benefits: Optional[list[SavingsPlanUpdateRequestProperties]]

        @overload
        def __init__(
                self, 
                *, 
                benefits: Optional[list[SavingsPlanUpdateRequestProperties]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.SavingsPlanValidResponseProperty(_Model):
        reason: Optional[str]
        reason_code: Optional[str]
        valid: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                reason: Optional[str] = ..., 
                reason_code: Optional[str] = ..., 
                valid: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.SavingsPlanValidateResponse(_Model):
        benefits: Optional[list[SavingsPlanValidResponseProperty]]
        next_link: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                benefits: Optional[list[SavingsPlanValidResponseProperty]] = ..., 
                next_link: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.ServiceDefinedResourceName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEFAULT = "default"


    class azure.mgmt.billing.models.Sku(_Model):
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.SkuName(_Model):
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.SpecialTaxationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INVOICE_LEVEL = "InvoiceLevel"
        SUBTOTAL_LEVEL = "SubtotalLevel"


    class azure.mgmt.billing.models.SpendingLimit(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        OFF = "Off"
        ON = "On"


    class azure.mgmt.billing.models.SpendingLimitDetails(_Model):
        amount: Optional[float]
        currency: Optional[str]
        end_date: Optional[datetime]
        start_date: Optional[datetime]
        status: Optional[Union[str, SpendingLimitStatus]]
        type: Optional[Union[str, SpendingLimitType]]

        @overload
        def __init__(
                self, 
                *, 
                amount: Optional[float] = ..., 
                currency: Optional[str] = ..., 
                end_date: Optional[datetime] = ..., 
                start_date: Optional[datetime] = ..., 
                status: Optional[Union[str, SpendingLimitStatus]] = ..., 
                type: Optional[Union[str, SpendingLimitType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.SpendingLimitStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        EXPIRED = "Expired"
        LIMIT_REACHED = "LimitReached"
        LIMIT_REMOVED = "LimitRemoved"
        NONE = "None"
        OTHER = "Other"


    class azure.mgmt.billing.models.SpendingLimitType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACADEMIC_SPONSORSHIP = "AcademicSponsorship"
        AZURE_CONSUMPTION_CREDIT = "AzureConsumptionCredit"
        AZURE_FOR_STUDENTS = "AzureForStudents"
        AZURE_FOR_STUDENTS_STARTER = "AzureForStudentsStarter"
        AZURE_PASS_SPONSORSHIP = "AzurePassSponsorship"
        FREE_ACCOUNT = "FreeAccount"
        MPN_SPONSORSHIP = "MpnSponsorship"
        MSDN = "MSDN"
        NONE = "None"
        NON_PROFIT_SPONSORSHIP = "NonProfitSponsorship"
        OTHER = "Other"
        SANDBOX = "Sandbox"
        SPONSORSHIP = "Sponsorship"
        STARTUP_SPONSORSHIP = "StartupSponsorship"
        VISUAL_STUDIO = "VisualStudio"


    class azure.mgmt.billing.models.SubscriptionBillingType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BENEFIT = "Benefit"
        FREE = "Free"
        NONE = "None"
        PAID = "Paid"
        PRE_PAID = "PrePaid"


    class azure.mgmt.billing.models.SubscriptionEnrollmentAccountStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        CANCELLED = "Cancelled"
        DELETED = "Deleted"
        EXPIRED = "Expired"
        INACTIVE = "Inactive"
        TRANSFERRED_OUT = "TransferredOut"
        TRANSFERRING = "Transferring"


    class azure.mgmt.billing.models.SubscriptionEnrollmentDetails(_Model):
        department_display_name: Optional[str]
        department_id: Optional[str]
        enrollment_account_display_name: Optional[str]
        enrollment_account_id: Optional[str]
        enrollment_account_status: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                department_display_name: Optional[str] = ..., 
                department_id: Optional[str] = ..., 
                enrollment_account_display_name: Optional[str] = ..., 
                enrollment_account_id: Optional[str] = ..., 
                enrollment_account_status: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.SubscriptionPolicy(ProxyResource):
        id: str
        name: str
        properties: Optional[SubscriptionPolicyProperties]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SubscriptionPolicyProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.SubscriptionPolicyProperties(_Model):
        policies: Optional[list[PolicySummary]]
        provisioning_state: Optional[Union[str, ProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                policies: Optional[list[PolicySummary]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.SubscriptionStatusReason(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELLED = "Cancelled"
        EXPIRED = "Expired"
        NONE = "None"
        OTHER = "Other"
        PAST_DUE = "PastDue"
        POLICY_VIOLATION = "PolicyViolation"
        SPENDING_LIMIT_REACHED = "SpendingLimitReached"
        SUSPICIOUS_ACTIVITY = "SuspiciousActivity"
        TRANSFERRED = "Transferred"


    class azure.mgmt.billing.models.SubscriptionTransferValidationErrorCode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCOUNT_IS_LOCKED = "AccountIsLocked"
        ASSET_HAS_CAP = "AssetHasCap"
        ASSET_NOT_ACTIVE = "AssetNotActive"
        BILLING_ACCOUNT_INACTIVE = "BillingAccountInactive"
        BILLING_PROFILE_PAST_DUE = "BillingProfilePastDue"
        CROSS_BILLING_ACCOUNT_NOT_ALLOWED = "CrossBillingAccountNotAllowed"
        DESTINATION_BILLING_PROFILE_INACTIVE = "DestinationBillingProfileInactive"
        DESTINATION_BILLING_PROFILE_NOT_FOUND = "DestinationBillingProfileNotFound"
        DESTINATION_BILLING_PROFILE_PAST_DUE = "DestinationBillingProfilePastDue"
        DESTINATION_INVOICE_SECTION_INACTIVE = "DestinationInvoiceSectionInactive"
        DESTINATION_INVOICE_SECTION_NOT_FOUND = "DestinationInvoiceSectionNotFound"
        INSUFFICIENT_PERMISSION_ON_DESTINATION = "InsufficientPermissionOnDestination"
        INSUFFICIENT_PERMISSION_ON_SOURCE = "InsufficientPermissionOnSource"
        INVALID_DESTINATION = "InvalidDestination"
        INVALID_SOURCE = "InvalidSource"
        INVOICE_SECTION_IS_RESTRICTED = "InvoiceSectionIsRestricted"
        MARKETPLACE_NOT_ENABLED_ON_DESTINATION = "MarketplaceNotEnabledOnDestination"
        NONE = "None"
        NO_ACTIVE_AZURE_PLAN = "NoActiveAzurePlan"
        OTHER = "Other"
        PRODUCT_INACTIVE = "ProductInactive"
        PRODUCT_NOT_FOUND = "ProductNotFound"
        PRODUCT_TYPE_NOT_SUPPORTED = "ProductTypeNotSupported"
        SOURCE_BILLING_PROFILE_PAST_DUE = "SourceBillingProfilePastDue"
        SOURCE_INVOICE_SECTION_INACTIVE = "SourceInvoiceSectionInactive"
        SUBSCRIPTION_HAS_RESERVATIONS = "SubscriptionHasReservations"
        SUBSCRIPTION_NOT_ACTIVE = "SubscriptionNotActive"
        SUBSCRIPTION_TYPE_NOT_SUPPORTED = "SubscriptionTypeNotSupported"


    class azure.mgmt.billing.models.SubscriptionWorkloadType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEV_TEST = "DevTest"
        INTERNAL = "Internal"
        NONE = "None"
        PRODUCTION = "Production"


    class azure.mgmt.billing.models.SupportLevel(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEVELOPER = "Developer"
        OTHER = "Other"
        PRO_DIRECT = "Pro-Direct"
        STANDARD = "Standard"


    class azure.mgmt.billing.models.SupportedAccountType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ENTERPRISE = "Enterprise"
        INDIVIDUAL = "Individual"
        NONE = "None"
        PARTNER = "Partner"


    class azure.mgmt.billing.models.SystemData(_Model):
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


    class azure.mgmt.billing.models.SystemOverrides(_Model):
        cancellation: Optional[Union[str, Cancellation]]
        cancellation_allowed_end_date: Optional[datetime]


    class azure.mgmt.billing.models.TaxIdentifier(_Model):
        country: Optional[str]
        id: Optional[str]
        scope: Optional[str]
        status: Optional[Union[str, TaxIdentifierStatus]]
        type: Optional[Union[str, TaxIdentifierType]]

        @overload
        def __init__(
                self, 
                *, 
                country: Optional[str] = ..., 
                id: Optional[str] = ..., 
                scope: Optional[str] = ..., 
                status: Optional[Union[str, TaxIdentifierStatus]] = ..., 
                type: Optional[Union[str, TaxIdentifierType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.TaxIdentifierStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INVALID = "Invalid"
        OTHER = "Other"
        VALID = "Valid"


    class azure.mgmt.billing.models.TaxIdentifierType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BRAZIL_CCM_ID = "BrazilCcmId"
        BRAZIL_CNPJ_ID = "BrazilCnpjId"
        BRAZIL_CPF_ID = "BrazilCpfId"
        CANADIAN_FEDERAL_EXEMPT = "CanadianFederalExempt"
        CANADIAN_PROVINCE_EXEMPT = "CanadianProvinceExempt"
        EXTERNAL_TAXATION = "ExternalTaxation"
        INDIA_FEDERAL_SERVICE_TAX_ID = "IndiaFederalServiceTaxId"
        INDIA_FEDERAL_TAN_ID = "IndiaFederalTanId"
        INDIA_PAN_ID = "IndiaPanId"
        INDIA_STATE_CST_ID = "IndiaStateCstId"
        INDIA_STATE_GST_IN_ID = "IndiaStateGstINId"
        INDIA_STATE_VAT_ID = "IndiaStateVatId"
        INTL_EXEMPT = "IntlExempt"
        LOVE_CODE = "LoveCode"
        MOBILE_BAR_CODE = "MobileBarCode"
        NATIONAL_IDENTIFICATION_NUMBER = "NationalIdentificationNumber"
        OTHER = "Other"
        PUBLIC_SECTOR_ID = "PublicSectorId"
        US_EXEMPT = "USExempt"
        VAT_ID = "VatId"


    class azure.mgmt.billing.models.Transaction(ProxyResourceWithTags):
        id: str
        name: str
        properties: Optional[TransactionProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[TransactionProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.TransactionKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALL = "All"
        OTHER = "Other"
        RESERVATION = "Reservation"


    class azure.mgmt.billing.models.TransactionProperties(_Model):
        azure_credit_applied: Optional[TransactionPropertiesAzureCreditApplied]
        azure_plan: Optional[str]
        billing_currency: Optional[str]
        billing_profile_display_name: Optional[Any]
        billing_profile_id: Optional[str]
        consumption_commitment_decremented: Optional[TransactionPropertiesConsumptionCommitmentDecremented]
        credit_type: Optional[Union[str, CreditType]]
        customer_display_name: Optional[str]
        customer_id: Optional[str]
        date: Optional[datetime]
        discount: Optional[float]
        effective_price: Optional[TransactionPropertiesEffectivePrice]
        exchange_rate: Optional[float]
        invoice: Optional[str]
        invoice_id: Optional[str]
        invoice_section_display_name: Optional[str]
        invoice_section_id: Optional[str]
        is_third_party: Optional[bool]
        kind: Optional[Union[str, TransactionKind]]
        market_price: Optional[TransactionPropertiesMarketPrice]
        part_number: Optional[str]
        pricing_currency: Optional[str]
        product_description: Optional[str]
        product_family: Optional[str]
        product_type: Optional[str]
        product_type_id: Optional[str]
        quantity: Optional[int]
        reason_code: Optional[str]
        refund_transaction_details: Optional[TransactionPropertiesRefundTransactionDetails]
        service_period_end_date: Optional[datetime]
        service_period_start_date: Optional[datetime]
        special_taxation_type: Optional[Union[str, SpecialTaxationType]]
        sub_total: Optional[TransactionPropertiesSubTotal]
        tax: Optional[TransactionPropertiesTax]
        transaction_amount: Optional[TransactionPropertiesTransactionAmount]
        transaction_type: Optional[str]
        unit_of_measure: Optional[str]
        unit_type: Optional[str]
        units: Optional[float]

        @overload
        def __init__(
                self, 
                *, 
                azure_credit_applied: Optional[TransactionPropertiesAzureCreditApplied] = ..., 
                azure_plan: Optional[str] = ..., 
                billing_currency: Optional[str] = ..., 
                billing_profile_display_name: Optional[Any] = ..., 
                billing_profile_id: Optional[str] = ..., 
                consumption_commitment_decremented: Optional[TransactionPropertiesConsumptionCommitmentDecremented] = ..., 
                credit_type: Optional[Union[str, CreditType]] = ..., 
                customer_display_name: Optional[str] = ..., 
                customer_id: Optional[str] = ..., 
                date: Optional[datetime] = ..., 
                discount: Optional[float] = ..., 
                effective_price: Optional[TransactionPropertiesEffectivePrice] = ..., 
                exchange_rate: Optional[float] = ..., 
                invoice: Optional[str] = ..., 
                invoice_id: Optional[str] = ..., 
                invoice_section_display_name: Optional[str] = ..., 
                invoice_section_id: Optional[str] = ..., 
                is_third_party: Optional[bool] = ..., 
                kind: Optional[Union[str, TransactionKind]] = ..., 
                market_price: Optional[TransactionPropertiesMarketPrice] = ..., 
                part_number: Optional[str] = ..., 
                pricing_currency: Optional[str] = ..., 
                product_description: Optional[str] = ..., 
                product_family: Optional[str] = ..., 
                product_type: Optional[str] = ..., 
                product_type_id: Optional[str] = ..., 
                quantity: Optional[int] = ..., 
                reason_code: Optional[str] = ..., 
                refund_transaction_details: Optional[TransactionPropertiesRefundTransactionDetails] = ..., 
                service_period_end_date: Optional[datetime] = ..., 
                service_period_start_date: Optional[datetime] = ..., 
                special_taxation_type: Optional[Union[str, SpecialTaxationType]] = ..., 
                sub_total: Optional[TransactionPropertiesSubTotal] = ..., 
                tax: Optional[TransactionPropertiesTax] = ..., 
                transaction_amount: Optional[TransactionPropertiesTransactionAmount] = ..., 
                transaction_type: Optional[str] = ..., 
                unit_of_measure: Optional[str] = ..., 
                unit_type: Optional[str] = ..., 
                units: Optional[float] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.TransactionPropertiesAzureCreditApplied(Amount):
        currency: str
        value: float


    class azure.mgmt.billing.models.TransactionPropertiesConsumptionCommitmentDecremented(Amount):
        currency: str
        value: float


    class azure.mgmt.billing.models.TransactionPropertiesEffectivePrice(Amount):
        currency: str
        value: float


    class azure.mgmt.billing.models.TransactionPropertiesMarketPrice(Amount):
        currency: str
        value: float


    class azure.mgmt.billing.models.TransactionPropertiesRefundTransactionDetails(RefundTransactionDetails):
        amount_refunded: RefundTransactionDetailsAmountRefunded
        amount_requested: RefundTransactionDetailsAmountRequested
        refund_operation_id: str

        @overload
        def __init__(
                self, 
                *, 
                amount_refunded: Optional[RefundTransactionDetailsAmountRefunded] = ..., 
                amount_requested: Optional[RefundTransactionDetailsAmountRequested] = ..., 
                refund_operation_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.TransactionPropertiesSubTotal(Amount):
        currency: str
        value: float


    class azure.mgmt.billing.models.TransactionPropertiesTax(Amount):
        currency: str
        value: float


    class azure.mgmt.billing.models.TransactionPropertiesTransactionAmount(Amount):
        currency: str
        value: float


    class azure.mgmt.billing.models.TransactionSummary(_Model):
        azure_credit_applied: Optional[float]
        billing_currency: Optional[str]
        consumption_commitment_decremented: Optional[float]
        sub_total: Optional[float]
        tax: Optional[float]
        total: Optional[float]


    class azure.mgmt.billing.models.TransactionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BILLED = "Billed"
        OTHER = "Other"
        UNBILLED = "Unbilled"


    class azure.mgmt.billing.models.TransferDetails(ProxyResource):
        id: str
        name: str
        properties: Optional[TransferProperties]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[TransferProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.billing.models.TransferError(_Model):
        code: Optional[str]
        message: Optional[str]


    class azure.mgmt.billing.models.TransferProperties(_Model):
        canceled_by: Optional[str]
        detailed_transfer_status: Optional[list[DetailedTransferStatus]]
        expiration_time: Optional[datetime]
        initiator_email_id: Optional[str]
        recipient_email_id: Optional[str]
        transfer_status: Optional[Union[str, TransferStatus]]


    class azure.mgmt.billing.models.TransferStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        COMPLETED = "Completed"
        COMPLETED_WITH_ERRORS = "CompletedWithErrors"
        DECLINED = "Declined"
        EXPIRED = "Expired"
        FAILED = "Failed"
        IN_PROGRESS = "InProgress"
        PENDING = "Pending"


    class azure.mgmt.billing.models.TransitionDetails(_Model):
        anniversary_day: Optional[int]
        transition_date: Optional[datetime]


    class azure.mgmt.billing.models.Utilization(_Model):
        aggregates: Optional[list[UtilizationAggregates]]
        trend: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                aggregates: Optional[list[UtilizationAggregates]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.UtilizationAggregates(_Model):
        grain: Optional[float]
        grain_unit: Optional[str]
        value: Optional[float]
        value_unit: Optional[str]


    class azure.mgmt.billing.models.ValidateTransferListResponse(_Model):
        value: Optional[list[ValidateTransferResponse]]


    class azure.mgmt.billing.models.ValidateTransferResponse(_Model):
        properties: Optional[ValidateTransferResponseProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ValidateTransferResponseProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.billing.models.ValidateTransferResponseProperties(_Model):
        product_id: Optional[str]
        results: Optional[list[ValidationResultProperties]]
        status: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                results: Optional[list[ValidationResultProperties]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billing.models.ValidationResultProperties(_Model):
        code: Optional[str]
        level: Optional[str]
        message: Optional[str]


    class azure.mgmt.billing.models.ViewChargesPolicy(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALLOWED = "Allowed"
        NOT_ALLOWED = "NotAllowed"
        OTHER = "Other"


namespace azure.mgmt.billing.operations

    class azure.mgmt.billing.operations.AddressOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def validate(
                self, 
                parameters: AddressDetails, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AddressValidationResponse: ...

        @overload
        def validate(
                self, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AddressValidationResponse: ...

        @overload
        def validate(
                self, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AddressValidationResponse: ...


    class azure.mgmt.billing.operations.AgreementsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                billing_account_name: str, 
                agreement_name: str, 
                **kwargs: Any
            ) -> Agreement: ...

        @distributed_trace
        def list_by_billing_account(
                self, 
                billing_account_name: str, 
                *, 
                expand: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Agreement]: ...


    class azure.mgmt.billing.operations.AssociatedTenantsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                billing_account_name: str, 
                associated_tenant_name: str, 
                parameters: AssociatedTenant, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AssociatedTenant]: ...

        @overload
        def begin_create_or_update(
                self, 
                billing_account_name: str, 
                associated_tenant_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AssociatedTenant]: ...

        @overload
        def begin_create_or_update(
                self, 
                billing_account_name: str, 
                associated_tenant_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AssociatedTenant]: ...

        @distributed_trace
        def begin_delete(
                self, 
                billing_account_name: str, 
                associated_tenant_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                billing_account_name: str, 
                associated_tenant_name: str, 
                **kwargs: Any
            ) -> AssociatedTenant: ...

        @distributed_trace
        def list_by_billing_account(
                self, 
                billing_account_name: str, 
                *, 
                count: Optional[bool] = ..., 
                filter: Optional[str] = ..., 
                include_revoked: bool = False, 
                order_by: Optional[str] = ..., 
                search: Optional[str] = ..., 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[AssociatedTenant]: ...


    class azure.mgmt.billing.operations.AvailableBalancesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get_by_billing_account(
                self, 
                billing_account_name: str, 
                **kwargs: Any
            ) -> AvailableBalance: ...

        @distributed_trace
        def get_by_billing_profile(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                **kwargs: Any
            ) -> AvailableBalance: ...


    class azure.mgmt.billing.operations.BillingAccountsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_add_payment_terms(
                self, 
                billing_account_name: str, 
                parameters: List[PaymentTerm], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BillingAccount]: ...

        @overload
        def begin_add_payment_terms(
                self, 
                billing_account_name: str, 
                parameters: List[JSON], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BillingAccount]: ...

        @overload
        def begin_add_payment_terms(
                self, 
                billing_account_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BillingAccount]: ...

        @distributed_trace
        def begin_cancel_payment_terms(
                self, 
                billing_account_name: str, 
                parameters: datetime, 
                **kwargs: Any
            ) -> LROPoller[BillingAccount]: ...

        @overload
        def begin_update(
                self, 
                billing_account_name: str, 
                parameters: BillingAccountPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BillingAccount]: ...

        @overload
        def begin_update(
                self, 
                billing_account_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BillingAccount]: ...

        @overload
        def begin_update(
                self, 
                billing_account_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BillingAccount]: ...

        @distributed_trace
        def confirm_transition(
                self, 
                billing_account_name: str, 
                **kwargs: Any
            ) -> TransitionDetails: ...

        @distributed_trace
        def get(
                self, 
                billing_account_name: str, 
                **kwargs: Any
            ) -> BillingAccount: ...

        @distributed_trace
        def list(
                self, 
                *, 
                expand: Optional[str] = ..., 
                filter: Optional[str] = ..., 
                include_all: bool = False, 
                include_all_without_billing_profiles: bool = False, 
                include_deleted: bool = False, 
                include_pending_agreement: bool = False, 
                include_resellee: bool = False, 
                legal_owner_oid: Optional[str] = ..., 
                legal_owner_tid: Optional[str] = ..., 
                search: Optional[str] = ..., 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[BillingAccount]: ...

        @distributed_trace
        def list_invoice_sections_by_create_subscription_permission(
                self, 
                billing_account_name: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[InvoiceSectionWithCreateSubPermission]: ...

        @overload
        def validate_payment_terms(
                self, 
                billing_account_name: str, 
                parameters: List[PaymentTerm], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PaymentTermsEligibilityResult: ...

        @overload
        def validate_payment_terms(
                self, 
                billing_account_name: str, 
                parameters: List[JSON], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PaymentTermsEligibilityResult: ...

        @overload
        def validate_payment_terms(
                self, 
                billing_account_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PaymentTermsEligibilityResult: ...


    class azure.mgmt.billing.operations.BillingPermissionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def check_access_by_billing_account(
                self, 
                billing_account_name: str, 
                parameters: CheckAccessRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> List[CheckAccessResponse]: ...

        @overload
        def check_access_by_billing_account(
                self, 
                billing_account_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> List[CheckAccessResponse]: ...

        @overload
        def check_access_by_billing_account(
                self, 
                billing_account_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> List[CheckAccessResponse]: ...

        @overload
        def check_access_by_billing_profile(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                parameters: CheckAccessRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> List[CheckAccessResponse]: ...

        @overload
        def check_access_by_billing_profile(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> List[CheckAccessResponse]: ...

        @overload
        def check_access_by_billing_profile(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> List[CheckAccessResponse]: ...

        @overload
        def check_access_by_customer(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                customer_name: str, 
                parameters: CheckAccessRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> List[CheckAccessResponse]: ...

        @overload
        def check_access_by_customer(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                customer_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> List[CheckAccessResponse]: ...

        @overload
        def check_access_by_customer(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                customer_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> List[CheckAccessResponse]: ...

        @overload
        def check_access_by_department(
                self, 
                billing_account_name: str, 
                department_name: str, 
                parameters: CheckAccessRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> List[CheckAccessResponse]: ...

        @overload
        def check_access_by_department(
                self, 
                billing_account_name: str, 
                department_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> List[CheckAccessResponse]: ...

        @overload
        def check_access_by_department(
                self, 
                billing_account_name: str, 
                department_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> List[CheckAccessResponse]: ...

        @overload
        def check_access_by_enrollment_account(
                self, 
                billing_account_name: str, 
                enrollment_account_name: str, 
                parameters: CheckAccessRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> List[CheckAccessResponse]: ...

        @overload
        def check_access_by_enrollment_account(
                self, 
                billing_account_name: str, 
                enrollment_account_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> List[CheckAccessResponse]: ...

        @overload
        def check_access_by_enrollment_account(
                self, 
                billing_account_name: str, 
                enrollment_account_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> List[CheckAccessResponse]: ...

        @overload
        def check_access_by_invoice_section(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                invoice_section_name: str, 
                parameters: CheckAccessRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> List[CheckAccessResponse]: ...

        @overload
        def check_access_by_invoice_section(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                invoice_section_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> List[CheckAccessResponse]: ...

        @overload
        def check_access_by_invoice_section(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                invoice_section_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> List[CheckAccessResponse]: ...

        @distributed_trace
        def list_by_billing_account(
                self, 
                billing_account_name: str, 
                **kwargs: Any
            ) -> ItemPaged[BillingPermission]: ...

        @distributed_trace
        def list_by_billing_profile(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                **kwargs: Any
            ) -> ItemPaged[BillingPermission]: ...

        @distributed_trace
        def list_by_customer(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                customer_name: str, 
                **kwargs: Any
            ) -> ItemPaged[BillingPermission]: ...

        @distributed_trace
        def list_by_customer_at_billing_account(
                self, 
                billing_account_name: str, 
                customer_name: str, 
                **kwargs: Any
            ) -> ItemPaged[BillingPermission]: ...

        @distributed_trace
        def list_by_department(
                self, 
                billing_account_name: str, 
                department_name: str, 
                **kwargs: Any
            ) -> ItemPaged[BillingPermission]: ...

        @distributed_trace
        def list_by_enrollment_account(
                self, 
                billing_account_name: str, 
                enrollment_account_name: str, 
                **kwargs: Any
            ) -> ItemPaged[BillingPermission]: ...

        @distributed_trace
        def list_by_invoice_section(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                invoice_section_name: str, 
                **kwargs: Any
            ) -> ItemPaged[BillingPermission]: ...


    class azure.mgmt.billing.operations.BillingProfilesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                parameters: BillingProfile, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BillingProfile]: ...

        @overload
        def begin_create_or_update(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BillingProfile]: ...

        @overload
        def begin_create_or_update(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BillingProfile]: ...

        @distributed_trace
        def begin_delete(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                **kwargs: Any
            ) -> BillingProfile: ...

        @distributed_trace
        def list_by_billing_account(
                self, 
                billing_account_name: str, 
                *, 
                count: Optional[bool] = ..., 
                filter: Optional[str] = ..., 
                include_deleted: bool = False, 
                order_by: Optional[str] = ..., 
                search: Optional[str] = ..., 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[BillingProfile]: ...

        @distributed_trace
        def validate_delete_eligibility(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                **kwargs: Any
            ) -> DeleteBillingProfileEligibilityResult: ...


    class azure.mgmt.billing.operations.BillingPropertyOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                *, 
                include_billing_country: bool = False, 
                include_transition_status: bool = False, 
                **kwargs: Any
            ) -> BillingProperty: ...

        @overload
        def update(
                self, 
                parameters: BillingProperty, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> BillingProperty: ...

        @overload
        def update(
                self, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> BillingProperty: ...

        @overload
        def update(
                self, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> BillingProperty: ...


    class azure.mgmt.billing.operations.BillingRequestsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                billing_request_name: str, 
                parameters: BillingRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BillingRequest]: ...

        @overload
        def begin_create_or_update(
                self, 
                billing_request_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BillingRequest]: ...

        @overload
        def begin_create_or_update(
                self, 
                billing_request_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BillingRequest]: ...

        @distributed_trace
        def get(
                self, 
                billing_request_name: str, 
                **kwargs: Any
            ) -> BillingRequest: ...

        @distributed_trace
        def list_by_billing_account(
                self, 
                billing_account_name: str, 
                *, 
                count: Optional[bool] = ..., 
                filter: Optional[str] = ..., 
                order_by: Optional[str] = ..., 
                search: Optional[str] = ..., 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[BillingRequest]: ...

        @distributed_trace
        def list_by_billing_profile(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                *, 
                count: Optional[bool] = ..., 
                filter: Optional[str] = ..., 
                order_by: Optional[str] = ..., 
                search: Optional[str] = ..., 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[BillingRequest]: ...

        @distributed_trace
        def list_by_customer(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                customer_name: str, 
                *, 
                count: Optional[bool] = ..., 
                filter: Optional[str] = ..., 
                order_by: Optional[str] = ..., 
                search: Optional[str] = ..., 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[BillingRequest]: ...

        @distributed_trace
        def list_by_invoice_section(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                invoice_section_name: str, 
                *, 
                count: Optional[bool] = ..., 
                filter: Optional[str] = ..., 
                order_by: Optional[str] = ..., 
                search: Optional[str] = ..., 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[BillingRequest]: ...

        @distributed_trace
        def list_by_user(
                self, 
                *, 
                count: Optional[bool] = ..., 
                filter: Optional[str] = ..., 
                order_by: Optional[str] = ..., 
                search: Optional[str] = ..., 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[BillingRequest]: ...


    class azure.mgmt.billing.operations.BillingRoleAssignmentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_by_billing_account(
                self, 
                billing_account_name: str, 
                parameters: BillingRoleAssignmentProperties, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BillingRoleAssignment]: ...

        @overload
        def begin_create_by_billing_account(
                self, 
                billing_account_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BillingRoleAssignment]: ...

        @overload
        def begin_create_by_billing_account(
                self, 
                billing_account_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BillingRoleAssignment]: ...

        @overload
        def begin_create_by_billing_profile(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                parameters: BillingRoleAssignmentProperties, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BillingRoleAssignment]: ...

        @overload
        def begin_create_by_billing_profile(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BillingRoleAssignment]: ...

        @overload
        def begin_create_by_billing_profile(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BillingRoleAssignment]: ...

        @overload
        def begin_create_by_customer(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                customer_name: str, 
                parameters: BillingRoleAssignmentProperties, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BillingRoleAssignment]: ...

        @overload
        def begin_create_by_customer(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                customer_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BillingRoleAssignment]: ...

        @overload
        def begin_create_by_customer(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                customer_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BillingRoleAssignment]: ...

        @overload
        def begin_create_by_invoice_section(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                invoice_section_name: str, 
                parameters: BillingRoleAssignmentProperties, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BillingRoleAssignment]: ...

        @overload
        def begin_create_by_invoice_section(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                invoice_section_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BillingRoleAssignment]: ...

        @overload
        def begin_create_by_invoice_section(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                invoice_section_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BillingRoleAssignment]: ...

        @overload
        def begin_create_or_update_by_billing_account(
                self, 
                billing_account_name: str, 
                billing_role_assignment_name: str, 
                parameters: BillingRoleAssignment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BillingRoleAssignment]: ...

        @overload
        def begin_create_or_update_by_billing_account(
                self, 
                billing_account_name: str, 
                billing_role_assignment_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BillingRoleAssignment]: ...

        @overload
        def begin_create_or_update_by_billing_account(
                self, 
                billing_account_name: str, 
                billing_role_assignment_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BillingRoleAssignment]: ...

        @overload
        def begin_create_or_update_by_department(
                self, 
                billing_account_name: str, 
                department_name: str, 
                billing_role_assignment_name: str, 
                parameters: BillingRoleAssignment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BillingRoleAssignment]: ...

        @overload
        def begin_create_or_update_by_department(
                self, 
                billing_account_name: str, 
                department_name: str, 
                billing_role_assignment_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BillingRoleAssignment]: ...

        @overload
        def begin_create_or_update_by_department(
                self, 
                billing_account_name: str, 
                department_name: str, 
                billing_role_assignment_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BillingRoleAssignment]: ...

        @overload
        def begin_create_or_update_by_enrollment_account(
                self, 
                billing_account_name: str, 
                enrollment_account_name: str, 
                billing_role_assignment_name: str, 
                parameters: BillingRoleAssignment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BillingRoleAssignment]: ...

        @overload
        def begin_create_or_update_by_enrollment_account(
                self, 
                billing_account_name: str, 
                enrollment_account_name: str, 
                billing_role_assignment_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BillingRoleAssignment]: ...

        @overload
        def begin_create_or_update_by_enrollment_account(
                self, 
                billing_account_name: str, 
                enrollment_account_name: str, 
                billing_role_assignment_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BillingRoleAssignment]: ...

        @distributed_trace
        def begin_resolve_by_billing_account(
                self, 
                billing_account_name: str, 
                *, 
                filter: Optional[str] = ..., 
                resolve_scope_display_names: bool = False, 
                **kwargs: Any
            ) -> LROPoller[BillingRoleAssignmentListResult]: ...

        @distributed_trace
        def begin_resolve_by_billing_profile(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                *, 
                filter: Optional[str] = ..., 
                resolve_scope_display_names: bool = False, 
                **kwargs: Any
            ) -> LROPoller[BillingRoleAssignmentListResult]: ...

        @distributed_trace
        def begin_resolve_by_customer(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                customer_name: str, 
                *, 
                filter: Optional[str] = ..., 
                resolve_scope_display_names: bool = False, 
                **kwargs: Any
            ) -> LROPoller[BillingRoleAssignmentListResult]: ...

        @distributed_trace
        def begin_resolve_by_invoice_section(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                invoice_section_name: str, 
                *, 
                filter: Optional[str] = ..., 
                resolve_scope_display_names: bool = False, 
                **kwargs: Any
            ) -> LROPoller[BillingRoleAssignmentListResult]: ...

        @distributed_trace
        def delete_by_billing_account(
                self, 
                billing_account_name: str, 
                billing_role_assignment_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def delete_by_billing_profile(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                billing_role_assignment_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def delete_by_customer(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                customer_name: str, 
                billing_role_assignment_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def delete_by_department(
                self, 
                billing_account_name: str, 
                department_name: str, 
                billing_role_assignment_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def delete_by_enrollment_account(
                self, 
                billing_account_name: str, 
                enrollment_account_name: str, 
                billing_role_assignment_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def delete_by_invoice_section(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                invoice_section_name: str, 
                billing_role_assignment_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get_by_billing_account(
                self, 
                billing_account_name: str, 
                billing_role_assignment_name: str, 
                **kwargs: Any
            ) -> BillingRoleAssignment: ...

        @distributed_trace
        def get_by_billing_profile(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                billing_role_assignment_name: str, 
                **kwargs: Any
            ) -> BillingRoleAssignment: ...

        @distributed_trace
        def get_by_customer(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                customer_name: str, 
                billing_role_assignment_name: str, 
                **kwargs: Any
            ) -> BillingRoleAssignment: ...

        @distributed_trace
        def get_by_department(
                self, 
                billing_account_name: str, 
                department_name: str, 
                billing_role_assignment_name: str, 
                **kwargs: Any
            ) -> BillingRoleAssignment: ...

        @distributed_trace
        def get_by_enrollment_account(
                self, 
                billing_account_name: str, 
                enrollment_account_name: str, 
                billing_role_assignment_name: str, 
                **kwargs: Any
            ) -> BillingRoleAssignment: ...

        @distributed_trace
        def get_by_invoice_section(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                invoice_section_name: str, 
                billing_role_assignment_name: str, 
                **kwargs: Any
            ) -> BillingRoleAssignment: ...

        @distributed_trace
        def list_by_billing_account(
                self, 
                billing_account_name: str, 
                *, 
                filter: Optional[str] = ..., 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[BillingRoleAssignment]: ...

        @distributed_trace
        def list_by_billing_profile(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                *, 
                filter: Optional[str] = ..., 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[BillingRoleAssignment]: ...

        @distributed_trace
        def list_by_customer(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                customer_name: str, 
                *, 
                filter: Optional[str] = ..., 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[BillingRoleAssignment]: ...

        @distributed_trace
        def list_by_department(
                self, 
                billing_account_name: str, 
                department_name: str, 
                **kwargs: Any
            ) -> ItemPaged[BillingRoleAssignment]: ...

        @distributed_trace
        def list_by_enrollment_account(
                self, 
                billing_account_name: str, 
                enrollment_account_name: str, 
                **kwargs: Any
            ) -> ItemPaged[BillingRoleAssignment]: ...

        @distributed_trace
        def list_by_invoice_section(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                invoice_section_name: str, 
                *, 
                filter: Optional[str] = ..., 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[BillingRoleAssignment]: ...


    class azure.mgmt.billing.operations.BillingRoleDefinitionOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get_by_billing_account(
                self, 
                billing_account_name: str, 
                role_definition_name: str, 
                **kwargs: Any
            ) -> BillingRoleDefinition: ...

        @distributed_trace
        def get_by_billing_profile(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                role_definition_name: str, 
                **kwargs: Any
            ) -> BillingRoleDefinition: ...

        @distributed_trace
        def get_by_customer(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                customer_name: str, 
                role_definition_name: str, 
                **kwargs: Any
            ) -> BillingRoleDefinition: ...

        @distributed_trace
        def get_by_department(
                self, 
                billing_account_name: str, 
                department_name: str, 
                role_definition_name: str, 
                **kwargs: Any
            ) -> BillingRoleDefinition: ...

        @distributed_trace
        def get_by_enrollment_account(
                self, 
                billing_account_name: str, 
                enrollment_account_name: str, 
                role_definition_name: str, 
                **kwargs: Any
            ) -> BillingRoleDefinition: ...

        @distributed_trace
        def get_by_invoice_section(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                invoice_section_name: str, 
                role_definition_name: str, 
                **kwargs: Any
            ) -> BillingRoleDefinition: ...

        @distributed_trace
        def list_by_billing_account(
                self, 
                billing_account_name: str, 
                **kwargs: Any
            ) -> ItemPaged[BillingRoleDefinition]: ...

        @distributed_trace
        def list_by_billing_profile(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                **kwargs: Any
            ) -> ItemPaged[BillingRoleDefinition]: ...

        @distributed_trace
        def list_by_customer(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                customer_name: str, 
                **kwargs: Any
            ) -> ItemPaged[BillingRoleDefinition]: ...

        @distributed_trace
        def list_by_department(
                self, 
                billing_account_name: str, 
                department_name: str, 
                **kwargs: Any
            ) -> ItemPaged[BillingRoleDefinition]: ...

        @distributed_trace
        def list_by_enrollment_account(
                self, 
                billing_account_name: str, 
                enrollment_account_name: str, 
                **kwargs: Any
            ) -> ItemPaged[BillingRoleDefinition]: ...

        @distributed_trace
        def list_by_invoice_section(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                invoice_section_name: str, 
                **kwargs: Any
            ) -> ItemPaged[BillingRoleDefinition]: ...


    class azure.mgmt.billing.operations.BillingSubscriptionsAliasesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                billing_account_name: str, 
                alias_name: str, 
                parameters: BillingSubscriptionAlias, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BillingSubscriptionAlias]: ...

        @overload
        def begin_create_or_update(
                self, 
                billing_account_name: str, 
                alias_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BillingSubscriptionAlias]: ...

        @overload
        def begin_create_or_update(
                self, 
                billing_account_name: str, 
                alias_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BillingSubscriptionAlias]: ...

        @distributed_trace
        def get(
                self, 
                billing_account_name: str, 
                alias_name: str, 
                **kwargs: Any
            ) -> BillingSubscriptionAlias: ...

        @distributed_trace
        def list_by_billing_account(
                self, 
                billing_account_name: str, 
                *, 
                count: Optional[bool] = ..., 
                filter: Optional[str] = ..., 
                include_deleted: bool = False, 
                order_by: Optional[str] = ..., 
                search: Optional[str] = ..., 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[BillingSubscriptionAlias]: ...


    class azure.mgmt.billing.operations.BillingSubscriptionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_cancel(
                self, 
                billing_account_name: str, 
                billing_subscription_name: str, 
                parameters: CancelSubscriptionRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_cancel(
                self, 
                billing_account_name: str, 
                billing_subscription_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_cancel(
                self, 
                billing_account_name: str, 
                billing_subscription_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_delete(
                self, 
                billing_account_name: str, 
                billing_subscription_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_merge(
                self, 
                billing_account_name: str, 
                billing_subscription_name: str, 
                parameters: BillingSubscriptionMergeRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BillingSubscription]: ...

        @overload
        def begin_merge(
                self, 
                billing_account_name: str, 
                billing_subscription_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BillingSubscription]: ...

        @overload
        def begin_merge(
                self, 
                billing_account_name: str, 
                billing_subscription_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BillingSubscription]: ...

        @overload
        def begin_move(
                self, 
                billing_account_name: str, 
                billing_subscription_name: str, 
                parameters: MoveBillingSubscriptionRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BillingSubscription]: ...

        @overload
        def begin_move(
                self, 
                billing_account_name: str, 
                billing_subscription_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BillingSubscription]: ...

        @overload
        def begin_move(
                self, 
                billing_account_name: str, 
                billing_subscription_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BillingSubscription]: ...

        @overload
        def begin_split(
                self, 
                billing_account_name: str, 
                billing_subscription_name: str, 
                parameters: BillingSubscriptionSplitRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BillingSubscription]: ...

        @overload
        def begin_split(
                self, 
                billing_account_name: str, 
                billing_subscription_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BillingSubscription]: ...

        @overload
        def begin_split(
                self, 
                billing_account_name: str, 
                billing_subscription_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BillingSubscription]: ...

        @overload
        def begin_update(
                self, 
                billing_account_name: str, 
                billing_subscription_name: str, 
                parameters: BillingSubscriptionPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BillingSubscription]: ...

        @overload
        def begin_update(
                self, 
                billing_account_name: str, 
                billing_subscription_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BillingSubscription]: ...

        @overload
        def begin_update(
                self, 
                billing_account_name: str, 
                billing_subscription_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BillingSubscription]: ...

        @distributed_trace
        def get(
                self, 
                billing_account_name: str, 
                billing_subscription_name: str, 
                *, 
                expand: Optional[str] = ..., 
                **kwargs: Any
            ) -> BillingSubscription: ...

        @distributed_trace
        def get_by_billing_profile(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                billing_subscription_name: str, 
                *, 
                expand: Optional[str] = ..., 
                **kwargs: Any
            ) -> BillingSubscription: ...

        @distributed_trace
        def list_by_billing_account(
                self, 
                billing_account_name: str, 
                *, 
                count: Optional[bool] = ..., 
                expand: Optional[str] = ..., 
                filter: Optional[str] = ..., 
                include_deleted: bool = False, 
                include_failed: bool = False, 
                include_tenant_subscriptions: bool = False, 
                order_by: Optional[str] = ..., 
                search: Optional[str] = ..., 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[BillingSubscription]: ...

        @distributed_trace
        def list_by_billing_profile(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                *, 
                count: Optional[bool] = ..., 
                expand: Optional[str] = ..., 
                filter: Optional[str] = ..., 
                include_deleted: bool = False, 
                order_by: Optional[str] = ..., 
                search: Optional[str] = ..., 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[BillingSubscription]: ...

        @distributed_trace
        def list_by_customer(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                customer_name: str, 
                *, 
                count: Optional[bool] = ..., 
                expand: Optional[str] = ..., 
                filter: Optional[str] = ..., 
                include_deleted: bool = False, 
                order_by: Optional[str] = ..., 
                search: Optional[str] = ..., 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[BillingSubscription]: ...

        @distributed_trace
        def list_by_customer_at_billing_account(
                self, 
                billing_account_name: str, 
                customer_name: str, 
                *, 
                count: Optional[bool] = ..., 
                expand: Optional[str] = ..., 
                filter: Optional[str] = ..., 
                include_deleted: bool = False, 
                order_by: Optional[str] = ..., 
                search: Optional[str] = ..., 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[BillingSubscription]: ...

        @distributed_trace
        def list_by_enrollment_account(
                self, 
                billing_account_name: str, 
                enrollment_account_name: str, 
                *, 
                count: Optional[bool] = ..., 
                filter: Optional[str] = ..., 
                order_by: Optional[str] = ..., 
                search: Optional[str] = ..., 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[BillingSubscription]: ...

        @distributed_trace
        def list_by_invoice_section(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                invoice_section_name: str, 
                *, 
                count: Optional[bool] = ..., 
                expand: Optional[str] = ..., 
                filter: Optional[str] = ..., 
                include_deleted: bool = False, 
                order_by: Optional[str] = ..., 
                search: Optional[str] = ..., 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[BillingSubscription]: ...

        @overload
        def validate_move_eligibility(
                self, 
                billing_account_name: str, 
                billing_subscription_name: str, 
                parameters: MoveBillingSubscriptionRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MoveBillingSubscriptionEligibilityResult: ...

        @overload
        def validate_move_eligibility(
                self, 
                billing_account_name: str, 
                billing_subscription_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MoveBillingSubscriptionEligibilityResult: ...

        @overload
        def validate_move_eligibility(
                self, 
                billing_account_name: str, 
                billing_subscription_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MoveBillingSubscriptionEligibilityResult: ...


    class azure.mgmt.billing.operations.CustomersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                customer_name: str, 
                **kwargs: Any
            ) -> Customer: ...

        @distributed_trace
        def get_by_billing_account(
                self, 
                billing_account_name: str, 
                customer_name: str, 
                **kwargs: Any
            ) -> Customer: ...

        @distributed_trace
        def list_by_billing_account(
                self, 
                billing_account_name: str, 
                *, 
                count: Optional[bool] = ..., 
                expand: Optional[str] = ..., 
                filter: Optional[str] = ..., 
                order_by: Optional[str] = ..., 
                search: Optional[str] = ..., 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Customer]: ...

        @distributed_trace
        def list_by_billing_profile(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                *, 
                count: Optional[bool] = ..., 
                expand: Optional[str] = ..., 
                filter: Optional[str] = ..., 
                order_by: Optional[str] = ..., 
                search: Optional[str] = ..., 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Customer]: ...


    class azure.mgmt.billing.operations.DepartmentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                billing_account_name: str, 
                department_name: str, 
                **kwargs: Any
            ) -> Department: ...

        @distributed_trace
        def list_by_billing_account(
                self, 
                billing_account_name: str, 
                *, 
                filter: Optional[str] = ..., 
                order_by: Optional[str] = ..., 
                search: Optional[str] = ..., 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Department]: ...


    class azure.mgmt.billing.operations.EnrollmentAccountsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                billing_account_name: str, 
                enrollment_account_name: str, 
                **kwargs: Any
            ) -> EnrollmentAccount: ...

        @distributed_trace
        def get_by_department(
                self, 
                billing_account_name: str, 
                department_name: str, 
                enrollment_account_name: str, 
                **kwargs: Any
            ) -> EnrollmentAccount: ...

        @distributed_trace
        def list_by_billing_account(
                self, 
                billing_account_name: str, 
                *, 
                count: Optional[bool] = ..., 
                filter: Optional[str] = ..., 
                order_by: Optional[str] = ..., 
                search: Optional[str] = ..., 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[EnrollmentAccount]: ...

        @distributed_trace
        def list_by_department(
                self, 
                billing_account_name: str, 
                department_name: str, 
                *, 
                count: Optional[bool] = ..., 
                filter: Optional[str] = ..., 
                order_by: Optional[str] = ..., 
                search: Optional[str] = ..., 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[EnrollmentAccount]: ...


    class azure.mgmt.billing.operations.InvoiceSectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                invoice_section_name: str, 
                parameters: InvoiceSection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[InvoiceSection]: ...

        @overload
        def begin_create_or_update(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                invoice_section_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[InvoiceSection]: ...

        @overload
        def begin_create_or_update(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                invoice_section_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[InvoiceSection]: ...

        @distributed_trace
        def begin_delete(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                invoice_section_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                invoice_section_name: str, 
                **kwargs: Any
            ) -> InvoiceSection: ...

        @distributed_trace
        def list_by_billing_profile(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                *, 
                count: Optional[bool] = ..., 
                filter: Optional[str] = ..., 
                include_deleted: bool = False, 
                order_by: Optional[str] = ..., 
                search: Optional[str] = ..., 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[InvoiceSection]: ...

        @distributed_trace
        def validate_delete_eligibility(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                invoice_section_name: str, 
                **kwargs: Any
            ) -> DeleteInvoiceSectionEligibilityResult: ...


    class azure.mgmt.billing.operations.InvoicesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_amend(
                self, 
                billing_account_name: str, 
                invoice_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_download_by_billing_account(
                self, 
                billing_account_name: str, 
                invoice_name: str, 
                *, 
                document_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> LROPoller[DocumentDownloadResult]: ...

        @distributed_trace
        def begin_download_by_billing_subscription(
                self, 
                invoice_name: str, 
                *, 
                document_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> LROPoller[DocumentDownloadResult]: ...

        @overload
        def begin_download_documents_by_billing_account(
                self, 
                billing_account_name: str, 
                parameters: List[DocumentDownloadRequest], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DocumentDownloadResult]: ...

        @overload
        def begin_download_documents_by_billing_account(
                self, 
                billing_account_name: str, 
                parameters: List[JSON], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DocumentDownloadResult]: ...

        @overload
        def begin_download_documents_by_billing_account(
                self, 
                billing_account_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DocumentDownloadResult]: ...

        @overload
        def begin_download_documents_by_billing_subscription(
                self, 
                parameters: List[DocumentDownloadRequest], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DocumentDownloadResult]: ...

        @overload
        def begin_download_documents_by_billing_subscription(
                self, 
                parameters: List[JSON], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DocumentDownloadResult]: ...

        @overload
        def begin_download_documents_by_billing_subscription(
                self, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DocumentDownloadResult]: ...

        @distributed_trace
        def begin_download_summary_by_billing_account(
                self, 
                billing_account_name: str, 
                invoice_name: str, 
                **kwargs: Any
            ) -> LROPoller[DocumentDownloadResult]: ...

        @distributed_trace
        def get(
                self, 
                invoice_name: str, 
                **kwargs: Any
            ) -> Invoice: ...

        @distributed_trace
        def get_by_billing_account(
                self, 
                billing_account_name: str, 
                invoice_name: str, 
                **kwargs: Any
            ) -> Invoice: ...

        @distributed_trace
        def get_by_billing_subscription(
                self, 
                invoice_name: str, 
                **kwargs: Any
            ) -> Invoice: ...

        @distributed_trace
        def list_by_billing_account(
                self, 
                billing_account_name: str, 
                *, 
                count: Optional[bool] = ..., 
                filter: Optional[str] = ..., 
                order_by: Optional[str] = ..., 
                period_end_date: Optional[date] = ..., 
                period_start_date: Optional[date] = ..., 
                search: Optional[str] = ..., 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Invoice]: ...

        @distributed_trace
        def list_by_billing_profile(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                *, 
                count: Optional[bool] = ..., 
                filter: Optional[str] = ..., 
                order_by: Optional[str] = ..., 
                period_end_date: Optional[date] = ..., 
                period_start_date: Optional[date] = ..., 
                search: Optional[str] = ..., 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Invoice]: ...

        @distributed_trace
        def list_by_billing_subscription(
                self, 
                *, 
                count: Optional[bool] = ..., 
                filter: Optional[str] = ..., 
                order_by: Optional[str] = ..., 
                period_end_date: Optional[date] = ..., 
                period_start_date: Optional[date] = ..., 
                search: Optional[str] = ..., 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Invoice]: ...


    class azure.mgmt.billing.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


    class azure.mgmt.billing.operations.PartnerTransfersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def cancel(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                customer_name: str, 
                transfer_name: str, 
                **kwargs: Any
            ) -> PartnerTransferDetails: ...

        @distributed_trace
        def get(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                customer_name: str, 
                transfer_name: str, 
                **kwargs: Any
            ) -> PartnerTransferDetails: ...

        @overload
        def initiate(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                customer_name: str, 
                transfer_name: str, 
                parameters: PartnerInitiateTransferRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PartnerTransferDetails: ...

        @overload
        def initiate(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                customer_name: str, 
                transfer_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PartnerTransferDetails: ...

        @overload
        def initiate(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                customer_name: str, 
                transfer_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PartnerTransferDetails: ...

        @distributed_trace
        def list(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                customer_name: str, 
                **kwargs: Any
            ) -> ItemPaged[PartnerTransferDetails]: ...


    class azure.mgmt.billing.operations.PaymentMethodsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def delete_by_user(
                self, 
                payment_method_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get_by_billing_account(
                self, 
                billing_account_name: str, 
                payment_method_name: str, 
                **kwargs: Any
            ) -> PaymentMethod: ...

        @distributed_trace
        def get_by_billing_profile(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                payment_method_name: str, 
                **kwargs: Any
            ) -> PaymentMethodLink: ...

        @distributed_trace
        def get_by_user(
                self, 
                payment_method_name: str, 
                **kwargs: Any
            ) -> PaymentMethod: ...

        @distributed_trace
        def list_by_billing_account(
                self, 
                billing_account_name: str, 
                **kwargs: Any
            ) -> ItemPaged[PaymentMethod]: ...

        @distributed_trace
        def list_by_billing_profile(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                **kwargs: Any
            ) -> ItemPaged[PaymentMethodLink]: ...

        @distributed_trace
        def list_by_user(self, **kwargs: Any) -> ItemPaged[PaymentMethod]: ...


    class azure.mgmt.billing.operations.PoliciesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update_by_billing_account(
                self, 
                billing_account_name: str, 
                parameters: BillingAccountPolicy, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BillingAccountPolicy]: ...

        @overload
        def begin_create_or_update_by_billing_account(
                self, 
                billing_account_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BillingAccountPolicy]: ...

        @overload
        def begin_create_or_update_by_billing_account(
                self, 
                billing_account_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BillingAccountPolicy]: ...

        @overload
        def begin_create_or_update_by_billing_profile(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                parameters: BillingProfilePolicy, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BillingProfilePolicy]: ...

        @overload
        def begin_create_or_update_by_billing_profile(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BillingProfilePolicy]: ...

        @overload
        def begin_create_or_update_by_billing_profile(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BillingProfilePolicy]: ...

        @overload
        def begin_create_or_update_by_customer(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                customer_name: str, 
                parameters: CustomerPolicy, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CustomerPolicy]: ...

        @overload
        def begin_create_or_update_by_customer(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                customer_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CustomerPolicy]: ...

        @overload
        def begin_create_or_update_by_customer(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                customer_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CustomerPolicy]: ...

        @overload
        def begin_create_or_update_by_customer_at_billing_account(
                self, 
                billing_account_name: str, 
                customer_name: str, 
                parameters: CustomerPolicy, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CustomerPolicy]: ...

        @overload
        def begin_create_or_update_by_customer_at_billing_account(
                self, 
                billing_account_name: str, 
                customer_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CustomerPolicy]: ...

        @overload
        def begin_create_or_update_by_customer_at_billing_account(
                self, 
                billing_account_name: str, 
                customer_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CustomerPolicy]: ...

        @distributed_trace
        def get_by_billing_account(
                self, 
                billing_account_name: str, 
                **kwargs: Any
            ) -> BillingAccountPolicy: ...

        @distributed_trace
        def get_by_billing_profile(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                **kwargs: Any
            ) -> BillingProfilePolicy: ...

        @distributed_trace
        def get_by_customer(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                customer_name: str, 
                policy_name: Union[str, ServiceDefinedResourceName], 
                **kwargs: Any
            ) -> CustomerPolicy: ...

        @distributed_trace
        def get_by_customer_at_billing_account(
                self, 
                billing_account_name: str, 
                customer_name: str, 
                **kwargs: Any
            ) -> CustomerPolicy: ...

        @distributed_trace
        def get_by_subscription(self, **kwargs: Any) -> SubscriptionPolicy: ...


    class azure.mgmt.billing.operations.ProductsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_move(
                self, 
                billing_account_name: str, 
                product_name: str, 
                parameters: MoveProductRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Product]: ...

        @overload
        def begin_move(
                self, 
                billing_account_name: str, 
                product_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Product]: ...

        @overload
        def begin_move(
                self, 
                billing_account_name: str, 
                product_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Product]: ...

        @distributed_trace
        def get(
                self, 
                billing_account_name: str, 
                product_name: str, 
                **kwargs: Any
            ) -> Product: ...

        @distributed_trace
        def list_by_billing_account(
                self, 
                billing_account_name: str, 
                *, 
                count: Optional[bool] = ..., 
                filter: Optional[str] = ..., 
                order_by: Optional[str] = ..., 
                search: Optional[str] = ..., 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Product]: ...

        @distributed_trace
        def list_by_billing_profile(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                *, 
                count: Optional[bool] = ..., 
                filter: Optional[str] = ..., 
                order_by: Optional[str] = ..., 
                search: Optional[str] = ..., 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Product]: ...

        @distributed_trace
        def list_by_customer(
                self, 
                billing_account_name: str, 
                customer_name: str, 
                *, 
                count: Optional[bool] = ..., 
                filter: Optional[str] = ..., 
                order_by: Optional[str] = ..., 
                search: Optional[str] = ..., 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Product]: ...

        @distributed_trace
        def list_by_invoice_section(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                invoice_section_name: str, 
                *, 
                count: Optional[bool] = ..., 
                filter: Optional[str] = ..., 
                order_by: Optional[str] = ..., 
                search: Optional[str] = ..., 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Product]: ...

        @overload
        def update(
                self, 
                billing_account_name: str, 
                product_name: str, 
                parameters: ProductPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Product: ...

        @overload
        def update(
                self, 
                billing_account_name: str, 
                product_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Product: ...

        @overload
        def update(
                self, 
                billing_account_name: str, 
                product_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Product: ...

        @overload
        def validate_move_eligibility(
                self, 
                billing_account_name: str, 
                product_name: str, 
                parameters: MoveProductRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MoveProductEligibilityResult: ...

        @overload
        def validate_move_eligibility(
                self, 
                billing_account_name: str, 
                product_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MoveProductEligibilityResult: ...

        @overload
        def validate_move_eligibility(
                self, 
                billing_account_name: str, 
                product_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MoveProductEligibilityResult: ...


    class azure.mgmt.billing.operations.RecipientTransfersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def accept(
                self, 
                transfer_name: str, 
                parameters: AcceptTransferRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RecipientTransferDetails: ...

        @overload
        def accept(
                self, 
                transfer_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RecipientTransferDetails: ...

        @overload
        def accept(
                self, 
                transfer_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RecipientTransferDetails: ...

        @distributed_trace
        def decline(
                self, 
                transfer_name: str, 
                **kwargs: Any
            ) -> RecipientTransferDetails: ...

        @distributed_trace
        def get(
                self, 
                transfer_name: str, 
                **kwargs: Any
            ) -> RecipientTransferDetails: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[RecipientTransferDetails]: ...

        @overload
        def validate(
                self, 
                transfer_name: str, 
                parameters: AcceptTransferRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ValidateTransferListResponse: ...

        @overload
        def validate(
                self, 
                transfer_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ValidateTransferListResponse: ...

        @overload
        def validate(
                self, 
                transfer_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ValidateTransferListResponse: ...


    class azure.mgmt.billing.operations.ReservationOrdersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get_by_billing_account(
                self, 
                billing_account_name: str, 
                reservation_order_id: str, 
                *, 
                expand: Optional[str] = ..., 
                **kwargs: Any
            ) -> ReservationOrder: ...

        @distributed_trace
        def list_by_billing_account(
                self, 
                billing_account_name: str, 
                *, 
                filter: Optional[str] = ..., 
                order_by: Optional[str] = ..., 
                skiptoken: Optional[float] = ..., 
                **kwargs: Any
            ) -> ItemPaged[ReservationOrder]: ...


    class azure.mgmt.billing.operations.ReservationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_update_by_billing_account(
                self, 
                billing_account_name: str, 
                reservation_order_id: str, 
                reservation_id: str, 
                body: Patch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Reservation]: ...

        @overload
        def begin_update_by_billing_account(
                self, 
                billing_account_name: str, 
                reservation_order_id: str, 
                reservation_id: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Reservation]: ...

        @overload
        def begin_update_by_billing_account(
                self, 
                billing_account_name: str, 
                reservation_order_id: str, 
                reservation_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Reservation]: ...

        @distributed_trace
        def get_by_reservation_order(
                self, 
                billing_account_name: str, 
                reservation_order_id: str, 
                reservation_id: str, 
                *, 
                expand: Optional[str] = ..., 
                **kwargs: Any
            ) -> Reservation: ...

        @distributed_trace
        def list_by_billing_account(
                self, 
                billing_account_name: str, 
                *, 
                filter: Optional[str] = ..., 
                order_by: Optional[str] = ..., 
                refresh_summary: Optional[str] = ..., 
                selected_state: Optional[str] = ..., 
                skiptoken: Optional[float] = ..., 
                take: Optional[float] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Reservation]: ...

        @distributed_trace
        def list_by_billing_profile(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                *, 
                filter: Optional[str] = ..., 
                order_by: Optional[str] = ..., 
                refresh_summary: Optional[str] = ..., 
                selected_state: Optional[str] = ..., 
                skiptoken: Optional[float] = ..., 
                take: Optional[float] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Reservation]: ...

        @distributed_trace
        def list_by_reservation_order(
                self, 
                billing_account_name: str, 
                reservation_order_id: str, 
                **kwargs: Any
            ) -> ItemPaged[Reservation]: ...


    class azure.mgmt.billing.operations.SavingsPlanOrdersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get_by_billing_account(
                self, 
                billing_account_name: str, 
                savings_plan_order_id: str, 
                *, 
                expand: Optional[str] = ..., 
                **kwargs: Any
            ) -> SavingsPlanOrderModel: ...

        @distributed_trace
        def list_by_billing_account(
                self, 
                billing_account_name: str, 
                *, 
                filter: Optional[str] = ..., 
                order_by: Optional[str] = ..., 
                skiptoken: Optional[float] = ..., 
                **kwargs: Any
            ) -> ItemPaged[SavingsPlanOrderModel]: ...


    class azure.mgmt.billing.operations.SavingsPlansOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_update_by_billing_account(
                self, 
                billing_account_name: str, 
                savings_plan_order_id: str, 
                savings_plan_id: str, 
                body: SavingsPlanUpdateRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SavingsPlanModel]: ...

        @overload
        def begin_update_by_billing_account(
                self, 
                billing_account_name: str, 
                savings_plan_order_id: str, 
                savings_plan_id: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SavingsPlanModel]: ...

        @overload
        def begin_update_by_billing_account(
                self, 
                billing_account_name: str, 
                savings_plan_order_id: str, 
                savings_plan_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SavingsPlanModel]: ...

        @distributed_trace
        def get_by_billing_account(
                self, 
                billing_account_name: str, 
                savings_plan_order_id: str, 
                savings_plan_id: str, 
                *, 
                expand: Optional[str] = ..., 
                **kwargs: Any
            ) -> SavingsPlanModel: ...

        @distributed_trace
        def list_by_billing_account(
                self, 
                billing_account_name: str, 
                *, 
                filter: Optional[str] = ..., 
                order_by: Optional[str] = ..., 
                refresh_summary: Optional[str] = ..., 
                selected_state: Optional[str] = ..., 
                skiptoken: Optional[float] = ..., 
                take: Optional[float] = ..., 
                **kwargs: Any
            ) -> ItemPaged[SavingsPlanModel]: ...

        @distributed_trace
        def list_by_savings_plan_order(
                self, 
                billing_account_name: str, 
                savings_plan_order_id: str, 
                **kwargs: Any
            ) -> ItemPaged[SavingsPlanModel]: ...

        @overload
        def validate_update_by_billing_account(
                self, 
                billing_account_name: str, 
                savings_plan_order_id: str, 
                savings_plan_id: str, 
                body: SavingsPlanUpdateValidateRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SavingsPlanValidateResponse: ...

        @overload
        def validate_update_by_billing_account(
                self, 
                billing_account_name: str, 
                savings_plan_order_id: str, 
                savings_plan_id: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SavingsPlanValidateResponse: ...

        @overload
        def validate_update_by_billing_account(
                self, 
                billing_account_name: str, 
                savings_plan_order_id: str, 
                savings_plan_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SavingsPlanValidateResponse: ...


    class azure.mgmt.billing.operations.TransactionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_transactions_download_by_invoice(
                self, 
                billing_account_name: str, 
                invoice_name: str, 
                **kwargs: Any
            ) -> LROPoller[DocumentDownloadResult]: ...

        @distributed_trace
        def get_transaction_summary_by_invoice(
                self, 
                billing_account_name: str, 
                invoice_name: str, 
                *, 
                filter: Optional[str] = ..., 
                search: Optional[str] = ..., 
                **kwargs: Any
            ) -> TransactionSummary: ...

        @distributed_trace
        def list_by_billing_profile(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                *, 
                count: Optional[bool] = ..., 
                filter: Optional[str] = ..., 
                order_by: Optional[str] = ..., 
                period_end_date: date, 
                period_start_date: date, 
                search: Optional[str] = ..., 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                type: Union[str, TransactionType], 
                **kwargs: Any
            ) -> ItemPaged[Transaction]: ...

        @distributed_trace
        def list_by_customer(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                customer_name: str, 
                *, 
                count: Optional[bool] = ..., 
                filter: Optional[str] = ..., 
                order_by: Optional[str] = ..., 
                period_end_date: date, 
                period_start_date: date, 
                search: Optional[str] = ..., 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                type: Union[str, TransactionType], 
                **kwargs: Any
            ) -> ItemPaged[Transaction]: ...

        @distributed_trace
        def list_by_invoice(
                self, 
                billing_account_name: str, 
                invoice_name: str, 
                *, 
                count: Optional[bool] = ..., 
                filter: Optional[str] = ..., 
                order_by: Optional[str] = ..., 
                search: Optional[str] = ..., 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Transaction]: ...

        @distributed_trace
        def list_by_invoice_section(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                invoice_section_name: str, 
                *, 
                count: Optional[bool] = ..., 
                filter: Optional[str] = ..., 
                order_by: Optional[str] = ..., 
                period_end_date: date, 
                period_start_date: date, 
                search: Optional[str] = ..., 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                type: Union[str, TransactionType], 
                **kwargs: Any
            ) -> ItemPaged[Transaction]: ...


    class azure.mgmt.billing.operations.TransfersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def cancel(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                invoice_section_name: str, 
                transfer_name: str, 
                **kwargs: Any
            ) -> TransferDetails: ...

        @distributed_trace
        def get(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                invoice_section_name: str, 
                transfer_name: str, 
                **kwargs: Any
            ) -> TransferDetails: ...

        @overload
        def initiate(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                invoice_section_name: str, 
                transfer_name: str, 
                parameters: InitiateTransferRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TransferDetails: ...

        @overload
        def initiate(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                invoice_section_name: str, 
                transfer_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TransferDetails: ...

        @overload
        def initiate(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                invoice_section_name: str, 
                transfer_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TransferDetails: ...

        @distributed_trace
        def list(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                invoice_section_name: str, 
                **kwargs: Any
            ) -> ItemPaged[TransferDetails]: ...


```