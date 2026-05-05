```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


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
                base_url: str = "https://management.azure.com", 
                *, 
                api_version: str = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def close(self) -> None: ...


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
                base_url: str = "https://management.azure.com", 
                *, 
                api_version: str = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        async def close(self) -> None: ...


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
                expand: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncIterable[Agreement]: ...


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
                include_revoked: bool = False, 
                filter: Optional[str] = None, 
                order_by: Optional[str] = None, 
                top: Optional[int] = None, 
                skip: Optional[int] = None, 
                count: Optional[bool] = None, 
                search: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncIterable[AssociatedTenant]: ...


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
                include_all: bool = False, 
                include_all_without_billing_profiles: bool = False, 
                include_deleted: bool = False, 
                include_pending_agreement: bool = False, 
                include_resellee: bool = False, 
                legal_owner_tid: Optional[str] = None, 
                legal_owner_oid: Optional[str] = None, 
                filter: Optional[str] = None, 
                expand: Optional[str] = None, 
                top: Optional[int] = None, 
                skip: Optional[int] = None, 
                search: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncIterable[BillingAccount]: ...

        @distributed_trace
        def list_invoice_sections_by_create_subscription_permission(
                self, 
                billing_account_name: str, 
                filter: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncIterable[InvoiceSectionWithCreateSubPermission]: ...

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
            ) -> AsyncIterable[BillingPermission]: ...

        @distributed_trace
        def list_by_billing_profile(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[BillingPermission]: ...

        @distributed_trace
        def list_by_customer(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                customer_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[BillingPermission]: ...

        @distributed_trace
        def list_by_customer_at_billing_account(
                self, 
                billing_account_name: str, 
                customer_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[BillingPermission]: ...

        @distributed_trace
        def list_by_department(
                self, 
                billing_account_name: str, 
                department_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[BillingPermission]: ...

        @distributed_trace
        def list_by_enrollment_account(
                self, 
                billing_account_name: str, 
                enrollment_account_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[BillingPermission]: ...

        @distributed_trace
        def list_by_invoice_section(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                invoice_section_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[BillingPermission]: ...


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
                include_deleted: bool = False, 
                filter: Optional[str] = None, 
                order_by: Optional[str] = None, 
                top: Optional[int] = None, 
                skip: Optional[int] = None, 
                count: Optional[bool] = None, 
                search: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncIterable[BillingProfile]: ...

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
                filter: Optional[str] = None, 
                order_by: Optional[str] = None, 
                top: Optional[int] = None, 
                skip: Optional[int] = None, 
                count: Optional[bool] = None, 
                search: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncIterable[BillingRequest]: ...

        @distributed_trace
        def list_by_billing_profile(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                filter: Optional[str] = None, 
                order_by: Optional[str] = None, 
                top: Optional[int] = None, 
                skip: Optional[int] = None, 
                count: Optional[bool] = None, 
                search: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncIterable[BillingRequest]: ...

        @distributed_trace
        def list_by_customer(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                customer_name: str, 
                filter: Optional[str] = None, 
                order_by: Optional[str] = None, 
                top: Optional[int] = None, 
                skip: Optional[int] = None, 
                count: Optional[bool] = None, 
                search: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncIterable[BillingRequest]: ...

        @distributed_trace
        def list_by_invoice_section(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                invoice_section_name: str, 
                filter: Optional[str] = None, 
                order_by: Optional[str] = None, 
                top: Optional[int] = None, 
                skip: Optional[int] = None, 
                count: Optional[bool] = None, 
                search: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncIterable[BillingRequest]: ...

        @distributed_trace
        def list_by_user(
                self, 
                filter: Optional[str] = None, 
                order_by: Optional[str] = None, 
                top: Optional[int] = None, 
                skip: Optional[int] = None, 
                count: Optional[bool] = None, 
                search: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncIterable[BillingRequest]: ...


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
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BillingRoleAssignment]: ...

        @distributed_trace_async
        async def begin_resolve_by_billing_account(
                self, 
                billing_account_name: str, 
                resolve_scope_display_names: bool = False, 
                filter: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncLROPoller[BillingRoleAssignmentListResult]: ...

        @distributed_trace_async
        async def begin_resolve_by_billing_profile(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                resolve_scope_display_names: bool = False, 
                filter: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncLROPoller[BillingRoleAssignmentListResult]: ...

        @distributed_trace_async
        async def begin_resolve_by_customer(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                customer_name: str, 
                resolve_scope_display_names: bool = False, 
                filter: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncLROPoller[BillingRoleAssignmentListResult]: ...

        @distributed_trace_async
        async def begin_resolve_by_invoice_section(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                invoice_section_name: str, 
                resolve_scope_display_names: bool = False, 
                filter: Optional[str] = None, 
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
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                skip: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncIterable[BillingRoleAssignment]: ...

        @distributed_trace
        def list_by_billing_profile(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                skip: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncIterable[BillingRoleAssignment]: ...

        @distributed_trace
        def list_by_customer(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                customer_name: str, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                skip: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncIterable[BillingRoleAssignment]: ...

        @distributed_trace
        def list_by_department(
                self, 
                billing_account_name: str, 
                department_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[BillingRoleAssignment]: ...

        @distributed_trace
        def list_by_enrollment_account(
                self, 
                billing_account_name: str, 
                enrollment_account_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[BillingRoleAssignment]: ...

        @distributed_trace
        def list_by_invoice_section(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                invoice_section_name: str, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                skip: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncIterable[BillingRoleAssignment]: ...


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
            ) -> AsyncIterable[BillingRoleDefinition]: ...

        @distributed_trace
        def list_by_billing_profile(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[BillingRoleDefinition]: ...

        @distributed_trace
        def list_by_customer(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                customer_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[BillingRoleDefinition]: ...

        @distributed_trace
        def list_by_department(
                self, 
                billing_account_name: str, 
                department_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[BillingRoleDefinition]: ...

        @distributed_trace
        def list_by_enrollment_account(
                self, 
                billing_account_name: str, 
                enrollment_account_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[BillingRoleDefinition]: ...

        @distributed_trace
        def list_by_invoice_section(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                invoice_section_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[BillingRoleDefinition]: ...


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
                include_deleted: bool = False, 
                filter: Optional[str] = None, 
                order_by: Optional[str] = None, 
                top: Optional[int] = None, 
                skip: Optional[int] = None, 
                count: Optional[bool] = None, 
                search: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncIterable[BillingSubscriptionAlias]: ...


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
                expand: Optional[str] = None, 
                **kwargs: Any
            ) -> BillingSubscription: ...

        @distributed_trace_async
        async def get_by_billing_profile(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                billing_subscription_name: str, 
                expand: Optional[str] = None, 
                **kwargs: Any
            ) -> BillingSubscription: ...

        @distributed_trace
        def list_by_billing_account(
                self, 
                billing_account_name: str, 
                include_deleted: bool = False, 
                include_tenant_subscriptions: bool = False, 
                include_failed: bool = False, 
                expand: Optional[str] = None, 
                filter: Optional[str] = None, 
                order_by: Optional[str] = None, 
                top: Optional[int] = None, 
                skip: Optional[int] = None, 
                count: Optional[bool] = None, 
                search: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncIterable[BillingSubscription]: ...

        @distributed_trace
        def list_by_billing_profile(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                include_deleted: bool = False, 
                expand: Optional[str] = None, 
                filter: Optional[str] = None, 
                order_by: Optional[str] = None, 
                top: Optional[int] = None, 
                skip: Optional[int] = None, 
                count: Optional[bool] = None, 
                search: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncIterable[BillingSubscription]: ...

        @distributed_trace
        def list_by_customer(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                customer_name: str, 
                include_deleted: bool = False, 
                expand: Optional[str] = None, 
                filter: Optional[str] = None, 
                order_by: Optional[str] = None, 
                top: Optional[int] = None, 
                skip: Optional[int] = None, 
                count: Optional[bool] = None, 
                search: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncIterable[BillingSubscription]: ...

        @distributed_trace
        def list_by_customer_at_billing_account(
                self, 
                billing_account_name: str, 
                customer_name: str, 
                include_deleted: bool = False, 
                expand: Optional[str] = None, 
                filter: Optional[str] = None, 
                order_by: Optional[str] = None, 
                top: Optional[int] = None, 
                skip: Optional[int] = None, 
                count: Optional[bool] = None, 
                search: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncIterable[BillingSubscription]: ...

        @distributed_trace
        def list_by_enrollment_account(
                self, 
                billing_account_name: str, 
                enrollment_account_name: str, 
                filter: Optional[str] = None, 
                order_by: Optional[str] = None, 
                top: Optional[int] = None, 
                skip: Optional[int] = None, 
                count: Optional[bool] = None, 
                search: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncIterable[BillingSubscription]: ...

        @distributed_trace
        def list_by_invoice_section(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                invoice_section_name: str, 
                include_deleted: bool = False, 
                expand: Optional[str] = None, 
                filter: Optional[str] = None, 
                order_by: Optional[str] = None, 
                top: Optional[int] = None, 
                skip: Optional[int] = None, 
                count: Optional[bool] = None, 
                search: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncIterable[BillingSubscription]: ...

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
                expand: Optional[str] = None, 
                filter: Optional[str] = None, 
                order_by: Optional[str] = None, 
                top: Optional[int] = None, 
                skip: Optional[int] = None, 
                count: Optional[bool] = None, 
                search: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncIterable[Customer]: ...

        @distributed_trace
        def list_by_billing_profile(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                expand: Optional[str] = None, 
                filter: Optional[str] = None, 
                order_by: Optional[str] = None, 
                top: Optional[int] = None, 
                skip: Optional[int] = None, 
                count: Optional[bool] = None, 
                search: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncIterable[Customer]: ...


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
                filter: Optional[str] = None, 
                order_by: Optional[str] = None, 
                top: Optional[int] = None, 
                skip: Optional[int] = None, 
                search: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncIterable[Department]: ...


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
                filter: Optional[str] = None, 
                order_by: Optional[str] = None, 
                top: Optional[int] = None, 
                skip: Optional[int] = None, 
                count: Optional[bool] = None, 
                search: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncIterable[EnrollmentAccount]: ...

        @distributed_trace
        def list_by_department(
                self, 
                billing_account_name: str, 
                department_name: str, 
                filter: Optional[str] = None, 
                order_by: Optional[str] = None, 
                top: Optional[int] = None, 
                skip: Optional[int] = None, 
                count: Optional[bool] = None, 
                search: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncIterable[EnrollmentAccount]: ...


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
                include_deleted: bool = False, 
                filter: Optional[str] = None, 
                order_by: Optional[str] = None, 
                top: Optional[int] = None, 
                skip: Optional[int] = None, 
                count: Optional[bool] = None, 
                search: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncIterable[InvoiceSection]: ...

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
                document_name: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncLROPoller[DocumentDownloadResult]: ...

        @distributed_trace_async
        async def begin_download_by_billing_subscription(
                self, 
                invoice_name: str, 
                document_name: Optional[str] = None, 
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
                period_start_date: Optional[date] = None, 
                period_end_date: Optional[date] = None, 
                filter: Optional[str] = None, 
                order_by: Optional[str] = None, 
                top: Optional[int] = None, 
                skip: Optional[int] = None, 
                count: Optional[bool] = None, 
                search: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncIterable[Invoice]: ...

        @distributed_trace
        def list_by_billing_profile(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                period_start_date: Optional[date] = None, 
                period_end_date: Optional[date] = None, 
                filter: Optional[str] = None, 
                order_by: Optional[str] = None, 
                top: Optional[int] = None, 
                skip: Optional[int] = None, 
                count: Optional[bool] = None, 
                search: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncIterable[Invoice]: ...

        @distributed_trace
        def list_by_billing_subscription(
                self, 
                period_start_date: Optional[date] = None, 
                period_end_date: Optional[date] = None, 
                filter: Optional[str] = None, 
                order_by: Optional[str] = None, 
                top: Optional[int] = None, 
                skip: Optional[int] = None, 
                count: Optional[bool] = None, 
                search: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncIterable[Invoice]: ...


    class azure.mgmt.billing.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncIterable[Operation]: ...


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
            ) -> AsyncIterable[PartnerTransferDetails]: ...


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
            ) -> AsyncIterable[PaymentMethod]: ...

        @distributed_trace
        def list_by_billing_profile(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[PaymentMethodLink]: ...

        @distributed_trace
        def list_by_user(self, **kwargs: Any) -> AsyncIterable[PaymentMethod]: ...


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
                filter: Optional[str] = None, 
                order_by: Optional[str] = None, 
                top: Optional[int] = None, 
                skip: Optional[int] = None, 
                count: Optional[bool] = None, 
                search: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncIterable[Product]: ...

        @distributed_trace
        def list_by_billing_profile(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                filter: Optional[str] = None, 
                order_by: Optional[str] = None, 
                top: Optional[int] = None, 
                skip: Optional[int] = None, 
                count: Optional[bool] = None, 
                search: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncIterable[Product]: ...

        @distributed_trace
        def list_by_customer(
                self, 
                billing_account_name: str, 
                customer_name: str, 
                filter: Optional[str] = None, 
                order_by: Optional[str] = None, 
                top: Optional[int] = None, 
                skip: Optional[int] = None, 
                count: Optional[bool] = None, 
                search: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncIterable[Product]: ...

        @distributed_trace
        def list_by_invoice_section(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                invoice_section_name: str, 
                filter: Optional[str] = None, 
                order_by: Optional[str] = None, 
                top: Optional[int] = None, 
                skip: Optional[int] = None, 
                count: Optional[bool] = None, 
                search: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncIterable[Product]: ...

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
        def list(self, **kwargs: Any) -> AsyncIterable[RecipientTransferDetails]: ...

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
                expand: Optional[str] = None, 
                **kwargs: Any
            ) -> ReservationOrder: ...

        @distributed_trace
        def list_by_billing_account(
                self, 
                billing_account_name: str, 
                filter: Optional[str] = None, 
                order_by: Optional[str] = None, 
                skiptoken: Optional[float] = None, 
                **kwargs: Any
            ) -> AsyncIterable[ReservationOrder]: ...


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
                expand: Optional[str] = None, 
                **kwargs: Any
            ) -> Reservation: ...

        @distributed_trace
        def list_by_billing_account(
                self, 
                billing_account_name: str, 
                filter: Optional[str] = None, 
                order_by: Optional[str] = None, 
                skiptoken: Optional[float] = None, 
                refresh_summary: Optional[str] = None, 
                selected_state: Optional[str] = None, 
                take: Optional[float] = None, 
                **kwargs: Any
            ) -> AsyncIterable[Reservation]: ...

        @distributed_trace
        def list_by_billing_profile(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                filter: Optional[str] = None, 
                order_by: Optional[str] = None, 
                skiptoken: Optional[float] = None, 
                refresh_summary: Optional[str] = None, 
                selected_state: Optional[str] = None, 
                take: Optional[float] = None, 
                **kwargs: Any
            ) -> AsyncIterable[Reservation]: ...

        @distributed_trace
        def list_by_reservation_order(
                self, 
                billing_account_name: str, 
                reservation_order_id: str, 
                **kwargs: Any
            ) -> AsyncIterable[Reservation]: ...


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
                expand: Optional[str] = None, 
                **kwargs: Any
            ) -> SavingsPlanOrderModel: ...

        @distributed_trace
        def list_by_billing_account(
                self, 
                billing_account_name: str, 
                filter: Optional[str] = None, 
                order_by: Optional[str] = None, 
                skiptoken: Optional[float] = None, 
                **kwargs: Any
            ) -> AsyncIterable[SavingsPlanOrderModel]: ...


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
                expand: Optional[str] = None, 
                **kwargs: Any
            ) -> SavingsPlanModel: ...

        @distributed_trace
        def list_by_billing_account(
                self, 
                billing_account_name: str, 
                filter: Optional[str] = None, 
                order_by: Optional[str] = None, 
                skiptoken: Optional[float] = None, 
                take: Optional[float] = None, 
                selected_state: Optional[str] = None, 
                refresh_summary: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncIterable[SavingsPlanModel]: ...

        @distributed_trace
        def list_by_savings_plan_order(
                self, 
                billing_account_name: str, 
                savings_plan_order_id: str, 
                **kwargs: Any
            ) -> AsyncIterable[SavingsPlanModel]: ...

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
                filter: Optional[str] = None, 
                search: Optional[str] = None, 
                **kwargs: Any
            ) -> TransactionSummary: ...

        @distributed_trace
        def list_by_billing_profile(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                period_start_date: date, 
                period_end_date: date, 
                type: Union[str, TransactionType], 
                filter: Optional[str] = None, 
                order_by: Optional[str] = None, 
                top: Optional[int] = None, 
                skip: Optional[int] = None, 
                count: Optional[bool] = None, 
                search: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncIterable[Transaction]: ...

        @distributed_trace
        def list_by_customer(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                customer_name: str, 
                period_start_date: date, 
                period_end_date: date, 
                type: Union[str, TransactionType], 
                filter: Optional[str] = None, 
                order_by: Optional[str] = None, 
                top: Optional[int] = None, 
                skip: Optional[int] = None, 
                count: Optional[bool] = None, 
                search: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncIterable[Transaction]: ...

        @distributed_trace
        def list_by_invoice(
                self, 
                billing_account_name: str, 
                invoice_name: str, 
                filter: Optional[str] = None, 
                order_by: Optional[str] = None, 
                top: Optional[int] = None, 
                skip: Optional[int] = None, 
                count: Optional[bool] = None, 
                search: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncIterable[Transaction]: ...

        @distributed_trace
        def list_by_invoice_section(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                invoice_section_name: str, 
                period_start_date: date, 
                period_end_date: date, 
                type: Union[str, TransactionType], 
                filter: Optional[str] = None, 
                order_by: Optional[str] = None, 
                top: Optional[int] = None, 
                skip: Optional[int] = None, 
                count: Optional[bool] = None, 
                search: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncIterable[Transaction]: ...


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
            ) -> AsyncIterable[TransferDetails]: ...


namespace azure.mgmt.billing.models

    class azure.mgmt.billing.models.AcceptTransferRequest(Model):
        product_details: list[ProductDetails]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                product_details: Optional[List[ProductDetails]] = ..., 
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


    class azure.mgmt.billing.models.AddressDetails(Model):
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

        def __eq__(self, other: Any) -> bool: ...

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


    class azure.mgmt.billing.models.AddressValidationResponse(Model):
        status: Union[str, AddressValidationStatus]
        suggested_addresses: list[AddressDetails]
        validation_message: str

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


    class azure.mgmt.billing.models.AddressValidationStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INVALID = "Invalid"
        OTHER = "Other"
        VALID = "Valid"


    class azure.mgmt.billing.models.Agreement(ProxyResourceWithTags):
        id: str
        name: str
        properties: AgreementProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[AgreementProperties] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
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


    class azure.mgmt.billing.models.AgreementListResult(Model):
        next_link: str
        value: list[Agreement]

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


    class azure.mgmt.billing.models.AgreementProperties(Model):
        acceptance_mode: Union[str, AcceptanceMode]
        agreement_link: str
        billing_profile_info: list[BillingProfileInfo]
        category: Union[str, Category]
        display_name: str
        effective_date: datetime
        expiration_date: datetime
        lead_billing_account_name: str
        participants: list[Participant]
        status: str

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


    class azure.mgmt.billing.models.AgreementType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ENTERPRISE_AGREEMENT = "EnterpriseAgreement"
        MICROSOFT_CUSTOMER_AGREEMENT = "MicrosoftCustomerAgreement"
        MICROSOFT_ONLINE_SERVICES_PROGRAM = "MicrosoftOnlineServicesProgram"
        MICROSOFT_PARTNER_AGREEMENT = "MicrosoftPartnerAgreement"
        OTHER = "Other"


    class azure.mgmt.billing.models.Amount(Model):
        currency: str
        value: float

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


    class azure.mgmt.billing.models.AppliedScopeProperties(Model):
        display_name: str
        management_group_id: str
        resource_group_id: str
        subscription_id: str
        tenant_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                display_name: Optional[str] = ..., 
                management_group_id: Optional[str] = ..., 
                resource_group_id: Optional[str] = ..., 
                subscription_id: Optional[str] = ..., 
                tenant_id: Optional[str] = ..., 
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


    class azure.mgmt.billing.models.AppliedScopeType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MANAGEMENT_GROUP = "ManagementGroup"
        SHARED = "Shared"
        SINGLE = "Single"


    class azure.mgmt.billing.models.AssociatedTenant(ProxyResourceWithTags):
        id: str
        name: str
        properties: AssociatedTenantProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[AssociatedTenantProperties] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
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


    class azure.mgmt.billing.models.AssociatedTenantListResult(Model):
        next_link: str
        value: list[AssociatedTenant]

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


    class azure.mgmt.billing.models.AssociatedTenantProperties(Model):
        billing_management_state: Union[str, BillingManagementTenantState]
        display_name: str
        provisioning_billing_request_id: str
        provisioning_management_state: Union[str, ProvisioningTenantState]
        provisioning_state: Union[str, ProvisioningState]
        tenant_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                billing_management_state: Optional[Union[str, BillingManagementTenantState]] = ..., 
                display_name: Optional[str] = ..., 
                provisioning_management_state: Optional[Union[str, ProvisioningTenantState]] = ..., 
                tenant_id: Optional[str] = ..., 
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


    class azure.mgmt.billing.models.AutoRenew(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        OFF = "Off"
        ON = "On"


    class azure.mgmt.billing.models.AvailableBalance(ProxyResourceWithTags):
        id: str
        name: str
        properties: AvailableBalanceProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[AvailableBalanceProperties] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
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


    class azure.mgmt.billing.models.AvailableBalanceProperties(Model):
        amount: AvailableBalancePropertiesAmount
        payments_on_account: list[PaymentOnAccount]
        total_payments_on_account: AvailableBalancePropertiesTotalPaymentsOnAccount

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                amount: Optional[AvailableBalancePropertiesAmount] = ..., 
                total_payments_on_account: Optional[AvailableBalancePropertiesTotalPaymentsOnAccount] = ..., 
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


    class azure.mgmt.billing.models.AvailableBalancePropertiesAmount(Amount):
        currency: str
        value: float

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


    class azure.mgmt.billing.models.AvailableBalancePropertiesTotalPaymentsOnAccount(Amount):
        currency: str
        value: float

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


    class azure.mgmt.billing.models.AzurePlan(Model):
        product_id: str
        sku_description: str
        sku_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                product_id: Optional[str] = ..., 
                sku_description: Optional[str] = ..., 
                sku_id: Optional[str] = ..., 
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


    class azure.mgmt.billing.models.Beneficiary(Model):
        object_id: str
        tenant_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                object_id: Optional[str] = ..., 
                tenant_id: Optional[str] = ..., 
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


    class azure.mgmt.billing.models.BillingAccount(ProxyResourceWithTags):
        id: str
        name: str
        properties: BillingAccountProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[BillingAccountProperties] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
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


    class azure.mgmt.billing.models.BillingAccountListResult(Model):
        next_link: str
        value: list[BillingAccount]

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


    class azure.mgmt.billing.models.BillingAccountPatch(ProxyResourceWithTags):
        id: str
        name: str
        properties: BillingAccountProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[BillingAccountProperties] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
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


    class azure.mgmt.billing.models.BillingAccountPolicy(ProxyResourceWithTags):
        id: str
        name: str
        properties: BillingAccountPolicyProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[BillingAccountPolicyProperties] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
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


    class azure.mgmt.billing.models.BillingAccountPolicyProperties(Model):
        enterprise_agreement_policies: BillingAccountPolicyPropertiesEnterpriseAgreementPolicies
        marketplace_purchases: Union[str, MarketplacePurchasesPolicy]
        policies: list[PolicySummary]
        provisioning_state: Union[str, ProvisioningState]
        reservation_purchases: Union[str, ReservationPurchasesPolicy]
        savings_plan_purchases: Union[str, SavingsPlanPurchasesPolicy]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                enterprise_agreement_policies: Optional[BillingAccountPolicyPropertiesEnterpriseAgreementPolicies] = ..., 
                marketplace_purchases: Optional[Union[str, MarketplacePurchasesPolicy]] = ..., 
                policies: Optional[List[PolicySummary]] = ..., 
                reservation_purchases: Optional[Union[str, ReservationPurchasesPolicy]] = ..., 
                savings_plan_purchases: Optional[Union[str, SavingsPlanPurchasesPolicy]] = ..., 
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


    class azure.mgmt.billing.models.BillingAccountPolicyPropertiesEnterpriseAgreementPolicies(EnterpriseAgreementPolicies):
        account_owner_view_charges: Union[str, EnrollmentAccountOwnerViewCharges]
        authentication_type: Union[str, EnrollmentAuthLevelState]
        department_admin_view_charges: Union[str, EnrollmentDepartmentAdminViewCharges]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                account_owner_view_charges: Optional[Union[str, EnrollmentAccountOwnerViewCharges]] = ..., 
                authentication_type: Optional[Union[str, EnrollmentAuthLevelState]] = ..., 
                department_admin_view_charges: Optional[Union[str, EnrollmentDepartmentAdminViewCharges]] = ..., 
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


    class azure.mgmt.billing.models.BillingAccountProperties(Model):
        account_status: Union[str, AccountStatus]
        account_status_reason_code: Union[str, BillingAccountStatusReasonCode]
        account_sub_type: Union[str, AccountSubType]
        account_type: Union[str, AccountType]
        agreement_type: Union[str, AgreementType]
        billing_relationship_types: Union[list[str, BillingRelationshipType]]
        display_name: str
        enrollment_details: BillingAccountPropertiesEnrollmentDetails
        has_no_billing_profiles: bool
        has_read_access: bool
        notification_email_address: str
        primary_billing_tenant_id: str
        provisioning_state: Union[str, ProvisioningState]
        qualifications: list[str]
        registration_number: BillingAccountPropertiesRegistrationNumber
        sold_to: BillingAccountPropertiesSoldTo
        tax_ids: list[TaxIdentifier]

        def __eq__(self, other: Any) -> bool: ...

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
                tax_ids: Optional[List[TaxIdentifier]] = ..., 
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

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                end_date: Optional[datetime] = ..., 
                indirect_relationship_info: Optional[EnrollmentDetailsIndirectRelationshipInfo] = ..., 
                po_number: Optional[str] = ..., 
                start_date: Optional[datetime] = ..., 
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


    class azure.mgmt.billing.models.BillingAccountPropertiesRegistrationNumber(RegistrationNumber):
        id: str
        required: bool
        type: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
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

        def __eq__(self, other: Any) -> bool: ...

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


    class azure.mgmt.billing.models.BillingPermission(Model):
        actions: list[str]
        not_actions: list[str]

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


    class azure.mgmt.billing.models.BillingPermissionListResult(Model):
        next_link: str
        value: list[BillingPermission]

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


    class azure.mgmt.billing.models.BillingPlan(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        P1_M = "P1M"


    class azure.mgmt.billing.models.BillingPlanInformation(Model):
        next_payment_due_date: date
        pricing_currency_total: Price
        start_date: date
        transactions: list[PaymentDetail]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_payment_due_date: Optional[date] = ..., 
                pricing_currency_total: Optional[Price] = ..., 
                start_date: Optional[date] = ..., 
                transactions: Optional[List[PaymentDetail]] = ..., 
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


    class azure.mgmt.billing.models.BillingProfile(ProxyResourceWithTags):
        id: str
        name: str
        properties: BillingProfileProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[BillingProfileProperties] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
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


    class azure.mgmt.billing.models.BillingProfileInfo(Model):
        billing_account_id: str
        billing_profile_display_name: str
        billing_profile_id: str
        billing_profile_system_id: str
        indirect_relationship_organization_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                billing_account_id: Optional[str] = ..., 
                billing_profile_display_name: Optional[str] = ..., 
                billing_profile_id: Optional[str] = ..., 
                billing_profile_system_id: Optional[str] = ..., 
                indirect_relationship_organization_name: Optional[str] = ..., 
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


    class azure.mgmt.billing.models.BillingProfileListResult(Model):
        next_link: str
        value: list[BillingProfile]

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


    class azure.mgmt.billing.models.BillingProfilePolicy(ProxyResourceWithTags):
        id: str
        name: str
        properties: BillingProfilePolicyProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[BillingProfilePolicyProperties] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
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


    class azure.mgmt.billing.models.BillingProfilePolicyProperties(Model):
        enterprise_agreement_policies: BillingProfilePolicyPropertiesEnterpriseAgreementPolicies
        invoice_section_label_management: Union[str, InvoiceSectionLabelManagementPolicy]
        marketplace_purchases: Union[str, MarketplacePurchasesPolicy]
        policies: list[PolicySummary]
        provisioning_state: Union[str, ProvisioningState]
        reservation_purchases: Union[str, ReservationPurchasesPolicy]
        savings_plan_purchases: Union[str, SavingsPlanPurchasesPolicy]
        view_charges: Union[str, ViewChargesPolicy]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                enterprise_agreement_policies: Optional[BillingProfilePolicyPropertiesEnterpriseAgreementPolicies] = ..., 
                invoice_section_label_management: Optional[Union[str, InvoiceSectionLabelManagementPolicy]] = ..., 
                marketplace_purchases: Optional[Union[str, MarketplacePurchasesPolicy]] = ..., 
                policies: Optional[List[PolicySummary]] = ..., 
                reservation_purchases: Optional[Union[str, ReservationPurchasesPolicy]] = ..., 
                savings_plan_purchases: Optional[Union[str, SavingsPlanPurchasesPolicy]] = ..., 
                view_charges: Optional[Union[str, ViewChargesPolicy]] = ..., 
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


    class azure.mgmt.billing.models.BillingProfilePolicyPropertiesEnterpriseAgreementPolicies(EnterpriseAgreementPolicies):
        account_owner_view_charges: Union[str, EnrollmentAccountOwnerViewCharges]
        authentication_type: Union[str, EnrollmentAuthLevelState]
        department_admin_view_charges: Union[str, EnrollmentDepartmentAdminViewCharges]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                account_owner_view_charges: Optional[Union[str, EnrollmentAccountOwnerViewCharges]] = ..., 
                authentication_type: Optional[Union[str, EnrollmentAuthLevelState]] = ..., 
                department_admin_view_charges: Optional[Union[str, EnrollmentDepartmentAdminViewCharges]] = ..., 
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


    class azure.mgmt.billing.models.BillingProfileProperties(Model):
        bill_to: BillingProfilePropertiesBillTo
        billing_relationship_type: Union[str, BillingRelationshipType]
        currency: str
        current_payment_term: BillingProfilePropertiesCurrentPaymentTerm
        display_name: str
        enabled_azure_plans: list[AzurePlan]
        has_read_access: bool
        indirect_relationship_info: BillingProfilePropertiesIndirectRelationshipInfo
        invoice_day: int
        invoice_email_opt_in: bool
        invoice_recipients: list[str]
        other_payment_terms: list[PaymentTerm]
        po_number: str
        provisioning_state: Union[str, ProvisioningState]
        ship_to: BillingProfilePropertiesShipTo
        sold_to: BillingProfilePropertiesSoldTo
        spending_limit: Union[str, SpendingLimit]
        spending_limit_details: list[SpendingLimitDetails]
        status: Union[str, BillingProfileStatus]
        status_reason_code: Union[str, BillingProfileStatusReasonCode]
        system_id: str
        tags: dict[str, str]
        target_clouds: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                bill_to: Optional[BillingProfilePropertiesBillTo] = ..., 
                current_payment_term: Optional[BillingProfilePropertiesCurrentPaymentTerm] = ..., 
                display_name: Optional[str] = ..., 
                enabled_azure_plans: Optional[List[AzurePlan]] = ..., 
                indirect_relationship_info: Optional[BillingProfilePropertiesIndirectRelationshipInfo] = ..., 
                invoice_email_opt_in: Optional[bool] = ..., 
                invoice_recipients: Optional[List[str]] = ..., 
                po_number: Optional[str] = ..., 
                ship_to: Optional[BillingProfilePropertiesShipTo] = ..., 
                sold_to: Optional[BillingProfilePropertiesSoldTo] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
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

        def __eq__(self, other: Any) -> bool: ...

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


    class azure.mgmt.billing.models.BillingProfilePropertiesCurrentPaymentTerm(PaymentTerm):
        end_date: datetime
        is_default: bool
        start_date: datetime
        term: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                end_date: Optional[datetime] = ..., 
                start_date: Optional[datetime] = ..., 
                term: Optional[str] = ..., 
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


    class azure.mgmt.billing.models.BillingProfilePropertiesIndirectRelationshipInfo(IndirectRelationshipInfo):
        billing_account_name: str
        billing_profile_name: str
        display_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                billing_account_name: Optional[str] = ..., 
                billing_profile_name: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
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

        def __eq__(self, other: Any) -> bool: ...

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

        def __eq__(self, other: Any) -> bool: ...

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


    class azure.mgmt.billing.models.BillingProperty(ProxyResourceWithTags):
        id: str
        name: str
        properties: BillingPropertyProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[BillingPropertyProperties] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
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


    class azure.mgmt.billing.models.BillingPropertyProperties(Model):
        account_admin_notification_email_address: str
        billing_account_agreement_type: Union[str, AgreementType]
        billing_account_display_name: str
        billing_account_id: str
        billing_account_sold_to_country: str
        billing_account_status: Union[str, AccountStatus]
        billing_account_status_reason_code: Union[str, BillingAccountStatusReasonCode]
        billing_account_sub_type: Union[str, AccountSubType]
        billing_account_type: Union[str, AccountType]
        billing_currency: str
        billing_profile_display_name: str
        billing_profile_id: str
        billing_profile_payment_method_family: Union[str, PaymentMethodFamily]
        billing_profile_payment_method_type: str
        billing_profile_spending_limit: Union[str, SpendingLimit]
        billing_profile_spending_limit_details: list[SpendingLimitDetails]
        billing_profile_status: Union[str, BillingProfileStatus]
        billing_profile_status_reason_code: Union[str, BillingProfileStatusReasonCode]
        billing_tenant_id: str
        cost_center: str
        customer_display_name: str
        customer_id: str
        customer_status: Union[str, CustomerStatus]
        enrollment_details: BillingPropertyPropertiesEnrollmentDetails
        invoice_section_display_name: str
        invoice_section_id: str
        invoice_section_status: Union[str, InvoiceSectionState]
        invoice_section_status_reason_code: Union[str, InvoiceSectionStateReasonCode]
        is_account_admin: bool
        is_transitioned_billing_account: bool
        product_id: str
        product_name: str
        sku_description: str
        sku_id: str
        subscription_billing_status: Union[str, BillingSubscriptionStatus]
        subscription_billing_status_details: list[BillingSubscriptionStatusDetails]
        subscription_billing_type: Union[str, SubscriptionBillingType]
        subscription_service_usage_address: BillingPropertyPropertiesSubscriptionServiceUsageAddress
        subscription_workload_type: Union[str, SubscriptionWorkloadType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                cost_center: Optional[str] = ..., 
                enrollment_details: Optional[BillingPropertyPropertiesEnrollmentDetails] = ..., 
                subscription_service_usage_address: Optional[BillingPropertyPropertiesSubscriptionServiceUsageAddress] = ..., 
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


    class azure.mgmt.billing.models.BillingPropertyPropertiesEnrollmentDetails(SubscriptionEnrollmentDetails):
        department_display_name: str
        department_id: str
        enrollment_account_display_name: str
        enrollment_account_id: str
        enrollment_account_status: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                department_display_name: Optional[str] = ..., 
                department_id: Optional[str] = ..., 
                enrollment_account_display_name: Optional[str] = ..., 
                enrollment_account_id: Optional[str] = ..., 
                enrollment_account_status: Optional[str] = ..., 
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

        def __eq__(self, other: Any) -> bool: ...

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


    class azure.mgmt.billing.models.BillingRelationshipType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CSP_CUSTOMER = "CSPCustomer"
        CSP_PARTNER = "CSPPartner"
        DIRECT = "Direct"
        INDIRECT_CUSTOMER = "IndirectCustomer"
        INDIRECT_PARTNER = "IndirectPartner"
        OTHER = "Other"


    class azure.mgmt.billing.models.BillingRequest(ProxyResourceWithTags):
        id: str
        name: str
        properties: BillingRequestProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[BillingRequestProperties] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
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


    class azure.mgmt.billing.models.BillingRequestListResult(Model):
        next_link: str
        value: list[BillingRequest]

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


    class azure.mgmt.billing.models.BillingRequestProperties(Model):
        additional_information: dict[str, str]
        billing_account_display_name: str
        billing_account_id: str
        billing_account_name: str
        billing_account_primary_billing_tenant_id: str
        billing_profile_display_name: str
        billing_profile_id: str
        billing_profile_name: str
        billing_scope: str
        created_by: BillingRequestPropertiesCreatedBy
        creation_date: datetime
        customer_display_name: str
        customer_id: str
        customer_name: str
        decision_reason: str
        expiration_date: datetime
        invoice_section_display_name: str
        invoice_section_id: str
        invoice_section_name: str
        justification: str
        last_updated_by: BillingRequestPropertiesLastUpdatedBy
        last_updated_date: datetime
        provisioning_state: Union[str, ProvisioningState]
        recipients: list[Principal]
        request_scope: str
        reviewal_date: datetime
        reviewed_by: BillingRequestPropertiesReviewedBy
        status: Union[str, BillingRequestStatus]
        subscription_display_name: str
        subscription_id: str
        subscription_name: str
        type: Union[str, BillingRequestType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                additional_information: Optional[Dict[str, str]] = ..., 
                created_by: Optional[BillingRequestPropertiesCreatedBy] = ..., 
                decision_reason: Optional[str] = ..., 
                justification: Optional[str] = ..., 
                last_updated_by: Optional[BillingRequestPropertiesLastUpdatedBy] = ..., 
                recipients: Optional[List[Principal]] = ..., 
                request_scope: Optional[str] = ..., 
                reviewed_by: Optional[BillingRequestPropertiesReviewedBy] = ..., 
                status: Optional[Union[str, BillingRequestStatus]] = ..., 
                type: Optional[Union[str, BillingRequestType]] = ..., 
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


    class azure.mgmt.billing.models.BillingRequestPropertiesCreatedBy(Principal):
        object_id: str
        tenant_id: str
        upn: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                object_id: Optional[str] = ..., 
                tenant_id: Optional[str] = ..., 
                upn: Optional[str] = ..., 
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


    class azure.mgmt.billing.models.BillingRequestPropertiesLastUpdatedBy(Principal):
        object_id: str
        tenant_id: str
        upn: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                object_id: Optional[str] = ..., 
                tenant_id: Optional[str] = ..., 
                upn: Optional[str] = ..., 
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


    class azure.mgmt.billing.models.BillingRequestPropertiesReviewedBy(Principal):
        object_id: str
        tenant_id: str
        upn: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                object_id: Optional[str] = ..., 
                tenant_id: Optional[str] = ..., 
                upn: Optional[str] = ..., 
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


    class azure.mgmt.billing.models.BillingRoleAssignment(ProxyResourceWithTags):
        id: str
        name: str
        properties: BillingRoleAssignmentProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[BillingRoleAssignmentProperties] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
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


    class azure.mgmt.billing.models.BillingRoleAssignmentListResult(Model):
        next_link: str
        value: list[BillingRoleAssignment]

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


    class azure.mgmt.billing.models.BillingRoleAssignmentProperties(Model):
        billing_account_display_name: str
        billing_account_id: str
        billing_profile_display_name: str
        billing_profile_id: str
        billing_request_id: str
        created_by_principal_id: str
        created_by_principal_puid: str
        created_by_principal_tenant_id: str
        created_by_user_email_address: str
        created_on: datetime
        customer_display_name: str
        customer_id: str
        invoice_section_display_name: str
        invoice_section_id: str
        modified_by_principal_id: str
        modified_by_principal_puid: str
        modified_by_principal_tenant_id: str
        modified_by_user_email_address: str
        modified_on: datetime
        principal_display_name: str
        principal_id: str
        principal_puid: str
        principal_tenant_id: str
        principal_tenant_name: str
        principal_type: Union[str, PrincipalType]
        provisioning_state: Union[str, ProvisioningState]
        role_definition_id: str
        scope: str
        user_authentication_type: str
        user_email_address: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                principal_id: Optional[str] = ..., 
                principal_puid: Optional[str] = ..., 
                principal_tenant_id: Optional[str] = ..., 
                role_definition_id: str, 
                scope: Optional[str] = ..., 
                user_authentication_type: Optional[str] = ..., 
                user_email_address: Optional[str] = ..., 
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


    class azure.mgmt.billing.models.BillingRoleDefinition(ProxyResourceWithTags):
        id: str
        name: str
        properties: BillingRoleDefinitionProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[BillingRoleDefinitionProperties] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
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


    class azure.mgmt.billing.models.BillingRoleDefinitionListResult(Model):
        next_link: str
        value: list[BillingRoleDefinition]

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


    class azure.mgmt.billing.models.BillingRoleDefinitionProperties(Model):
        description: str
        permissions: list[BillingPermission]
        role_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                role_name: str, 
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


    class azure.mgmt.billing.models.BillingSubscription(ProxyResourceWithTags):
        auto_renew: Union[str, AutoRenew]
        beneficiary: Beneficiary
        beneficiary_tenant_id: str
        billing_frequency: str
        billing_policies: dict[str, str]
        billing_profile_display_name: str
        billing_profile_id: str
        billing_profile_name: str
        consumption_cost_center: str
        customer_display_name: str
        customer_id: str
        customer_name: str
        display_name: str
        enrollment_account_display_name: str
        enrollment_account_id: str
        enrollment_account_start_date: datetime
        id: str
        invoice_section_display_name: str
        invoice_section_id: str
        invoice_section_name: str
        last_month_charges: Amount
        month_to_date_charges: Amount
        name: str
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
        subscription_enrollment_account_status: Union[str, SubscriptionEnrollmentAccountStatus]
        subscription_id: str
        suspension_reason_details: list[BillingSubscriptionStatusDetails]
        suspension_reasons: list[str]
        system_data: SystemData
        system_overrides: SystemOverrides
        tags: dict[str, str]
        term_duration: str
        term_end_date: datetime
        term_start_date: datetime
        type: str

        def __eq__(self, other: Any) -> bool: ...

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
                tags: Optional[Dict[str, str]] = ..., 
                term_duration: Optional[str] = ..., 
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


    class azure.mgmt.billing.models.BillingSubscriptionAlias(ProxyResourceWithTags):
        auto_renew: Union[str, AutoRenew]
        beneficiary: Beneficiary
        beneficiary_tenant_id: str
        billing_frequency: str
        billing_policies: dict[str, str]
        billing_profile_display_name: str
        billing_profile_id: str
        billing_profile_name: str
        billing_subscription_id: str
        consumption_cost_center: str
        customer_display_name: str
        customer_id: str
        customer_name: str
        display_name: str
        enrollment_account_display_name: str
        enrollment_account_id: str
        enrollment_account_start_date: datetime
        id: str
        invoice_section_display_name: str
        invoice_section_id: str
        invoice_section_name: str
        last_month_charges: Amount
        month_to_date_charges: Amount
        name: str
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
        subscription_enrollment_account_status: Union[str, SubscriptionEnrollmentAccountStatus]
        subscription_id: str
        suspension_reason_details: list[BillingSubscriptionStatusDetails]
        suspension_reasons: list[str]
        system_data: SystemData
        system_overrides: SystemOverrides
        tags: dict[str, str]
        term_duration: str
        term_end_date: datetime
        term_start_date: datetime
        type: str

        def __eq__(self, other: Any) -> bool: ...

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
                tags: Optional[Dict[str, str]] = ..., 
                term_duration: Optional[str] = ..., 
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


    class azure.mgmt.billing.models.BillingSubscriptionAliasListResult(Model):
        next_link: str
        value: list[BillingSubscriptionAlias]

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


    class azure.mgmt.billing.models.BillingSubscriptionAliasProperties(BillingSubscriptionProperties):
        auto_renew: Union[str, AutoRenew]
        beneficiary: Beneficiary
        beneficiary_tenant_id: str
        billing_frequency: str
        billing_policies: dict[str, str]
        billing_profile_display_name: str
        billing_profile_id: str
        billing_profile_name: str
        billing_subscription_id: str
        consumption_cost_center: str
        customer_display_name: str
        customer_id: str
        customer_name: str
        display_name: str
        enrollment_account_display_name: str
        enrollment_account_id: str
        enrollment_account_start_date: datetime
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
        subscription_enrollment_account_status: Union[str, SubscriptionEnrollmentAccountStatus]
        subscription_id: str
        suspension_reason_details: list[BillingSubscriptionStatusDetails]
        suspension_reasons: list[str]
        system_overrides: SystemOverrides
        term_duration: str
        term_end_date: datetime
        term_start_date: datetime

        def __eq__(self, other: Any) -> bool: ...

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
                term_duration: Optional[str] = ..., 
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


    class azure.mgmt.billing.models.BillingSubscriptionListResult(Model):
        next_link: str
        total_count: int
        value: list[BillingSubscription]

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


    class azure.mgmt.billing.models.BillingSubscriptionMergeRequest(Model):
        quantity: int
        target_billing_subscription_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                quantity: Optional[int] = ..., 
                target_billing_subscription_name: Optional[str] = ..., 
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


    class azure.mgmt.billing.models.BillingSubscriptionOperationStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LOCKED_FOR_UPDATE = "LockedForUpdate"
        NONE = "None"
        OTHER = "Other"


    class azure.mgmt.billing.models.BillingSubscriptionPatch(ProxyResourceWithTags):
        auto_renew: Union[str, AutoRenew]
        beneficiary: Beneficiary
        beneficiary_tenant_id: str
        billing_frequency: str
        billing_policies: dict[str, str]
        billing_profile_display_name: str
        billing_profile_id: str
        billing_profile_name: str
        consumption_cost_center: str
        customer_display_name: str
        customer_id: str
        customer_name: str
        display_name: str
        enrollment_account_display_name: str
        enrollment_account_id: str
        enrollment_account_start_date: datetime
        id: str
        invoice_section_display_name: str
        invoice_section_id: str
        invoice_section_name: str
        last_month_charges: Amount
        month_to_date_charges: Amount
        name: str
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
        subscription_enrollment_account_status: Union[str, SubscriptionEnrollmentAccountStatus]
        subscription_id: str
        suspension_reason_details: list[BillingSubscriptionStatusDetails]
        suspension_reasons: list[str]
        system_data: SystemData
        system_overrides: SystemOverrides
        tags: dict[str, str]
        term_duration: str
        term_end_date: datetime
        term_start_date: datetime
        type: str

        def __eq__(self, other: Any) -> bool: ...

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
                tags: Optional[Dict[str, str]] = ..., 
                term_duration: Optional[str] = ..., 
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


    class azure.mgmt.billing.models.BillingSubscriptionProperties(Model):
        auto_renew: Union[str, AutoRenew]
        beneficiary: Beneficiary
        beneficiary_tenant_id: str
        billing_frequency: str
        billing_policies: dict[str, str]
        billing_profile_display_name: str
        billing_profile_id: str
        billing_profile_name: str
        consumption_cost_center: str
        customer_display_name: str
        customer_id: str
        customer_name: str
        display_name: str
        enrollment_account_display_name: str
        enrollment_account_id: str
        enrollment_account_start_date: datetime
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
        subscription_enrollment_account_status: Union[str, SubscriptionEnrollmentAccountStatus]
        subscription_id: str
        suspension_reason_details: list[BillingSubscriptionStatusDetails]
        suspension_reasons: list[str]
        system_overrides: SystemOverrides
        term_duration: str
        term_end_date: datetime
        term_start_date: datetime

        def __eq__(self, other: Any) -> bool: ...

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
                term_duration: Optional[str] = ..., 
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


    class azure.mgmt.billing.models.BillingSubscriptionSplitRequest(Model):
        billing_frequency: str
        quantity: int
        target_product_type_id: str
        target_sku_id: str
        term_duration: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                billing_frequency: Optional[str] = ..., 
                quantity: Optional[int] = ..., 
                target_product_type_id: Optional[str] = ..., 
                target_sku_id: Optional[str] = ..., 
                term_duration: Optional[str] = ..., 
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


    class azure.mgmt.billing.models.BillingSubscriptionStatusDetails(Model):
        effective_date: datetime
        reason: Union[str, SubscriptionStatusReason]

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


    class azure.mgmt.billing.models.CancelSubscriptionRequest(Model):
        cancellation_reason: Union[str, CancellationReason]
        customer_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                cancellation_reason: Union[str, CancellationReason], 
                customer_id: Optional[str] = ..., 
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


    class azure.mgmt.billing.models.CheckAccessRequest(Model):
        actions: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                actions: Optional[List[str]] = ..., 
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


    class azure.mgmt.billing.models.CheckAccessResponse(Model):
        access_decision: Union[str, AccessDecision]
        action: str

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


    class azure.mgmt.billing.models.Commitment(Price):
        amount: float
        currency_code: str
        grain: Union[str, CommitmentGrain]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                amount: Optional[float] = ..., 
                currency_code: Optional[str] = ..., 
                grain: Optional[Union[str, CommitmentGrain]] = ..., 
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


    class azure.mgmt.billing.models.Customer(ProxyResourceWithTags):
        id: str
        name: str
        properties: CustomerProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[CustomerProperties] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
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


    class azure.mgmt.billing.models.CustomerListResult(Model):
        next_link: str
        value: list[Customer]

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


    class azure.mgmt.billing.models.CustomerPolicy(ProxyResourceWithTags):
        id: str
        name: str
        properties: CustomerPolicyProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[CustomerPolicyProperties] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
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


    class azure.mgmt.billing.models.CustomerPolicyProperties(Model):
        policies: list[PolicySummary]
        provisioning_state: Union[str, ProvisioningState]
        view_charges: Union[str, ViewChargesPolicy]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                policies: Optional[List[PolicySummary]] = ..., 
                view_charges: Union[str, ViewChargesPolicy], 
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


    class azure.mgmt.billing.models.CustomerProperties(Model):
        billing_profile_display_name: str
        billing_profile_id: str
        display_name: str
        enabled_azure_plans: list[AzurePlan]
        resellers: list[Reseller]
        status: Union[str, CustomerStatus]
        system_id: str
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                enabled_azure_plans: Optional[List[AzurePlan]] = ..., 
                resellers: Optional[List[Reseller]] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
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


    class azure.mgmt.billing.models.DeleteBillingProfileEligibilityDetail(Model):
        code: Union[str, DeleteBillingProfileEligibilityCode]
        message: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                code: Optional[Union[str, DeleteBillingProfileEligibilityCode]] = ..., 
                message: Optional[str] = ..., 
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


    class azure.mgmt.billing.models.DeleteBillingProfileEligibilityResult(Model):
        eligibility_details: list[DeleteBillingProfileEligibilityDetail]
        eligibility_status: Union[str, DeleteBillingProfileEligibilityStatus]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                eligibility_details: Optional[List[DeleteBillingProfileEligibilityDetail]] = ..., 
                eligibility_status: Optional[Union[str, DeleteBillingProfileEligibilityStatus]] = ..., 
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


    class azure.mgmt.billing.models.DeleteBillingProfileEligibilityStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALLOWED = "Allowed"
        NOT_ALLOWED = "NotAllowed"


    class azure.mgmt.billing.models.DeleteInvoiceSectionEligibilityCode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE_AZURE_PLANS = "ActiveAzurePlans"
        ACTIVE_BILLING_SUBSCRIPTIONS = "ActiveBillingSubscriptions"
        LAST_INVOICE_SECTION = "LastInvoiceSection"
        OTHER = "Other"
        RESERVED_INSTANCES = "ReservedInstances"


    class azure.mgmt.billing.models.DeleteInvoiceSectionEligibilityDetail(Model):
        code: Union[str, DeleteInvoiceSectionEligibilityCode]
        message: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                code: Optional[Union[str, DeleteInvoiceSectionEligibilityCode]] = ..., 
                message: Optional[str] = ..., 
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


    class azure.mgmt.billing.models.DeleteInvoiceSectionEligibilityResult(Model):
        eligibility_details: list[DeleteInvoiceSectionEligibilityDetail]
        eligibility_status: Union[str, DeleteInvoiceSectionEligibilityStatus]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                eligibility_details: Optional[List[DeleteInvoiceSectionEligibilityDetail]] = ..., 
                eligibility_status: Optional[Union[str, DeleteInvoiceSectionEligibilityStatus]] = ..., 
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


    class azure.mgmt.billing.models.DeleteInvoiceSectionEligibilityStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALLOWED = "Allowed"
        NOT_ALLOWED = "NotAllowed"


    class azure.mgmt.billing.models.Department(ProxyResourceWithTags):
        id: str
        name: str
        properties: DepartmentProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[DepartmentProperties] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
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


    class azure.mgmt.billing.models.DepartmentListResult(Model):
        next_link: str
        value: list[Department]

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


    class azure.mgmt.billing.models.DepartmentProperties(Model):
        cost_center: str
        display_name: str
        id: str
        status: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                cost_center: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
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


    class azure.mgmt.billing.models.DetailedTransferStatus(Model):
        error_details: TransferError
        product_id: str
        product_name: str
        product_type: Union[str, ProductType]
        sku_description: str
        transfer_status: Union[str, ProductTransferStatus]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                error_details: Optional[TransferError] = ..., 
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


    class azure.mgmt.billing.models.DocumentDownloadRequest(Model):
        document_name: str
        invoice_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                document_name: Optional[str] = ..., 
                invoice_name: Optional[str] = ..., 
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


    class azure.mgmt.billing.models.DocumentDownloadResult(Model):
        expiry_time: str
        url: str

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


    class azure.mgmt.billing.models.DocumentSource(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DRS = "DRS"
        ENF = "ENF"
        OTHER = "Other"


    class azure.mgmt.billing.models.EligibleProductType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_RESERVATION = "AzureReservation"
        DEV_TEST_AZURE_SUBSCRIPTION = "DevTestAzureSubscription"
        STANDARD_AZURE_SUBSCRIPTION = "StandardAzureSubscription"


    class azure.mgmt.billing.models.EnrollmentAccount(ProxyResourceWithTags):
        id: str
        name: str
        properties: EnrollmentAccountProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[EnrollmentAccountProperties] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
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


    class azure.mgmt.billing.models.EnrollmentAccountListResult(Model):
        next_link: str
        value: list[EnrollmentAccount]

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


    class azure.mgmt.billing.models.EnrollmentAccountOwnerViewCharges(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALLOWED = "Allowed"
        DISABLED = "Disabled"
        NOT_ALLOWED = "NotAllowed"
        OTHER = "Other"


    class azure.mgmt.billing.models.EnrollmentAccountProperties(Model):
        account_owner: str
        auth_type: str
        cost_center: str
        department_display_name: str
        department_id: str
        display_name: str
        end_date: datetime
        is_dev_test_enabled: bool
        start_date: datetime
        status: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                cost_center: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                is_dev_test_enabled: Optional[bool] = ..., 
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


    class azure.mgmt.billing.models.EnrollmentDetails(Model):
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

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                end_date: Optional[datetime] = ..., 
                indirect_relationship_info: Optional[EnrollmentDetailsIndirectRelationshipInfo] = ..., 
                po_number: Optional[str] = ..., 
                start_date: Optional[datetime] = ..., 
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


    class azure.mgmt.billing.models.EnrollmentDetailsIndirectRelationshipInfo(IndirectRelationshipInfo):
        billing_account_name: str
        billing_profile_name: str
        display_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                billing_account_name: Optional[str] = ..., 
                billing_profile_name: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
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


    class azure.mgmt.billing.models.EnterpriseAgreementPolicies(Model):
        account_owner_view_charges: Union[str, EnrollmentAccountOwnerViewCharges]
        authentication_type: Union[str, EnrollmentAuthLevelState]
        department_admin_view_charges: Union[str, EnrollmentDepartmentAdminViewCharges]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                account_owner_view_charges: Optional[Union[str, EnrollmentAccountOwnerViewCharges]] = ..., 
                authentication_type: Optional[Union[str, EnrollmentAuthLevelState]] = ..., 
                department_admin_view_charges: Optional[Union[str, EnrollmentDepartmentAdminViewCharges]] = ..., 
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


    class azure.mgmt.billing.models.ErrorAdditionalInfo(Model):
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


    class azure.mgmt.billing.models.ErrorDetail(Model):
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


    class azure.mgmt.billing.models.ErrorResponse(Model):
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


    class azure.mgmt.billing.models.ExtendedStatusDefinitionProperties(Model):
        subscription_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                subscription_id: Optional[str] = ..., 
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


    class azure.mgmt.billing.models.ExtendedStatusInfo(Model):
        message: str
        status_code: str
        subscription_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                message: Optional[str] = ..., 
                status_code: Optional[str] = ..., 
                subscription_id: Optional[str] = ..., 
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


    class azure.mgmt.billing.models.ExtendedTermOption(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        OPTED_IN = "Opted-In"
        OPTED_OUT = "Opted-Out"
        OTHER = "Other"


    class azure.mgmt.billing.models.ExternalReference(Model):
        id: str
        url: str

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


    class azure.mgmt.billing.models.FailedPayment(Model):
        date: datetime
        failed_payment_reason: Union[str, FailedPaymentReason]

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


    class azure.mgmt.billing.models.FailedPaymentReason(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BANK_DECLINED = "BankDeclined"
        CARD_EXPIRED = "CardExpired"
        INCORRECT_CARD_DETAILS = "IncorrectCardDetails"
        OTHER = "Other"


    class azure.mgmt.billing.models.IndirectRelationshipInfo(Model):
        billing_account_name: str
        billing_profile_name: str
        display_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                billing_account_name: Optional[str] = ..., 
                billing_profile_name: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
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


    class azure.mgmt.billing.models.InitiateTransferRequest(Model):
        recipient_email_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                recipient_email_id: Optional[str] = ..., 
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


    class azure.mgmt.billing.models.InitiatorCustomerType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EA = "EA"
        PARTNER = "Partner"


    class azure.mgmt.billing.models.InstanceFlexibility(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        OFF = "Off"
        ON = "On"


    class azure.mgmt.billing.models.Invoice(ProxyResourceWithTags):
        id: str
        name: str
        properties: InvoiceProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[InvoiceProperties] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
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


    class azure.mgmt.billing.models.InvoiceDocument(Model):
        document_numbers: list[str]
        external_url: str
        kind: Union[str, InvoiceDocumentType]
        name: str
        source: Union[str, DocumentSource]
        url: str

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


    class azure.mgmt.billing.models.InvoiceDocumentType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CREDIT_NOTE = "CreditNote"
        INVOICE = "Invoice"
        OTHER = "Other"
        SUMMARY = "Summary"
        TAX_RECEIPT = "TaxReceipt"
        TRANSACTIONS = "Transactions"
        VOID_NOTE = "VoidNote"


    class azure.mgmt.billing.models.InvoiceListResult(Model):
        next_link: str
        value: list[Invoice]

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


    class azure.mgmt.billing.models.InvoiceProperties(Model):
        amount_due: InvoicePropertiesAmountDue
        azure_prepayment_applied: InvoicePropertiesAzurePrepaymentApplied
        billed_amount: InvoicePropertiesBilledAmount
        billed_document_id: str
        billing_profile_display_name: str
        billing_profile_id: str
        credit_amount: InvoicePropertiesCreditAmount
        credit_for_document_id: str
        document_type: Union[str, InvoiceDocumentType]
        documents: list[InvoiceDocument]
        due_date: datetime
        failed_payments: list[FailedPayment]
        free_azure_credit_applied: InvoicePropertiesFreeAzureCreditApplied
        invoice_date: datetime
        invoice_period_end_date: datetime
        invoice_period_start_date: datetime
        invoice_type: Union[str, InvoiceType]
        is_monthly_invoice: bool
        payments: list[Payment]
        purchase_order_number: str
        rebill_details: InvoicePropertiesRebillDetails
        refund_details: InvoicePropertiesRefundDetails
        special_taxation_type: Union[str, SpecialTaxationType]
        status: Union[str, InvoiceStatus]
        sub_total: InvoicePropertiesSubTotal
        subscription_display_name: str
        subscription_id: str
        tax_amount: InvoicePropertiesTaxAmount
        total_amount: InvoicePropertiesTotalAmount

        def __eq__(self, other: Any) -> bool: ...

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
                total_amount: Optional[InvoicePropertiesTotalAmount] = ..., 
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


    class azure.mgmt.billing.models.InvoicePropertiesAmountDue(Amount):
        currency: str
        value: float

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


    class azure.mgmt.billing.models.InvoicePropertiesAzurePrepaymentApplied(Amount):
        currency: str
        value: float

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


    class azure.mgmt.billing.models.InvoicePropertiesBilledAmount(Amount):
        currency: str
        value: float

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


    class azure.mgmt.billing.models.InvoicePropertiesCreditAmount(Amount):
        currency: str
        value: float

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


    class azure.mgmt.billing.models.InvoicePropertiesFreeAzureCreditApplied(Amount):
        currency: str
        value: float

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


    class azure.mgmt.billing.models.InvoicePropertiesRebillDetails(RebillDetails):
        credit_note_document_id: str
        invoice_document_id: str
        rebill_details: RebillDetails

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

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                amount_refunded: Optional[RefundDetailsSummaryAmountRefunded] = ..., 
                amount_requested: Optional[RefundDetailsSummaryAmountRequested] = ..., 
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


    class azure.mgmt.billing.models.InvoicePropertiesSubTotal(Amount):
        currency: str
        value: float

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


    class azure.mgmt.billing.models.InvoicePropertiesTaxAmount(Amount):
        currency: str
        value: float

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


    class azure.mgmt.billing.models.InvoicePropertiesTotalAmount(Amount):
        currency: str
        value: float

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


    class azure.mgmt.billing.models.InvoiceSection(ProxyResourceWithTags):
        id: str
        name: str
        properties: InvoiceSectionProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[InvoiceSectionProperties] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
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


    class azure.mgmt.billing.models.InvoiceSectionLabelManagementPolicy(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALLOWED = "Allowed"
        NOT_ALLOWED = "NotAllowed"
        OTHER = "Other"


    class azure.mgmt.billing.models.InvoiceSectionListResult(Model):
        next_link: str
        value: list[InvoiceSection]

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


    class azure.mgmt.billing.models.InvoiceSectionProperties(Model):
        display_name: str
        provisioning_state: Union[str, ProvisioningState]
        reason_code: Union[str, InvoiceSectionStateReasonCode]
        state: Union[str, InvoiceSectionState]
        system_id: str
        tags: dict[str, str]
        target_cloud: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                display_name: Optional[str] = ..., 
                reason_code: Optional[Union[str, InvoiceSectionStateReasonCode]] = ..., 
                state: Optional[Union[str, InvoiceSectionState]] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                target_cloud: Optional[str] = ..., 
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


    class azure.mgmt.billing.models.InvoiceSectionWithCreateSubPermission(Model):
        billing_profile_display_name: str
        billing_profile_id: str
        billing_profile_spending_limit: Union[str, SpendingLimit]
        billing_profile_status: Union[str, BillingProfileStatus]
        billing_profile_status_reason_code: Union[str, BillingProfileStatusReasonCode]
        billing_profile_system_id: str
        enabled_azure_plans: list[AzurePlan]
        invoice_section_display_name: str
        invoice_section_id: str
        invoice_section_system_id: str

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


    class azure.mgmt.billing.models.InvoiceSectionWithCreateSubPermissionListResult(Model):
        next_link: str
        value: list[InvoiceSectionWithCreateSubPermission]

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


    class azure.mgmt.billing.models.MoveBillingSubscriptionEligibilityResult(Model):
        error_details: MoveBillingSubscriptionErrorDetails
        is_move_eligible: bool

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                error_details: Optional[MoveBillingSubscriptionErrorDetails] = ..., 
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


    class azure.mgmt.billing.models.MoveBillingSubscriptionErrorDetails(Model):
        code: Union[str, SubscriptionTransferValidationErrorCode]
        details: str
        message: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                code: Optional[Union[str, SubscriptionTransferValidationErrorCode]] = ..., 
                details: Optional[str] = ..., 
                message: Optional[str] = ..., 
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


    class azure.mgmt.billing.models.MoveBillingSubscriptionRequest(Model):
        destination_enrollment_account_id: str
        destination_invoice_section_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                destination_enrollment_account_id: Optional[str] = ..., 
                destination_invoice_section_id: Optional[str] = ..., 
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


    class azure.mgmt.billing.models.MoveProductEligibilityResult(Model):
        error_details: MoveProductEligibilityResultErrorDetails
        is_move_eligible: bool

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                error_details: Optional[MoveProductEligibilityResultErrorDetails] = ..., 
                is_move_eligible: Optional[bool] = ..., 
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


    class azure.mgmt.billing.models.MoveProductEligibilityResultErrorDetails(MoveProductErrorDetails):
        code: Union[str, MoveValidationErrorCode]
        details: str
        message: str

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


    class azure.mgmt.billing.models.MoveProductErrorDetails(Model):
        code: Union[str, MoveValidationErrorCode]
        details: str
        message: str

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


    class azure.mgmt.billing.models.MoveProductRequest(Model):
        destination_invoice_section_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                destination_invoice_section_id: str, 
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


    class azure.mgmt.billing.models.NextBillingCycleDetails(Model):
        billing_frequency: str

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


    class azure.mgmt.billing.models.Operation(Model):
        display: OperationDisplay
        is_data_action: bool
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


    class azure.mgmt.billing.models.OperationDisplay(Model):
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


    class azure.mgmt.billing.models.OperationListResult(Model):
        next_link: str
        value: list[Operation]

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


    class azure.mgmt.billing.models.Participant(Model):
        email: str
        status: str
        status_date: datetime

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


    class azure.mgmt.billing.models.PartnerInitiateTransferRequest(Model):
        recipient_email_id: str
        reseller_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                recipient_email_id: Optional[str] = ..., 
                reseller_id: Optional[str] = ..., 
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


    class azure.mgmt.billing.models.PartnerTransferDetails(ProxyResourceWithTags):
        canceled_by: str
        detailed_transfer_status: list[DetailedTransferStatus]
        expiration_time: datetime
        id: str
        initiator_customer_type: Union[str, InitiatorCustomerType]
        initiator_email_id: str
        name: str
        recipient_email_id: str
        reseller_id: str
        reseller_name: str
        system_data: SystemData
        tags: dict[str, str]
        transfer_status: Union[str, TransferStatus]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                tags: Optional[Dict[str, str]] = ..., 
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


    class azure.mgmt.billing.models.PartnerTransferDetailsListResult(Model):
        next_link: str
        value: list[PartnerTransferDetails]

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


    class azure.mgmt.billing.models.Patch(Model):
        applied_scope_properties: ReservationAppliedScopeProperties
        applied_scope_type: Union[str, AppliedScopeType]
        display_name: str
        instance_flexibility: Union[str, InstanceFlexibility]
        purchase_properties: ReservationPurchaseRequest
        renew: bool
        review_date_time: datetime
        sku: ReservationSkuProperty
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                applied_scope_properties: Optional[ReservationAppliedScopeProperties] = ..., 
                applied_scope_type: Optional[Union[str, AppliedScopeType]] = ..., 
                display_name: Optional[str] = ..., 
                instance_flexibility: Optional[Union[str, InstanceFlexibility]] = ..., 
                purchase_properties: Optional[ReservationPurchaseRequest] = ..., 
                renew: bool = False, 
                review_date_time: Optional[datetime] = ..., 
                sku: Optional[ReservationSkuProperty] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
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


    class azure.mgmt.billing.models.Payment(Model):
        amount: PaymentAmount
        date: datetime
        payment_method_family: Union[str, PaymentMethodFamily]
        payment_method_id: str
        payment_method_type: str
        payment_type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                amount: Optional[PaymentAmount] = ..., 
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


    class azure.mgmt.billing.models.PaymentAmount(Amount):
        currency: str
        value: float

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


    class azure.mgmt.billing.models.PaymentDetail(Model):
        billing_currency_total: Price
        due_date: date
        extended_status_info: ExtendedStatusInfo
        payment_date: date
        pricing_currency_total: Price
        status: Union[str, PaymentStatus]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                billing_currency_total: Optional[Price] = ..., 
                due_date: Optional[date] = ..., 
                payment_date: Optional[date] = ..., 
                pricing_currency_total: Optional[Price] = ..., 
                status: Optional[Union[str, PaymentStatus]] = ..., 
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


    class azure.mgmt.billing.models.PaymentMethod(ProxyResourceWithTags):
        account_holder_name: str
        display_name: str
        expiration: str
        family: Union[str, PaymentMethodFamily]
        id: str
        id_properties_id: str
        last_four_digits: str
        logos: list[PaymentMethodLogo]
        name: str
        payment_method_type: str
        status: Union[str, PaymentMethodStatus]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                family: Optional[Union[str, PaymentMethodFamily]] = ..., 
                logos: Optional[List[PaymentMethodLogo]] = ..., 
                status: Optional[Union[str, PaymentMethodStatus]] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
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


    class azure.mgmt.billing.models.PaymentMethodFamily(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CHECK_WIRE = "CheckWire"
        CREDITS = "Credits"
        CREDIT_CARD = "CreditCard"
        DIRECT_DEBIT = "DirectDebit"
        E_WALLET = "EWallet"
        NONE = "None"
        OTHER = "Other"
        TASK_ORDER = "TaskOrder"


    class azure.mgmt.billing.models.PaymentMethodLink(ProxyResourceWithTags):
        account_holder_name: str
        display_name: str
        expiration: str
        family: Union[str, PaymentMethodFamily]
        id: str
        last_four_digits: str
        logos: list[PaymentMethodLogo]
        name: str
        payment_method: PaymentMethodProperties
        payment_method_id: str
        payment_method_type: str
        status: Union[str, PaymentMethodStatus]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                payment_method: Optional[PaymentMethodProperties] = ..., 
                payment_method_id: Optional[str] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
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


    class azure.mgmt.billing.models.PaymentMethodLinksListResult(Model):
        next_link: str
        value: list[PaymentMethodLink]

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


    class azure.mgmt.billing.models.PaymentMethodLogo(Model):
        mime_type: str
        url: str

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


    class azure.mgmt.billing.models.PaymentMethodProperties(Model):
        account_holder_name: str
        display_name: str
        expiration: str
        family: Union[str, PaymentMethodFamily]
        id: str
        last_four_digits: str
        logos: list[PaymentMethodLogo]
        payment_method_type: str
        status: Union[str, PaymentMethodStatus]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                family: Optional[Union[str, PaymentMethodFamily]] = ..., 
                logos: Optional[List[PaymentMethodLogo]] = ..., 
                status: Optional[Union[str, PaymentMethodStatus]] = ..., 
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


    class azure.mgmt.billing.models.PaymentMethodStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "active"
        INACTIVE = "inactive"


    class azure.mgmt.billing.models.PaymentMethodsListResult(Model):
        next_link: str
        value: list[PaymentMethod]

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


    class azure.mgmt.billing.models.PaymentOnAccount(Model):
        amount: PaymentOnAccountAmount
        billing_profile_display_name: str
        billing_profile_id: str
        date: datetime
        invoice_id: str
        invoice_name: str
        payment_method_type: Union[str, PaymentMethodFamily]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                amount: Optional[PaymentOnAccountAmount] = ..., 
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


    class azure.mgmt.billing.models.PaymentOnAccountAmount(Amount):
        currency: str
        value: float

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


    class azure.mgmt.billing.models.PaymentStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELLED = "Cancelled"
        COMPLETED = "Completed"
        FAILED = "Failed"
        PENDING = "Pending"
        SCHEDULED = "Scheduled"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.billing.models.PaymentTerm(Model):
        end_date: datetime
        is_default: bool
        start_date: datetime
        term: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                end_date: Optional[datetime] = ..., 
                start_date: Optional[datetime] = ..., 
                term: Optional[str] = ..., 
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


    class azure.mgmt.billing.models.PaymentTermsEligibilityDetail(Model):
        code: Union[str, PaymentTermsEligibilityCode]
        message: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                code: Optional[Union[str, PaymentTermsEligibilityCode]] = ..., 
                message: Optional[str] = ..., 
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


    class azure.mgmt.billing.models.PaymentTermsEligibilityResult(Model):
        eligibility_details: list[PaymentTermsEligibilityDetail]
        eligibility_status: Union[str, PaymentTermsEligibilityStatus]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                eligibility_details: Optional[List[PaymentTermsEligibilityDetail]] = ..., 
                eligibility_status: Optional[Union[str, PaymentTermsEligibilityStatus]] = ..., 
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


    class azure.mgmt.billing.models.PaymentTermsEligibilityStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INVALID = "Invalid"
        OTHER = "Other"
        VALID = "Valid"


    class azure.mgmt.billing.models.PolicySummary(Model):
        name: str
        policy_type: Union[str, PolicyType]
        scope: str
        value: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                policy_type: Optional[Union[str, PolicyType]] = ..., 
                scope: Optional[str] = ..., 
                value: Optional[str] = ..., 
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


    class azure.mgmt.billing.models.PolicyType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        OTHER = "Other"
        SYSTEM_CONTROLLED = "SystemControlled"
        USER_CONTROLLED = "UserControlled"


    class azure.mgmt.billing.models.Price(Model):
        amount: float
        currency_code: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                amount: Optional[float] = ..., 
                currency_code: Optional[str] = ..., 
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


    class azure.mgmt.billing.models.Principal(Model):
        object_id: str
        tenant_id: str
        upn: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                object_id: Optional[str] = ..., 
                tenant_id: Optional[str] = ..., 
                upn: Optional[str] = ..., 
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


    class azure.mgmt.billing.models.PrincipalType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DIRECTORY_ROLE = "DirectoryRole"
        EVERYONE = "Everyone"
        GROUP = "Group"
        NONE = "None"
        SERVICE_PRINCIPAL = "ServicePrincipal"
        UNKNOWN = "Unknown"
        USER = "User"


    class azure.mgmt.billing.models.Product(ProxyResourceWithTags):
        id: str
        name: str
        properties: ProductProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[ProductProperties] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
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


    class azure.mgmt.billing.models.ProductDetails(Model):
        product_id: str
        product_type: Union[str, ProductType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                product_id: Optional[str] = ..., 
                product_type: Optional[Union[str, ProductType]] = ..., 
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


    class azure.mgmt.billing.models.ProductListResult(Model):
        next_link: str
        value: list[Product]

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


    class azure.mgmt.billing.models.ProductPatch(ProxyResourceWithTags):
        id: str
        name: str
        properties: ProductProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[ProductProperties] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
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


    class azure.mgmt.billing.models.ProductProperties(Model):
        auto_renew: Union[str, AutoRenew]
        availability_id: str
        billing_frequency: str
        billing_profile_display_name: str
        billing_profile_id: str
        customer_display_name: str
        customer_id: str
        display_name: str
        end_date: str
        invoice_section_display_name: str
        invoice_section_id: str
        last_charge: ProductPropertiesLastCharge
        last_charge_date: str
        product_type: str
        product_type_id: str
        purchase_date: str
        quantity: int
        reseller: ProductPropertiesReseller
        sku_description: str
        sku_id: str
        status: Union[str, ProductStatus]
        tenant_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                auto_renew: Optional[Union[str, AutoRenew]] = ..., 
                last_charge: Optional[ProductPropertiesLastCharge] = ..., 
                reseller: Optional[ProductPropertiesReseller] = ..., 
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


    class azure.mgmt.billing.models.ProductPropertiesLastCharge(Amount):
        currency: str
        value: float

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


    class azure.mgmt.billing.models.ProductPropertiesReseller(Reseller):
        description: str
        reseller_id: str

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


    class azure.mgmt.billing.models.ProxyResourceWithTags(ProxyResource):
        id: str
        name: str
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                tags: Optional[Dict[str, str]] = ..., 
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


    class azure.mgmt.billing.models.PurchaseRequest(Model):
        applied_scope_properties: AppliedScopeProperties
        applied_scope_type: Union[str, AppliedScopeType]
        billing_plan: Union[str, BillingPlan]
        billing_scope_id: str
        commitment: Commitment
        display_name: str
        renew: bool
        sku: Sku
        term: Union[str, SavingsPlanTerm]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                applied_scope_properties: Optional[AppliedScopeProperties] = ..., 
                applied_scope_type: Optional[Union[str, AppliedScopeType]] = ..., 
                billing_plan: Optional[Union[str, BillingPlan]] = ..., 
                billing_scope_id: Optional[str] = ..., 
                commitment: Optional[Commitment] = ..., 
                display_name: Optional[str] = ..., 
                renew: bool = False, 
                sku: Optional[Sku] = ..., 
                term: Optional[Union[str, SavingsPlanTerm]] = ..., 
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


    class azure.mgmt.billing.models.RebillDetails(Model):
        credit_note_document_id: str
        invoice_document_id: str
        rebill_details: RebillDetails

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


    class azure.mgmt.billing.models.RecipientTransferDetails(ProxyResourceWithTags):
        allowed_product_type: Union[list[str, EligibleProductType]]
        canceled_by: str
        customer_tenant_id: str
        detailed_transfer_status: list[DetailedTransferStatus]
        expiration_time: datetime
        id: str
        initiator_customer_type: Union[str, InitiatorCustomerType]
        initiator_email_id: str
        name: str
        recipient_email_id: str
        reseller_id: str
        reseller_name: str
        supported_accounts: Union[list[str, SupportedAccountType]]
        system_data: SystemData
        tags: dict[str, str]
        transfer_status: Union[str, TransferStatus]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                tags: Optional[Dict[str, str]] = ..., 
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


    class azure.mgmt.billing.models.RecipientTransferDetailsListResult(Model):
        next_link: str
        value: list[RecipientTransferDetails]

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


    class azure.mgmt.billing.models.RefundDetailsSummary(Model):
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

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                amount_refunded: Optional[RefundDetailsSummaryAmountRefunded] = ..., 
                amount_requested: Optional[RefundDetailsSummaryAmountRequested] = ..., 
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


    class azure.mgmt.billing.models.RefundDetailsSummaryAmountRefunded(Amount):
        currency: str
        value: float

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


    class azure.mgmt.billing.models.RefundDetailsSummaryAmountRequested(Amount):
        currency: str
        value: float

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


    class azure.mgmt.billing.models.RefundTransactionDetails(Model):
        amount_refunded: RefundTransactionDetailsAmountRefunded
        amount_requested: RefundTransactionDetailsAmountRequested
        refund_operation_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                amount_refunded: Optional[RefundTransactionDetailsAmountRefunded] = ..., 
                amount_requested: Optional[RefundTransactionDetailsAmountRequested] = ..., 
                refund_operation_id: Optional[str] = ..., 
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


    class azure.mgmt.billing.models.RefundTransactionDetailsAmountRefunded(Amount):
        currency: str
        value: float

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


    class azure.mgmt.billing.models.RefundTransactionDetailsAmountRequested(Amount):
        currency: str
        value: float

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


    class azure.mgmt.billing.models.RegistrationNumber(Model):
        id: str
        required: bool
        type: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
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


    class azure.mgmt.billing.models.RenewProperties(Model):
        purchase_properties: PurchaseRequest

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                purchase_properties: Optional[PurchaseRequest] = ..., 
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


    class azure.mgmt.billing.models.RenewPropertiesResponse(Model):
        billing_currency_total: Price
        pricing_currency_total: Price
        purchase_properties: ReservationPurchaseRequest

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                billing_currency_total: Optional[Price] = ..., 
                pricing_currency_total: Optional[Price] = ..., 
                purchase_properties: Optional[ReservationPurchaseRequest] = ..., 
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


    class azure.mgmt.billing.models.RenewalTermDetails(Model):
        billing_frequency: str
        product_id: str
        product_type_id: str
        quantity: int
        sku_id: str
        term_duration: str
        term_end_date: datetime

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                quantity: Optional[int] = ..., 
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


    class azure.mgmt.billing.models.Reseller(Model):
        description: str
        reseller_id: str

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


    class azure.mgmt.billing.models.Reservation(ProxyResource):
        aggregates: list[ReservationUtilizationAggregates]
        applied_scope_properties: ReservationAppliedScopeProperties
        applied_scope_type: str
        applied_scopes: list[str]
        archived: bool
        benefit_start_time: datetime
        billing_plan: Union[str, ReservationBillingPlan]
        billing_scope_id: str
        capabilities: str
        display_name: str
        display_provisioning_state: str
        effective_date_time: datetime
        etag: int
        expiry_date: str
        expiry_date_time: datetime
        extended_status_info: ReservationExtendedStatusInfo
        id: str
        instance_flexibility: Union[str, InstanceFlexibility]
        last_updated_date_time: datetime
        location: str
        merge_properties: ReservationMergeProperties
        name: str
        product_code: str
        provisioning_state: str
        provisioning_sub_state: str
        purchase_date: date
        purchase_date_time: datetime
        quantity: float
        renew: bool
        renew_destination: str
        renew_properties: RenewPropertiesResponse
        renew_source: str
        reserved_resource_type: str
        review_date_time: datetime
        sku: ReservationSkuProperty
        sku_description: str
        split_properties: ReservationSplitProperties
        swap_properties: ReservationSwapProperties
        system_data: SystemData
        tags: dict[str, str]
        term: str
        trend: str
        type: str
        user_friendly_applied_scope_type: str
        user_friendly_renew_state: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                aggregates: Optional[List[ReservationUtilizationAggregates]] = ..., 
                applied_scope_properties: Optional[ReservationAppliedScopeProperties] = ..., 
                applied_scopes: Optional[List[str]] = ..., 
                archived: Optional[bool] = ..., 
                benefit_start_time: Optional[datetime] = ..., 
                billing_plan: Optional[Union[str, ReservationBillingPlan]] = ..., 
                capabilities: Optional[str] = ..., 
                etag: Optional[int] = ..., 
                expiry_date_time: Optional[datetime] = ..., 
                extended_status_info: Optional[ReservationExtendedStatusInfo] = ..., 
                instance_flexibility: Optional[Union[str, InstanceFlexibility]] = ..., 
                location: Optional[str] = ..., 
                merge_properties: Optional[ReservationMergeProperties] = ..., 
                product_code: Optional[str] = ..., 
                purchase_date: Optional[date] = ..., 
                purchase_date_time: Optional[datetime] = ..., 
                renew_destination: Optional[str] = ..., 
                renew_properties: Optional[RenewPropertiesResponse] = ..., 
                review_date_time: Optional[datetime] = ..., 
                sku: Optional[ReservationSkuProperty] = ..., 
                split_properties: Optional[ReservationSplitProperties] = ..., 
                swap_properties: Optional[ReservationSwapProperties] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
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


    class azure.mgmt.billing.models.ReservationAppliedScopeProperties(Model):
        display_name: str
        management_group_id: str
        resource_group_id: str
        subscription_id: str
        tenant_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                display_name: Optional[str] = ..., 
                management_group_id: Optional[str] = ..., 
                resource_group_id: Optional[str] = ..., 
                subscription_id: Optional[str] = ..., 
                tenant_id: Optional[str] = ..., 
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


    class azure.mgmt.billing.models.ReservationBillingPlan(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MONTHLY = "Monthly"
        UPFRONT = "Upfront"


    class azure.mgmt.billing.models.ReservationExtendedStatusInfo(Model):
        message: str
        properties: ExtendedStatusDefinitionProperties
        status_code: Union[str, ReservationStatusCode]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                message: Optional[str] = ..., 
                properties: Optional[ExtendedStatusDefinitionProperties] = ..., 
                status_code: Optional[Union[str, ReservationStatusCode]] = ..., 
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


    class azure.mgmt.billing.models.ReservationList(Model):
        next_link: str
        value: list[Reservation]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[Reservation]] = ..., 
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


    class azure.mgmt.billing.models.ReservationMergeProperties(Model):
        merge_destination: str
        merge_sources: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                merge_destination: Optional[str] = ..., 
                merge_sources: Optional[List[str]] = ..., 
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


    class azure.mgmt.billing.models.ReservationOrder(ProxyResource):
        benefit_start_time: datetime
        billing_account_id: str
        billing_plan: Union[str, ReservationBillingPlan]
        billing_profile_id: str
        created_date_time: datetime
        customer_id: str
        display_name: str
        enrollment_id: str
        etag: int
        expiry_date: date
        expiry_date_time: datetime
        extended_status_info: ReservationExtendedStatusInfo
        id: str
        name: str
        original_quantity: int
        plan_information: ReservationOrderBillingPlanInformation
        product_code: str
        provisioning_state: str
        request_date_time: datetime
        reservations: list[Reservation]
        review_date_time: datetime
        system_data: SystemData
        tags: dict[str, str]
        term: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

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
                etag: Optional[int] = ..., 
                expiry_date: Optional[date] = ..., 
                expiry_date_time: Optional[datetime] = ..., 
                extended_status_info: Optional[ReservationExtendedStatusInfo] = ..., 
                original_quantity: Optional[int] = ..., 
                plan_information: Optional[ReservationOrderBillingPlanInformation] = ..., 
                product_code: Optional[str] = ..., 
                request_date_time: Optional[datetime] = ..., 
                reservations: Optional[List[Reservation]] = ..., 
                review_date_time: Optional[datetime] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
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


    class azure.mgmt.billing.models.ReservationOrderBillingPlanInformation(Model):
        next_payment_due_date: date
        pricing_currency_total: Price
        start_date: date
        transactions: list[ReservationPaymentDetail]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_payment_due_date: Optional[date] = ..., 
                pricing_currency_total: Optional[Price] = ..., 
                start_date: Optional[date] = ..., 
                transactions: Optional[List[ReservationPaymentDetail]] = ..., 
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


    class azure.mgmt.billing.models.ReservationOrderList(Model):
        next_link: str
        value: list[ReservationOrder]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[ReservationOrder]] = ..., 
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


    class azure.mgmt.billing.models.ReservationPaymentDetail(Model):
        billing_account: str
        billing_currency_total: Price
        due_date: date
        extended_status_info: ReservationExtendedStatusInfo
        payment_date: date
        pricing_currency_total: Price
        status: Union[str, PaymentStatus]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                billing_account: Optional[str] = ..., 
                billing_currency_total: Optional[Price] = ..., 
                due_date: Optional[date] = ..., 
                extended_status_info: Optional[ReservationExtendedStatusInfo] = ..., 
                payment_date: Optional[date] = ..., 
                pricing_currency_total: Optional[Price] = ..., 
                status: Optional[Union[str, PaymentStatus]] = ..., 
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


    class azure.mgmt.billing.models.ReservationPurchaseRequest(Model):
        applied_scope_properties: ReservationAppliedScopeProperties
        applied_scope_type: Union[str, AppliedScopeType]
        applied_scopes: list[str]
        billing_plan: Union[str, ReservationBillingPlan]
        billing_scope_id: str
        display_name: str
        instance_flexibility_properties_instance_flexibility: Union[str, InstanceFlexibility]
        instance_flexibility_properties_reserved_resource_properties_instance_flexibility: str
        location: str
        quantity: int
        renew: bool
        reserved_resource_type: str
        review_date_time: datetime
        sku: SkuName
        term: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                applied_scope_properties: Optional[ReservationAppliedScopeProperties] = ..., 
                applied_scope_type: Optional[Union[str, AppliedScopeType]] = ..., 
                applied_scopes: Optional[List[str]] = ..., 
                billing_plan: Optional[Union[str, ReservationBillingPlan]] = ..., 
                display_name: Optional[str] = ..., 
                instance_flexibility_properties_instance_flexibility: Optional[Union[str, InstanceFlexibility]] = ..., 
                instance_flexibility_properties_reserved_resource_properties_instance_flexibility: Optional[Union[str, InstanceFlexibility]] = ..., 
                location: Optional[str] = ..., 
                quantity: Optional[int] = ..., 
                renew: bool = False, 
                review_date_time: Optional[datetime] = ..., 
                sku: Optional[SkuName] = ..., 
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


    class azure.mgmt.billing.models.ReservationPurchasesPolicy(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALLOWED = "Allowed"
        DISABLED = "Disabled"
        NOT_ALLOWED = "NotAllowed"
        OTHER = "Other"


    class azure.mgmt.billing.models.ReservationSkuProperty(Model):
        name: str

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


    class azure.mgmt.billing.models.ReservationSplitProperties(Model):
        split_destinations: list[str]
        split_source: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                split_destinations: Optional[List[str]] = ..., 
                split_source: Optional[str] = ..., 
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


    class azure.mgmt.billing.models.ReservationSummary(Model):
        cancelled_count: float
        expired_count: float
        expiring_count: float
        failed_count: float
        no_benefit_count: float
        pending_count: float
        processing_count: float
        succeeded_count: float
        warning_count: float

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


    class azure.mgmt.billing.models.ReservationSwapProperties(Model):
        swap_destination: str
        swap_source: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                swap_destination: Optional[str] = ..., 
                swap_source: Optional[str] = ..., 
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


    class azure.mgmt.billing.models.ReservationUtilizationAggregates(Model):
        grain: float
        grain_unit: str
        value: float
        value_unit: str

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


    class azure.mgmt.billing.models.ReservationsListResult(Model):
        next_link: str
        summary: ReservationSummary
        value: list[Reservation]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                summary: Optional[ReservationSummary] = ..., 
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


    class azure.mgmt.billing.models.Resource(Model):
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


    class azure.mgmt.billing.models.SavingsPlanModel(ProxyResourceWithTags):
        applied_scope_properties: AppliedScopeProperties
        applied_scope_type: Union[str, AppliedScopeType]
        benefit_start_time: datetime
        billing_account_id: str
        billing_plan: Union[str, BillingPlan]
        billing_profile_id: str
        billing_scope_id: str
        commitment: Commitment
        customer_id: str
        display_name: str
        display_provisioning_state: str
        effective_date_time: datetime
        expiry_date_time: datetime
        extended_status_info: ExtendedStatusInfo
        id: str
        name: str
        product_code: str
        provisioning_state: Union[str, ProvisioningState]
        purchase_date_time: datetime
        renew: bool
        renew_destination: str
        renew_properties: RenewProperties
        renew_source: str
        sku: Sku
        system_data: SystemData
        tags: dict[str, str]
        term: Union[str, SavingsPlanTerm]
        type: str
        user_friendly_applied_scope_type: str
        utilization: Utilization

        def __eq__(self, other: Any) -> bool: ...

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
                provisioning_state: Optional[Union[str, ProvisioningState]] = ..., 
                renew: bool = False, 
                renew_destination: Optional[str] = ..., 
                renew_properties: Optional[RenewProperties] = ..., 
                renew_source: Optional[str] = ..., 
                sku: Sku, 
                tags: Optional[Dict[str, str]] = ..., 
                term: Optional[Union[str, SavingsPlanTerm]] = ..., 
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


    class azure.mgmt.billing.models.SavingsPlanModelList(Model):
        next_link: str
        value: list[SavingsPlanModel]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[SavingsPlanModel]] = ..., 
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


    class azure.mgmt.billing.models.SavingsPlanModelListResult(SavingsPlanModelList):
        next_link: str
        summary: SavingsPlanSummaryCount
        value: list[SavingsPlanModel]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                summary: Optional[SavingsPlanSummaryCount] = ..., 
                value: Optional[List[SavingsPlanModel]] = ..., 
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


    class azure.mgmt.billing.models.SavingsPlanOrderModel(ProxyResourceWithTags):
        benefit_start_time: datetime
        billing_account_id: str
        billing_plan: Union[str, BillingPlan]
        billing_profile_id: str
        billing_scope_id: str
        customer_id: str
        display_name: str
        expiry_date_time: datetime
        extended_status_info: ExtendedStatusInfo
        id: str
        name: str
        plan_information: BillingPlanInformation
        product_code: str
        provisioning_state: str
        savings_plans: list[str]
        sku: Sku
        system_data: SystemData
        tags: dict[str, str]
        term: Union[str, SavingsPlanTerm]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                billing_plan: Optional[Union[str, BillingPlan]] = ..., 
                billing_scope_id: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                plan_information: Optional[BillingPlanInformation] = ..., 
                product_code: Optional[str] = ..., 
                savings_plans: Optional[List[str]] = ..., 
                sku: Sku, 
                tags: Optional[Dict[str, str]] = ..., 
                term: Optional[Union[str, SavingsPlanTerm]] = ..., 
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


    class azure.mgmt.billing.models.SavingsPlanOrderModelList(Model):
        next_link: str
        value: list[SavingsPlanOrderModel]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[SavingsPlanOrderModel]] = ..., 
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


    class azure.mgmt.billing.models.SavingsPlanPurchasesPolicy(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALLOWED = "Allowed"
        DISABLED = "Disabled"
        NOT_ALLOWED = "NotAllowed"
        OTHER = "Other"


    class azure.mgmt.billing.models.SavingsPlanSummaryCount(Model):
        cancelled_count: float
        expired_count: float
        expiring_count: float
        failed_count: float
        no_benefit_count: float
        pending_count: float
        processing_count: float
        succeeded_count: float
        warning_count: float

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


    class azure.mgmt.billing.models.SavingsPlanTerm(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        P1_Y = "P1Y"
        P3_Y = "P3Y"
        P5_Y = "P5Y"


    class azure.mgmt.billing.models.SavingsPlanUpdateRequest(Model):
        properties: SavingsPlanUpdateRequestProperties
        sku: Sku
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[SavingsPlanUpdateRequestProperties] = ..., 
                sku: Optional[Sku] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
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


    class azure.mgmt.billing.models.SavingsPlanUpdateRequestProperties(Model):
        applied_scope_properties: AppliedScopeProperties
        applied_scope_type: Union[str, AppliedScopeType]
        display_name: str
        renew: bool
        renew_properties: RenewProperties

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                applied_scope_properties: Optional[AppliedScopeProperties] = ..., 
                applied_scope_type: Optional[Union[str, AppliedScopeType]] = ..., 
                display_name: Optional[str] = ..., 
                renew: bool = False, 
                renew_properties: Optional[RenewProperties] = ..., 
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


    class azure.mgmt.billing.models.SavingsPlanUpdateValidateRequest(Model):
        benefits: list[SavingsPlanUpdateRequestProperties]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                benefits: Optional[List[SavingsPlanUpdateRequestProperties]] = ..., 
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


    class azure.mgmt.billing.models.SavingsPlanValidResponseProperty(Model):
        reason: str
        reason_code: str
        valid: bool

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                reason: Optional[str] = ..., 
                reason_code: Optional[str] = ..., 
                valid: Optional[bool] = ..., 
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


    class azure.mgmt.billing.models.SavingsPlanValidateResponse(Model):
        benefits: list[SavingsPlanValidResponseProperty]
        next_link: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                benefits: Optional[List[SavingsPlanValidResponseProperty]] = ..., 
                next_link: Optional[str] = ..., 
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


    class azure.mgmt.billing.models.ServiceDefinedResourceName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEFAULT = "default"


    class azure.mgmt.billing.models.Sku(Model):
        name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
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


    class azure.mgmt.billing.models.SkuName(Model):
        name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
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


    class azure.mgmt.billing.models.SpecialTaxationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INVOICE_LEVEL = "InvoiceLevel"
        SUBTOTAL_LEVEL = "SubtotalLevel"


    class azure.mgmt.billing.models.SpendingLimit(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        OFF = "Off"
        ON = "On"


    class azure.mgmt.billing.models.SpendingLimitDetails(Model):
        amount: float
        currency: str
        end_date: datetime
        start_date: datetime
        status: Union[str, SpendingLimitStatus]
        type: Union[str, SpendingLimitType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                amount: Optional[float] = ..., 
                currency: Optional[str] = ..., 
                end_date: Optional[datetime] = ..., 
                start_date: Optional[datetime] = ..., 
                status: Optional[Union[str, SpendingLimitStatus]] = ..., 
                type: Optional[Union[str, SpendingLimitType]] = ..., 
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


    class azure.mgmt.billing.models.SubscriptionEnrollmentDetails(Model):
        department_display_name: str
        department_id: str
        enrollment_account_display_name: str
        enrollment_account_id: str
        enrollment_account_status: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                department_display_name: Optional[str] = ..., 
                department_id: Optional[str] = ..., 
                enrollment_account_display_name: Optional[str] = ..., 
                enrollment_account_id: Optional[str] = ..., 
                enrollment_account_status: Optional[str] = ..., 
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


    class azure.mgmt.billing.models.SubscriptionPolicy(ProxyResourceWithTags):
        id: str
        name: str
        properties: SubscriptionPolicyProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[SubscriptionPolicyProperties] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
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


    class azure.mgmt.billing.models.SubscriptionPolicyProperties(Model):
        policies: list[PolicySummary]
        provisioning_state: Union[str, ProvisioningState]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                policies: Optional[List[PolicySummary]] = ..., 
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


    class azure.mgmt.billing.models.SystemData(Model):
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


    class azure.mgmt.billing.models.SystemOverrides(Model):
        cancellation: Union[str, Cancellation]
        cancellation_allowed_end_date: datetime

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


    class azure.mgmt.billing.models.TaxIdentifier(Model):
        country: str
        id: str
        scope: str
        status: Union[str, TaxIdentifierStatus]
        type: Union[str, TaxIdentifierType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                country: Optional[str] = ..., 
                id: Optional[str] = ..., 
                scope: Optional[str] = ..., 
                status: Optional[Union[str, TaxIdentifierStatus]] = ..., 
                type: Optional[Union[str, TaxIdentifierType]] = ..., 
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
        properties: TransactionProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[TransactionProperties] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
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


    class azure.mgmt.billing.models.TransactionKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALL = "All"
        OTHER = "Other"
        RESERVATION = "Reservation"


    class azure.mgmt.billing.models.TransactionListResult(Model):
        next_link: str
        value: list[Transaction]

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


    class azure.mgmt.billing.models.TransactionProperties(Model):
        azure_credit_applied: TransactionPropertiesAzureCreditApplied
        azure_plan: str
        billing_currency: str
        billing_profile_display_name: any
        billing_profile_id: str
        consumption_commitment_decremented: TransactionPropertiesConsumptionCommitmentDecremented
        credit_type: Union[str, CreditType]
        customer_display_name: str
        customer_id: str
        date: datetime
        discount: float
        effective_price: TransactionPropertiesEffectivePrice
        exchange_rate: float
        invoice: str
        invoice_id: str
        invoice_section_display_name: str
        invoice_section_id: str
        is_third_party: bool
        kind: Union[str, TransactionKind]
        market_price: TransactionPropertiesMarketPrice
        part_number: str
        pricing_currency: str
        product_description: str
        product_family: str
        product_type: str
        product_type_id: str
        quantity: int
        reason_code: str
        refund_transaction_details: TransactionPropertiesRefundTransactionDetails
        service_period_end_date: datetime
        service_period_start_date: datetime
        special_taxation_type: Union[str, SpecialTaxationType]
        sub_total: TransactionPropertiesSubTotal
        tax: TransactionPropertiesTax
        transaction_amount: TransactionPropertiesTransactionAmount
        transaction_type: str
        unit_of_measure: str
        unit_type: str
        units: float

        def __eq__(self, other: Any) -> bool: ...

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
                units: Optional[float] = ..., 
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


    class azure.mgmt.billing.models.TransactionPropertiesAzureCreditApplied(Amount):
        currency: str
        value: float

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


    class azure.mgmt.billing.models.TransactionPropertiesConsumptionCommitmentDecremented(Amount):
        currency: str
        value: float

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


    class azure.mgmt.billing.models.TransactionPropertiesEffectivePrice(Amount):
        currency: str
        value: float

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


    class azure.mgmt.billing.models.TransactionPropertiesMarketPrice(Amount):
        currency: str
        value: float

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


    class azure.mgmt.billing.models.TransactionPropertiesRefundTransactionDetails(RefundTransactionDetails):
        amount_refunded: RefundTransactionDetailsAmountRefunded
        amount_requested: RefundTransactionDetailsAmountRequested
        refund_operation_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                amount_refunded: Optional[RefundTransactionDetailsAmountRefunded] = ..., 
                amount_requested: Optional[RefundTransactionDetailsAmountRequested] = ..., 
                refund_operation_id: Optional[str] = ..., 
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


    class azure.mgmt.billing.models.TransactionPropertiesSubTotal(Amount):
        currency: str
        value: float

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


    class azure.mgmt.billing.models.TransactionPropertiesTax(Amount):
        currency: str
        value: float

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


    class azure.mgmt.billing.models.TransactionPropertiesTransactionAmount(Amount):
        currency: str
        value: float

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


    class azure.mgmt.billing.models.TransactionSummary(Model):
        azure_credit_applied: float
        billing_currency: str
        consumption_commitment_decremented: float
        sub_total: float
        tax: float
        total: float

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


    class azure.mgmt.billing.models.TransactionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BILLED = "Billed"
        OTHER = "Other"
        UNBILLED = "Unbilled"


    class azure.mgmt.billing.models.TransferDetails(ProxyResourceWithTags):
        canceled_by: str
        detailed_transfer_status: list[DetailedTransferStatus]
        expiration_time: datetime
        id: str
        initiator_email_id: str
        name: str
        recipient_email_id: str
        system_data: SystemData
        tags: dict[str, str]
        transfer_status: Union[str, TransferStatus]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                tags: Optional[Dict[str, str]] = ..., 
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


    class azure.mgmt.billing.models.TransferDetailsListResult(Model):
        next_link: str
        value: list[TransferDetails]

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


    class azure.mgmt.billing.models.TransferError(Model):
        code: str
        message: str

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


    class azure.mgmt.billing.models.TransferItemQueryParameter(Model):
        state: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                state: Optional[str] = ..., 
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


    class azure.mgmt.billing.models.TransferStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        COMPLETED = "Completed"
        COMPLETED_WITH_ERRORS = "CompletedWithErrors"
        DECLINED = "Declined"
        EXPIRED = "Expired"
        FAILED = "Failed"
        IN_PROGRESS = "InProgress"
        PENDING = "Pending"


    class azure.mgmt.billing.models.TransitionDetails(Model):
        anniversary_day: int
        transition_date: datetime

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


    class azure.mgmt.billing.models.Utilization(Model):
        aggregates: list[UtilizationAggregates]
        trend: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                aggregates: Optional[List[UtilizationAggregates]] = ..., 
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


    class azure.mgmt.billing.models.UtilizationAggregates(Model):
        grain: float
        grain_unit: str
        value: float
        value_unit: str

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


    class azure.mgmt.billing.models.ValidateTransferListResponse(Model):
        value: list[ValidateTransferResponse]

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


    class azure.mgmt.billing.models.ValidateTransferResponse(Model):
        product_id: str
        results: list[ValidationResultProperties]
        status: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                results: Optional[List[ValidationResultProperties]] = ..., 
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


    class azure.mgmt.billing.models.ValidationResultProperties(Model):
        code: str
        level: str
        message: str

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
            ): ...

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
            ): ...

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
                expand: Optional[str] = None, 
                **kwargs: Any
            ) -> Iterable[Agreement]: ...


    class azure.mgmt.billing.operations.AssociatedTenantsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

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
                include_revoked: bool = False, 
                filter: Optional[str] = None, 
                order_by: Optional[str] = None, 
                top: Optional[int] = None, 
                skip: Optional[int] = None, 
                count: Optional[bool] = None, 
                search: Optional[str] = None, 
                **kwargs: Any
            ) -> Iterable[AssociatedTenant]: ...


    class azure.mgmt.billing.operations.AvailableBalancesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

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
            ): ...

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
                include_all: bool = False, 
                include_all_without_billing_profiles: bool = False, 
                include_deleted: bool = False, 
                include_pending_agreement: bool = False, 
                include_resellee: bool = False, 
                legal_owner_tid: Optional[str] = None, 
                legal_owner_oid: Optional[str] = None, 
                filter: Optional[str] = None, 
                expand: Optional[str] = None, 
                top: Optional[int] = None, 
                skip: Optional[int] = None, 
                search: Optional[str] = None, 
                **kwargs: Any
            ) -> Iterable[BillingAccount]: ...

        @distributed_trace
        def list_invoice_sections_by_create_subscription_permission(
                self, 
                billing_account_name: str, 
                filter: Optional[str] = None, 
                **kwargs: Any
            ) -> Iterable[InvoiceSectionWithCreateSubPermission]: ...

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
            ): ...

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
            ) -> Iterable[BillingPermission]: ...

        @distributed_trace
        def list_by_billing_profile(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                **kwargs: Any
            ) -> Iterable[BillingPermission]: ...

        @distributed_trace
        def list_by_customer(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                customer_name: str, 
                **kwargs: Any
            ) -> Iterable[BillingPermission]: ...

        @distributed_trace
        def list_by_customer_at_billing_account(
                self, 
                billing_account_name: str, 
                customer_name: str, 
                **kwargs: Any
            ) -> Iterable[BillingPermission]: ...

        @distributed_trace
        def list_by_department(
                self, 
                billing_account_name: str, 
                department_name: str, 
                **kwargs: Any
            ) -> Iterable[BillingPermission]: ...

        @distributed_trace
        def list_by_enrollment_account(
                self, 
                billing_account_name: str, 
                enrollment_account_name: str, 
                **kwargs: Any
            ) -> Iterable[BillingPermission]: ...

        @distributed_trace
        def list_by_invoice_section(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                invoice_section_name: str, 
                **kwargs: Any
            ) -> Iterable[BillingPermission]: ...


    class azure.mgmt.billing.operations.BillingProfilesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

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
                include_deleted: bool = False, 
                filter: Optional[str] = None, 
                order_by: Optional[str] = None, 
                top: Optional[int] = None, 
                skip: Optional[int] = None, 
                count: Optional[bool] = None, 
                search: Optional[str] = None, 
                **kwargs: Any
            ) -> Iterable[BillingProfile]: ...

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
            ): ...

        @distributed_trace
        def get(
                self, 
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
            ): ...

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
                filter: Optional[str] = None, 
                order_by: Optional[str] = None, 
                top: Optional[int] = None, 
                skip: Optional[int] = None, 
                count: Optional[bool] = None, 
                search: Optional[str] = None, 
                **kwargs: Any
            ) -> Iterable[BillingRequest]: ...

        @distributed_trace
        def list_by_billing_profile(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                filter: Optional[str] = None, 
                order_by: Optional[str] = None, 
                top: Optional[int] = None, 
                skip: Optional[int] = None, 
                count: Optional[bool] = None, 
                search: Optional[str] = None, 
                **kwargs: Any
            ) -> Iterable[BillingRequest]: ...

        @distributed_trace
        def list_by_customer(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                customer_name: str, 
                filter: Optional[str] = None, 
                order_by: Optional[str] = None, 
                top: Optional[int] = None, 
                skip: Optional[int] = None, 
                count: Optional[bool] = None, 
                search: Optional[str] = None, 
                **kwargs: Any
            ) -> Iterable[BillingRequest]: ...

        @distributed_trace
        def list_by_invoice_section(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                invoice_section_name: str, 
                filter: Optional[str] = None, 
                order_by: Optional[str] = None, 
                top: Optional[int] = None, 
                skip: Optional[int] = None, 
                count: Optional[bool] = None, 
                search: Optional[str] = None, 
                **kwargs: Any
            ) -> Iterable[BillingRequest]: ...

        @distributed_trace
        def list_by_user(
                self, 
                filter: Optional[str] = None, 
                order_by: Optional[str] = None, 
                top: Optional[int] = None, 
                skip: Optional[int] = None, 
                count: Optional[bool] = None, 
                search: Optional[str] = None, 
                **kwargs: Any
            ) -> Iterable[BillingRequest]: ...


    class azure.mgmt.billing.operations.BillingRoleAssignmentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

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
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BillingRoleAssignment]: ...

        @distributed_trace
        def begin_resolve_by_billing_account(
                self, 
                billing_account_name: str, 
                resolve_scope_display_names: bool = False, 
                filter: Optional[str] = None, 
                **kwargs: Any
            ) -> LROPoller[BillingRoleAssignmentListResult]: ...

        @distributed_trace
        def begin_resolve_by_billing_profile(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                resolve_scope_display_names: bool = False, 
                filter: Optional[str] = None, 
                **kwargs: Any
            ) -> LROPoller[BillingRoleAssignmentListResult]: ...

        @distributed_trace
        def begin_resolve_by_customer(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                customer_name: str, 
                resolve_scope_display_names: bool = False, 
                filter: Optional[str] = None, 
                **kwargs: Any
            ) -> LROPoller[BillingRoleAssignmentListResult]: ...

        @distributed_trace
        def begin_resolve_by_invoice_section(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                invoice_section_name: str, 
                resolve_scope_display_names: bool = False, 
                filter: Optional[str] = None, 
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
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                skip: Optional[int] = None, 
                **kwargs: Any
            ) -> Iterable[BillingRoleAssignment]: ...

        @distributed_trace
        def list_by_billing_profile(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                skip: Optional[int] = None, 
                **kwargs: Any
            ) -> Iterable[BillingRoleAssignment]: ...

        @distributed_trace
        def list_by_customer(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                customer_name: str, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                skip: Optional[int] = None, 
                **kwargs: Any
            ) -> Iterable[BillingRoleAssignment]: ...

        @distributed_trace
        def list_by_department(
                self, 
                billing_account_name: str, 
                department_name: str, 
                **kwargs: Any
            ) -> Iterable[BillingRoleAssignment]: ...

        @distributed_trace
        def list_by_enrollment_account(
                self, 
                billing_account_name: str, 
                enrollment_account_name: str, 
                **kwargs: Any
            ) -> Iterable[BillingRoleAssignment]: ...

        @distributed_trace
        def list_by_invoice_section(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                invoice_section_name: str, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                skip: Optional[int] = None, 
                **kwargs: Any
            ) -> Iterable[BillingRoleAssignment]: ...


    class azure.mgmt.billing.operations.BillingRoleDefinitionOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

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
            ) -> Iterable[BillingRoleDefinition]: ...

        @distributed_trace
        def list_by_billing_profile(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                **kwargs: Any
            ) -> Iterable[BillingRoleDefinition]: ...

        @distributed_trace
        def list_by_customer(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                customer_name: str, 
                **kwargs: Any
            ) -> Iterable[BillingRoleDefinition]: ...

        @distributed_trace
        def list_by_department(
                self, 
                billing_account_name: str, 
                department_name: str, 
                **kwargs: Any
            ) -> Iterable[BillingRoleDefinition]: ...

        @distributed_trace
        def list_by_enrollment_account(
                self, 
                billing_account_name: str, 
                enrollment_account_name: str, 
                **kwargs: Any
            ) -> Iterable[BillingRoleDefinition]: ...

        @distributed_trace
        def list_by_invoice_section(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                invoice_section_name: str, 
                **kwargs: Any
            ) -> Iterable[BillingRoleDefinition]: ...


    class azure.mgmt.billing.operations.BillingSubscriptionsAliasesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

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
                include_deleted: bool = False, 
                filter: Optional[str] = None, 
                order_by: Optional[str] = None, 
                top: Optional[int] = None, 
                skip: Optional[int] = None, 
                count: Optional[bool] = None, 
                search: Optional[str] = None, 
                **kwargs: Any
            ) -> Iterable[BillingSubscriptionAlias]: ...


    class azure.mgmt.billing.operations.BillingSubscriptionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

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
                expand: Optional[str] = None, 
                **kwargs: Any
            ) -> BillingSubscription: ...

        @distributed_trace
        def get_by_billing_profile(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                billing_subscription_name: str, 
                expand: Optional[str] = None, 
                **kwargs: Any
            ) -> BillingSubscription: ...

        @distributed_trace
        def list_by_billing_account(
                self, 
                billing_account_name: str, 
                include_deleted: bool = False, 
                include_tenant_subscriptions: bool = False, 
                include_failed: bool = False, 
                expand: Optional[str] = None, 
                filter: Optional[str] = None, 
                order_by: Optional[str] = None, 
                top: Optional[int] = None, 
                skip: Optional[int] = None, 
                count: Optional[bool] = None, 
                search: Optional[str] = None, 
                **kwargs: Any
            ) -> Iterable[BillingSubscription]: ...

        @distributed_trace
        def list_by_billing_profile(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                include_deleted: bool = False, 
                expand: Optional[str] = None, 
                filter: Optional[str] = None, 
                order_by: Optional[str] = None, 
                top: Optional[int] = None, 
                skip: Optional[int] = None, 
                count: Optional[bool] = None, 
                search: Optional[str] = None, 
                **kwargs: Any
            ) -> Iterable[BillingSubscription]: ...

        @distributed_trace
        def list_by_customer(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                customer_name: str, 
                include_deleted: bool = False, 
                expand: Optional[str] = None, 
                filter: Optional[str] = None, 
                order_by: Optional[str] = None, 
                top: Optional[int] = None, 
                skip: Optional[int] = None, 
                count: Optional[bool] = None, 
                search: Optional[str] = None, 
                **kwargs: Any
            ) -> Iterable[BillingSubscription]: ...

        @distributed_trace
        def list_by_customer_at_billing_account(
                self, 
                billing_account_name: str, 
                customer_name: str, 
                include_deleted: bool = False, 
                expand: Optional[str] = None, 
                filter: Optional[str] = None, 
                order_by: Optional[str] = None, 
                top: Optional[int] = None, 
                skip: Optional[int] = None, 
                count: Optional[bool] = None, 
                search: Optional[str] = None, 
                **kwargs: Any
            ) -> Iterable[BillingSubscription]: ...

        @distributed_trace
        def list_by_enrollment_account(
                self, 
                billing_account_name: str, 
                enrollment_account_name: str, 
                filter: Optional[str] = None, 
                order_by: Optional[str] = None, 
                top: Optional[int] = None, 
                skip: Optional[int] = None, 
                count: Optional[bool] = None, 
                search: Optional[str] = None, 
                **kwargs: Any
            ) -> Iterable[BillingSubscription]: ...

        @distributed_trace
        def list_by_invoice_section(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                invoice_section_name: str, 
                include_deleted: bool = False, 
                expand: Optional[str] = None, 
                filter: Optional[str] = None, 
                order_by: Optional[str] = None, 
                top: Optional[int] = None, 
                skip: Optional[int] = None, 
                count: Optional[bool] = None, 
                search: Optional[str] = None, 
                **kwargs: Any
            ) -> Iterable[BillingSubscription]: ...

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
            ): ...

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
                expand: Optional[str] = None, 
                filter: Optional[str] = None, 
                order_by: Optional[str] = None, 
                top: Optional[int] = None, 
                skip: Optional[int] = None, 
                count: Optional[bool] = None, 
                search: Optional[str] = None, 
                **kwargs: Any
            ) -> Iterable[Customer]: ...

        @distributed_trace
        def list_by_billing_profile(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                expand: Optional[str] = None, 
                filter: Optional[str] = None, 
                order_by: Optional[str] = None, 
                top: Optional[int] = None, 
                skip: Optional[int] = None, 
                count: Optional[bool] = None, 
                search: Optional[str] = None, 
                **kwargs: Any
            ) -> Iterable[Customer]: ...


    class azure.mgmt.billing.operations.DepartmentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

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
                filter: Optional[str] = None, 
                order_by: Optional[str] = None, 
                top: Optional[int] = None, 
                skip: Optional[int] = None, 
                search: Optional[str] = None, 
                **kwargs: Any
            ) -> Iterable[Department]: ...


    class azure.mgmt.billing.operations.EnrollmentAccountsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

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
                filter: Optional[str] = None, 
                order_by: Optional[str] = None, 
                top: Optional[int] = None, 
                skip: Optional[int] = None, 
                count: Optional[bool] = None, 
                search: Optional[str] = None, 
                **kwargs: Any
            ) -> Iterable[EnrollmentAccount]: ...

        @distributed_trace
        def list_by_department(
                self, 
                billing_account_name: str, 
                department_name: str, 
                filter: Optional[str] = None, 
                order_by: Optional[str] = None, 
                top: Optional[int] = None, 
                skip: Optional[int] = None, 
                count: Optional[bool] = None, 
                search: Optional[str] = None, 
                **kwargs: Any
            ) -> Iterable[EnrollmentAccount]: ...


    class azure.mgmt.billing.operations.InvoiceSectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

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
                include_deleted: bool = False, 
                filter: Optional[str] = None, 
                order_by: Optional[str] = None, 
                top: Optional[int] = None, 
                skip: Optional[int] = None, 
                count: Optional[bool] = None, 
                search: Optional[str] = None, 
                **kwargs: Any
            ) -> Iterable[InvoiceSection]: ...

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
            ): ...

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
                document_name: Optional[str] = None, 
                **kwargs: Any
            ) -> LROPoller[DocumentDownloadResult]: ...

        @distributed_trace
        def begin_download_by_billing_subscription(
                self, 
                invoice_name: str, 
                document_name: Optional[str] = None, 
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
                period_start_date: Optional[date] = None, 
                period_end_date: Optional[date] = None, 
                filter: Optional[str] = None, 
                order_by: Optional[str] = None, 
                top: Optional[int] = None, 
                skip: Optional[int] = None, 
                count: Optional[bool] = None, 
                search: Optional[str] = None, 
                **kwargs: Any
            ) -> Iterable[Invoice]: ...

        @distributed_trace
        def list_by_billing_profile(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                period_start_date: Optional[date] = None, 
                period_end_date: Optional[date] = None, 
                filter: Optional[str] = None, 
                order_by: Optional[str] = None, 
                top: Optional[int] = None, 
                skip: Optional[int] = None, 
                count: Optional[bool] = None, 
                search: Optional[str] = None, 
                **kwargs: Any
            ) -> Iterable[Invoice]: ...

        @distributed_trace
        def list_by_billing_subscription(
                self, 
                period_start_date: Optional[date] = None, 
                period_end_date: Optional[date] = None, 
                filter: Optional[str] = None, 
                order_by: Optional[str] = None, 
                top: Optional[int] = None, 
                skip: Optional[int] = None, 
                count: Optional[bool] = None, 
                search: Optional[str] = None, 
                **kwargs: Any
            ) -> Iterable[Invoice]: ...


    class azure.mgmt.billing.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def list(self, **kwargs: Any) -> Iterable[Operation]: ...


    class azure.mgmt.billing.operations.PartnerTransfersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

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
            ) -> Iterable[PartnerTransferDetails]: ...


    class azure.mgmt.billing.operations.PaymentMethodsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

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
            ) -> Iterable[PaymentMethod]: ...

        @distributed_trace
        def list_by_billing_profile(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                **kwargs: Any
            ) -> Iterable[PaymentMethodLink]: ...

        @distributed_trace
        def list_by_user(self, **kwargs: Any) -> Iterable[PaymentMethod]: ...


    class azure.mgmt.billing.operations.PoliciesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

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
            ): ...

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
                filter: Optional[str] = None, 
                order_by: Optional[str] = None, 
                top: Optional[int] = None, 
                skip: Optional[int] = None, 
                count: Optional[bool] = None, 
                search: Optional[str] = None, 
                **kwargs: Any
            ) -> Iterable[Product]: ...

        @distributed_trace
        def list_by_billing_profile(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                filter: Optional[str] = None, 
                order_by: Optional[str] = None, 
                top: Optional[int] = None, 
                skip: Optional[int] = None, 
                count: Optional[bool] = None, 
                search: Optional[str] = None, 
                **kwargs: Any
            ) -> Iterable[Product]: ...

        @distributed_trace
        def list_by_customer(
                self, 
                billing_account_name: str, 
                customer_name: str, 
                filter: Optional[str] = None, 
                order_by: Optional[str] = None, 
                top: Optional[int] = None, 
                skip: Optional[int] = None, 
                count: Optional[bool] = None, 
                search: Optional[str] = None, 
                **kwargs: Any
            ) -> Iterable[Product]: ...

        @distributed_trace
        def list_by_invoice_section(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                invoice_section_name: str, 
                filter: Optional[str] = None, 
                order_by: Optional[str] = None, 
                top: Optional[int] = None, 
                skip: Optional[int] = None, 
                count: Optional[bool] = None, 
                search: Optional[str] = None, 
                **kwargs: Any
            ) -> Iterable[Product]: ...

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
            ): ...

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
        def list(self, **kwargs: Any) -> Iterable[RecipientTransferDetails]: ...

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
            ): ...

        @distributed_trace
        def get_by_billing_account(
                self, 
                billing_account_name: str, 
                reservation_order_id: str, 
                expand: Optional[str] = None, 
                **kwargs: Any
            ) -> ReservationOrder: ...

        @distributed_trace
        def list_by_billing_account(
                self, 
                billing_account_name: str, 
                filter: Optional[str] = None, 
                order_by: Optional[str] = None, 
                skiptoken: Optional[float] = None, 
                **kwargs: Any
            ) -> Iterable[ReservationOrder]: ...


    class azure.mgmt.billing.operations.ReservationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

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
                expand: Optional[str] = None, 
                **kwargs: Any
            ) -> Reservation: ...

        @distributed_trace
        def list_by_billing_account(
                self, 
                billing_account_name: str, 
                filter: Optional[str] = None, 
                order_by: Optional[str] = None, 
                skiptoken: Optional[float] = None, 
                refresh_summary: Optional[str] = None, 
                selected_state: Optional[str] = None, 
                take: Optional[float] = None, 
                **kwargs: Any
            ) -> Iterable[Reservation]: ...

        @distributed_trace
        def list_by_billing_profile(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                filter: Optional[str] = None, 
                order_by: Optional[str] = None, 
                skiptoken: Optional[float] = None, 
                refresh_summary: Optional[str] = None, 
                selected_state: Optional[str] = None, 
                take: Optional[float] = None, 
                **kwargs: Any
            ) -> Iterable[Reservation]: ...

        @distributed_trace
        def list_by_reservation_order(
                self, 
                billing_account_name: str, 
                reservation_order_id: str, 
                **kwargs: Any
            ) -> Iterable[Reservation]: ...


    class azure.mgmt.billing.operations.SavingsPlanOrdersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get_by_billing_account(
                self, 
                billing_account_name: str, 
                savings_plan_order_id: str, 
                expand: Optional[str] = None, 
                **kwargs: Any
            ) -> SavingsPlanOrderModel: ...

        @distributed_trace
        def list_by_billing_account(
                self, 
                billing_account_name: str, 
                filter: Optional[str] = None, 
                order_by: Optional[str] = None, 
                skiptoken: Optional[float] = None, 
                **kwargs: Any
            ) -> Iterable[SavingsPlanOrderModel]: ...


    class azure.mgmt.billing.operations.SavingsPlansOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

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
                expand: Optional[str] = None, 
                **kwargs: Any
            ) -> SavingsPlanModel: ...

        @distributed_trace
        def list_by_billing_account(
                self, 
                billing_account_name: str, 
                filter: Optional[str] = None, 
                order_by: Optional[str] = None, 
                skiptoken: Optional[float] = None, 
                take: Optional[float] = None, 
                selected_state: Optional[str] = None, 
                refresh_summary: Optional[str] = None, 
                **kwargs: Any
            ) -> Iterable[SavingsPlanModel]: ...

        @distributed_trace
        def list_by_savings_plan_order(
                self, 
                billing_account_name: str, 
                savings_plan_order_id: str, 
                **kwargs: Any
            ) -> Iterable[SavingsPlanModel]: ...

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
            ): ...

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
                filter: Optional[str] = None, 
                search: Optional[str] = None, 
                **kwargs: Any
            ) -> TransactionSummary: ...

        @distributed_trace
        def list_by_billing_profile(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                period_start_date: date, 
                period_end_date: date, 
                type: Union[str, TransactionType], 
                filter: Optional[str] = None, 
                order_by: Optional[str] = None, 
                top: Optional[int] = None, 
                skip: Optional[int] = None, 
                count: Optional[bool] = None, 
                search: Optional[str] = None, 
                **kwargs: Any
            ) -> Iterable[Transaction]: ...

        @distributed_trace
        def list_by_customer(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                customer_name: str, 
                period_start_date: date, 
                period_end_date: date, 
                type: Union[str, TransactionType], 
                filter: Optional[str] = None, 
                order_by: Optional[str] = None, 
                top: Optional[int] = None, 
                skip: Optional[int] = None, 
                count: Optional[bool] = None, 
                search: Optional[str] = None, 
                **kwargs: Any
            ) -> Iterable[Transaction]: ...

        @distributed_trace
        def list_by_invoice(
                self, 
                billing_account_name: str, 
                invoice_name: str, 
                filter: Optional[str] = None, 
                order_by: Optional[str] = None, 
                top: Optional[int] = None, 
                skip: Optional[int] = None, 
                count: Optional[bool] = None, 
                search: Optional[str] = None, 
                **kwargs: Any
            ) -> Iterable[Transaction]: ...

        @distributed_trace
        def list_by_invoice_section(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                invoice_section_name: str, 
                period_start_date: date, 
                period_end_date: date, 
                type: Union[str, TransactionType], 
                filter: Optional[str] = None, 
                order_by: Optional[str] = None, 
                top: Optional[int] = None, 
                skip: Optional[int] = None, 
                count: Optional[bool] = None, 
                search: Optional[str] = None, 
                **kwargs: Any
            ) -> Iterable[Transaction]: ...


    class azure.mgmt.billing.operations.TransfersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

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
            ) -> Iterable[TransferDetails]: ...


```