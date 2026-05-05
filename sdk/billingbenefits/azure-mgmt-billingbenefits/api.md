```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.billingbenefits

    class azure.mgmt.billingbenefits.BillingBenefitsMgmtClient: implements ContextManager 
        applicable_maccs: ApplicableMaccsOperations
        benefit: BenefitOperations
        conditional_credit_contributors: ConditionalCreditContributorsOperations
        conditional_credits: ConditionalCreditsOperations
        contributors: ContributorsOperations
        credits: CreditsOperations
        discount: DiscountOperations
        discounts: DiscountsOperations
        free_services: FreeServicesOperations
        maccs: MaccsOperations
        operations: Operations
        reservation_order_alias: ReservationOrderAliasOperations
        savings_plan: SavingsPlanOperations
        savings_plan_order: SavingsPlanOrderOperations
        savings_plan_order_alias: SavingsPlanOrderAliasOperations
        seller_resource: SellerResourceOperations
        sources: SourcesOperations

        def __init__(
                self, 
                credential: TokenCredential, 
                subscription_id: str, 
                base_url: Optional[str] = None, 
                expand: Optional[str] = None, 
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


namespace azure.mgmt.billingbenefits.aio

    class azure.mgmt.billingbenefits.aio.BillingBenefitsMgmtClient: implements AsyncContextManager 
        applicable_maccs: ApplicableMaccsOperations
        benefit: BenefitOperations
        conditional_credit_contributors: ConditionalCreditContributorsOperations
        conditional_credits: ConditionalCreditsOperations
        contributors: ContributorsOperations
        credits: CreditsOperations
        discount: DiscountOperations
        discounts: DiscountsOperations
        free_services: FreeServicesOperations
        maccs: MaccsOperations
        operations: Operations
        reservation_order_alias: ReservationOrderAliasOperations
        savings_plan: SavingsPlanOperations
        savings_plan_order: SavingsPlanOrderOperations
        savings_plan_order_alias: SavingsPlanOrderAliasOperations
        seller_resource: SellerResourceOperations
        sources: SourcesOperations

        def __init__(
                self, 
                credential: AsyncTokenCredential, 
                subscription_id: str, 
                base_url: Optional[str] = None, 
                expand: Optional[str] = None, 
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


namespace azure.mgmt.billingbenefits.aio.operations

    class azure.mgmt.billingbenefits.aio.operations.ApplicableMaccsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                billing_account_id: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ApplicableMacc]: ...


    class azure.mgmt.billingbenefits.aio.operations.BenefitOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def validate(
                self, 
                body: BenefitValidateRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> BenefitValidateResponse: ...

        @overload
        async def validate(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> BenefitValidateResponse: ...

        @overload
        async def validate(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> BenefitValidateResponse: ...


    class azure.mgmt.billingbenefits.aio.operations.ConditionalCreditContributorsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get_from_primary(
                self, 
                resource_group_name: str, 
                conditional_credit_name: str, 
                contributor_name: str, 
                **kwargs: Any
            ) -> ConditionalCreditContributor: ...

        @distributed_trace
        def list_from_applicable_conditional_credit(
                self, 
                billing_account_id: str, 
                system_id: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ConditionalCreditContributor]: ...

        @distributed_trace
        def list_from_primary(
                self, 
                resource_group_name: str, 
                conditional_credit_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ConditionalCreditContributor]: ...


    class azure.mgmt.billingbenefits.aio.operations.ConditionalCreditsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_cancel(
                self, 
                resource_group_name: str, 
                conditional_credit_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[ConditionalCredit]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                conditional_credit_name: str, 
                body: ConditionalCredit, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ConditionalCredit]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                conditional_credit_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ConditionalCredit]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                conditional_credit_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ConditionalCredit]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                conditional_credit_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                conditional_credit_name: str, 
                body: ConditionalCreditPatchRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ConditionalCredit]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                conditional_credit_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ConditionalCredit]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                conditional_credit_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ConditionalCredit]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                conditional_credit_name: str, 
                **kwargs: Any
            ) -> ConditionalCredit: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ConditionalCredit]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[ConditionalCredit]: ...

        @distributed_trace
        def scope_list(
                self, 
                scope: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ConditionalCredit]: ...


    class azure.mgmt.billingbenefits.aio.operations.ContributorsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get_from_primary(
                self, 
                resource_group_name: str, 
                macc_name: str, 
                contributor_name: str, 
                **kwargs: Any
            ) -> Contributor: ...

        @distributed_trace
        def list_from_applicable_macc(
                self, 
                billing_account_id: str, 
                system_id: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Contributor]: ...

        @distributed_trace
        def list_from_primary(
                self, 
                resource_group_name: str, 
                macc_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Contributor]: ...


    class azure.mgmt.billingbenefits.aio.operations.CreditsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_cancel(
                self, 
                resource_group_name: str, 
                credit_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[Credit]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                credit_name: str, 
                body: Credit, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Credit]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                credit_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Credit]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                credit_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Credit]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                credit_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                credit_name: str, 
                body: CreditPatchRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Credit]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                credit_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Credit]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                credit_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Credit]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                credit_name: str, 
                **kwargs: Any
            ) -> Credit: ...

        @distributed_trace
        def list_applicable(
                self, 
                scope: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Credit]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Credit]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[Credit]: ...


    class azure.mgmt.billingbenefits.aio.operations.DiscountOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                discount_name: str, 
                body: DiscountPatchRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Discount]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                discount_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Discount]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                discount_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Discount]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                discount_name: str, 
                **kwargs: Any
            ) -> Discount: ...


    class azure.mgmt.billingbenefits.aio.operations.DiscountsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_cancel(
                self, 
                resource_group_name: str, 
                discount_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[Discount]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                discount_name: str, 
                body: Discount, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Discount]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                discount_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Discount]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                discount_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Discount]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                discount_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace
        def resource_group_list(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Discount]: ...

        @distributed_trace
        def scope_list(
                self, 
                scope: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Discount]: ...

        @distributed_trace
        def subscription_list(self, **kwargs: Any) -> AsyncItemPaged[Discount]: ...


    class azure.mgmt.billingbenefits.aio.operations.FreeServicesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                free_service_name: str, 
                body: FreeServices, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[FreeServices]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                free_service_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[FreeServices]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                free_service_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[FreeServices]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                free_service_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                free_service_name: str, 
                body: FreeServicesPatchRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[FreeServices]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                free_service_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[FreeServices]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                free_service_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[FreeServices]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                free_service_name: str, 
                **kwargs: Any
            ) -> FreeServices: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[FreeServices]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[FreeServices]: ...


    class azure.mgmt.billingbenefits.aio.operations.MaccsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_cancel(
                self, 
                resource_group_name: str, 
                macc_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[Macc]: ...

        @overload
        async def begin_charge_shortfall(
                self, 
                resource_group_name: str, 
                macc_name: str, 
                body: ChargeShortfallRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Macc]: ...

        @overload
        async def begin_charge_shortfall(
                self, 
                resource_group_name: str, 
                macc_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Macc]: ...

        @overload
        async def begin_charge_shortfall(
                self, 
                resource_group_name: str, 
                macc_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Macc]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                macc_name: str, 
                body: Macc, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Macc]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                macc_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Macc]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                macc_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Macc]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                macc_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                macc_name: str, 
                body: MaccPatchRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Macc]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                macc_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Macc]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                macc_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Macc]: ...

        @distributed_trace_async
        async def begin_write_off(
                self, 
                resource_group_name: str, 
                macc_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[Macc]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                macc_name: str, 
                **kwargs: Any
            ) -> Macc: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Macc]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[Macc]: ...


    class azure.mgmt.billingbenefits.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


    class azure.mgmt.billingbenefits.aio.operations.ReservationOrderAliasOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                reservation_order_alias_name: str, 
                body: ReservationOrderAliasRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ReservationOrderAliasResponse]: ...

        @overload
        async def begin_create(
                self, 
                reservation_order_alias_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ReservationOrderAliasResponse]: ...

        @overload
        async def begin_create(
                self, 
                reservation_order_alias_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ReservationOrderAliasResponse]: ...

        @distributed_trace_async
        async def get(
                self, 
                reservation_order_alias_name: str, 
                **kwargs: Any
            ) -> ReservationOrderAliasResponse: ...


    class azure.mgmt.billingbenefits.aio.operations.SavingsPlanOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_update(
                self, 
                savings_plan_order_id: str, 
                savings_plan_id: str, 
                body: SavingsPlanUpdateRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SavingsPlanModel]: ...

        @overload
        async def begin_update(
                self, 
                savings_plan_order_id: str, 
                savings_plan_id: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SavingsPlanModel]: ...

        @overload
        async def begin_update(
                self, 
                savings_plan_order_id: str, 
                savings_plan_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SavingsPlanModel]: ...

        @distributed_trace_async
        async def get(
                self, 
                savings_plan_order_id: str, 
                savings_plan_id: str, 
                **kwargs: Any
            ) -> SavingsPlanModel: ...

        @distributed_trace
        def list(
                self, 
                savings_plan_order_id: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[SavingsPlanModel]: ...

        @distributed_trace
        def list_all(
                self, 
                *, 
                filter: Optional[str] = ..., 
                orderby: Optional[str] = ..., 
                refresh_summary: Optional[str] = ..., 
                selected_state: Optional[str] = ..., 
                skiptoken: Optional[float] = ..., 
                take: Optional[float] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[SavingsPlanModel]: ...

        @overload
        async def validate_update(
                self, 
                savings_plan_order_id: str, 
                savings_plan_id: str, 
                body: SavingsPlanUpdateValidateRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SavingsPlanValidateResponse: ...

        @overload
        async def validate_update(
                self, 
                savings_plan_order_id: str, 
                savings_plan_id: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SavingsPlanValidateResponse: ...

        @overload
        async def validate_update(
                self, 
                savings_plan_order_id: str, 
                savings_plan_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SavingsPlanValidateResponse: ...


    class azure.mgmt.billingbenefits.aio.operations.SavingsPlanOrderAliasOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                savings_plan_order_alias_name: str, 
                body: SavingsPlanOrderAliasModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SavingsPlanOrderAliasModel]: ...

        @overload
        async def begin_create(
                self, 
                savings_plan_order_alias_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SavingsPlanOrderAliasModel]: ...

        @overload
        async def begin_create(
                self, 
                savings_plan_order_alias_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SavingsPlanOrderAliasModel]: ...

        @distributed_trace_async
        async def get(
                self, 
                savings_plan_order_alias_name: str, 
                **kwargs: Any
            ) -> SavingsPlanOrderAliasModel: ...


    class azure.mgmt.billingbenefits.aio.operations.SavingsPlanOrderOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def elevate(
                self, 
                savings_plan_order_id: str, 
                **kwargs: Any
            ) -> RoleAssignmentEntity: ...

        @distributed_trace_async
        async def get(
                self, 
                savings_plan_order_id: str, 
                **kwargs: Any
            ) -> SavingsPlanOrderModel: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[SavingsPlanOrderModel]: ...


    class azure.mgmt.billingbenefits.aio.operations.SellerResourceOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def list(
                self, 
                body: SellerResourceListRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> List[Macc]: ...

        @overload
        async def list(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> List[Macc]: ...

        @overload
        async def list(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> List[Macc]: ...


    class azure.mgmt.billingbenefits.aio.operations.SourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                credit_name: str, 
                source_name: str, 
                body: CreditSource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CreditSource: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                credit_name: str, 
                source_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CreditSource: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                credit_name: str, 
                source_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CreditSource: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                credit_name: str, 
                source_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                credit_name: str, 
                source_name: str, 
                **kwargs: Any
            ) -> CreditSource: ...

        @distributed_trace
        def list_by_credit(
                self, 
                resource_group_name: str, 
                credit_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[CreditSource]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                credit_name: str, 
                source_name: str, 
                body: CreditSourcePatchRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CreditSource: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                credit_name: str, 
                source_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CreditSource: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                credit_name: str, 
                source_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CreditSource: ...


namespace azure.mgmt.billingbenefits.models

    class azure.mgmt.billingbenefits.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.billingbenefits.models.ApplicableMacc(ProxyResource):
        id: str
        name: str
        properties: Optional[MaccModelProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[MaccModelProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.billingbenefits.models.AppliedScopeProperties(_Model):
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


    class azure.mgmt.billingbenefits.models.AppliedScopeType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MANAGEMENT_GROUP = "ManagementGroup"
        SHARED = "Shared"
        SINGLE = "Single"


    class azure.mgmt.billingbenefits.models.ApplyDiscountOn(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONSUME = "Consume"
        PURCHASE = "Purchase"
        RENEW = "Renew"


    class azure.mgmt.billingbenefits.models.AutomaticShortfallSuppressReason(_Model):
        code: Optional[str]
        message: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                message: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billingbenefits.models.Award(_Model):
        balance_version: Optional[float]
        credit: Optional[Commitment]
        duration: Optional[Union[str, Term]]
        end_at: Optional[datetime]
        resource_id: Optional[str]
        start_at: Optional[datetime]
        system_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                credit: Optional[Commitment] = ..., 
                duration: Optional[Union[str, Term]] = ..., 
                end_at: Optional[datetime] = ..., 
                start_at: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billingbenefits.models.BenefitType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONDITIONAL_CREDITS = "ConditionalCredits"
        CREDITS = "Credits"
        MACC = "MACC"
        SAVINGS_PLAN = "SavingsPlan"


    class azure.mgmt.billingbenefits.models.BenefitValidateModel(_Model):
        benefit_type: str

        @overload
        def __init__(
                self, 
                *, 
                benefit_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billingbenefits.models.BenefitValidateRequest(_Model):
        benefits: Optional[list[BenefitValidateModel]]

        @overload
        def __init__(
                self, 
                *, 
                benefits: Optional[list[BenefitValidateModel]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billingbenefits.models.BenefitValidateResponse(_Model):
        benefits: Optional[list[BenefitValidateResponseProperty]]
        next_link: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                benefits: Optional[list[BenefitValidateResponseProperty]] = ..., 
                next_link: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billingbenefits.models.BenefitValidateResponseProperty(_Model):
        reason: Optional[str]
        reason_code: Optional[str]
        resource_id: Optional[str]
        valid: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                reason: Optional[str] = ..., 
                reason_code: Optional[str] = ..., 
                resource_id: Optional[str] = ..., 
                valid: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billingbenefits.models.BillingPlan(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        P1_M = "P1M"


    class azure.mgmt.billingbenefits.models.BillingPlanInformation(_Model):
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


    class azure.mgmt.billingbenefits.models.CatalogClaimsItem(_Model):
        catalog_claims_item_type: Optional[str]
        value: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                catalog_claims_item_type: Optional[str] = ..., 
                value: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billingbenefits.models.ChargeShortfallRequest(_Model):
        properties: Optional[Shortfall]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[Shortfall] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.billingbenefits.models.Commitment(Price):
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


    class azure.mgmt.billingbenefits.models.CommitmentGrain(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FULL_TERM = "FullTerm"
        HOURLY = "Hourly"
        UNKNOWN = "Unknown"


    class azure.mgmt.billingbenefits.models.ConditionalCredit(TrackedResource):
        etag: Optional[str]
        id: str
        identity: Optional[ManagedServiceIdentity]
        kind: Optional[str]
        location: str
        managed_by: Optional[str]
        name: str
        plan: Optional[Plan]
        properties: Optional[ConditionalCreditProperties]
        sku: Optional[Sku]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                kind: Optional[str] = ..., 
                location: str, 
                managed_by: Optional[str] = ..., 
                plan: Optional[Plan] = ..., 
                properties: Optional[ConditionalCreditProperties] = ..., 
                sku: Optional[Sku] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billingbenefits.models.ConditionalCreditContributor(ProxyResource):
        id: str
        name: str
        properties: Optional[ContributorConditionalCreditProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ContributorConditionalCreditProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.billingbenefits.models.ConditionalCreditEntityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONTRIBUTOR = "Contributor"
        PRIMARY = "Primary"


    class azure.mgmt.billingbenefits.models.ConditionalCreditMilestone(ConditionalCreditMilestoneBase):
        award: Award
        end_at: datetime
        milestone_id: str
        name: str
        spend_target: Price
        status: Union[str, MilestoneStatus]

        @overload
        def __init__(
                self, 
                *, 
                award: Optional[Award] = ..., 
                end_at: Optional[datetime] = ..., 
                milestone_id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                spend_target: Optional[Price] = ..., 
                status: Optional[Union[str, MilestoneStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billingbenefits.models.ConditionalCreditMilestoneBase(_Model):
        award: Optional[Award]
        end_at: Optional[datetime]
        milestone_id: Optional[str]
        name: Optional[str]
        spend_target: Optional[Price]
        status: Optional[Union[str, MilestoneStatus]]

        @overload
        def __init__(
                self, 
                *, 
                award: Optional[Award] = ..., 
                end_at: Optional[datetime] = ..., 
                milestone_id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                spend_target: Optional[Price] = ..., 
                status: Optional[Union[str, MilestoneStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billingbenefits.models.ConditionalCreditPatchRequest(_Model):
        properties: Optional[ConditionalCreditPatchRequestProperties]
        tags: Optional[dict[str, str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ConditionalCreditPatchRequestProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.billingbenefits.models.ConditionalCreditPatchRequestProperties(_Model):
        allow_contributors: Optional[Union[str, EnablementMode]]
        display_name: Optional[str]
        end_at: Optional[datetime]
        milestones: Optional[list[ConditionalCreditMilestone]]

        @overload
        def __init__(
                self, 
                *, 
                allow_contributors: Optional[Union[str, EnablementMode]] = ..., 
                display_name: Optional[str] = ..., 
                end_at: Optional[datetime] = ..., 
                milestones: Optional[list[ConditionalCreditMilestone]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billingbenefits.models.ConditionalCreditProperties(_Model):
        benefit_resource_id: Optional[str]
        billing_account_resource_id: Optional[str]
        display_name: Optional[str]
        end_at: Optional[datetime]
        entity_type: str
        product_code: Optional[str]
        provisioning_state: Optional[Union[str, ConditionalCreditsProvisioningState]]
        resource_id: Optional[str]
        start_at: Optional[datetime]
        status: Optional[Union[str, ConditionalCreditStatus]]

        @overload
        def __init__(
                self, 
                *, 
                billing_account_resource_id: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                end_at: Optional[datetime] = ..., 
                entity_type: str, 
                product_code: Optional[str] = ..., 
                resource_id: Optional[str] = ..., 
                start_at: Optional[datetime] = ..., 
                status: Optional[Union[str, ConditionalCreditStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billingbenefits.models.ConditionalCreditStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        CANCELED = "Canceled"
        COMPLETED = "Completed"
        FAILED = "Failed"
        PENDING = "Pending"
        PENDING_SETTLEMENT = "PendingSettlement"
        SCHEDULED = "Scheduled"
        STOPPED = "Stopped"
        UNKNOWN = "Unknown"


    class azure.mgmt.billingbenefits.models.ConditionalCreditsProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        FAILED = "Failed"
        PENDING = "Pending"
        SUCCEEDED = "Succeeded"
        UNKNOWN = "Unknown"


    class azure.mgmt.billingbenefits.models.ConditionalCreditsValidateModel(BenefitValidateModel, discriminator='ConditionalCredits'):
        benefit_type: Literal[BenefitType.CONDITIONAL_CREDITS]
        properties: Optional[ConditionalCreditProperties]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ConditionalCreditProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billingbenefits.models.ConditionsItem(_Model):
        condition_name: Optional[str]
        type: Optional[str]
        value: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                condition_name: Optional[str] = ..., 
                type: Optional[str] = ..., 
                value: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billingbenefits.models.Contributor(ProxyResource):
        id: str
        name: str
        properties: Optional[MaccModelProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[MaccModelProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.billingbenefits.models.ContributorConditionalCreditMilestone(ConditionalCreditMilestoneBase):
        award: Award
        end_at: datetime
        milestone_id: str
        name: str
        spend_target: Price
        status: Union[str, MilestoneStatus]

        @overload
        def __init__(
                self, 
                *, 
                award: Optional[Award] = ..., 
                end_at: Optional[datetime] = ..., 
                milestone_id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                spend_target: Optional[Price] = ..., 
                status: Optional[Union[str, MilestoneStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billingbenefits.models.ContributorConditionalCreditProperties(ConditionalCreditProperties, discriminator='Contributor'):
        benefit_resource_id: str
        billing_account_resource_id: str
        display_name: str
        end_at: datetime
        entity_type: Literal[ConditionalCreditEntityType.CONTRIBUTOR]
        milestones: Optional[list[ContributorConditionalCreditMilestone]]
        primary_billing_account_resource_id: Optional[str]
        primary_resource_id: Optional[str]
        product_code: str
        provisioning_state: Union[str, ConditionalCreditsProvisioningState]
        resource_id: str
        start_at: datetime
        status: Union[str, ConditionalCreditStatus]
        system_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                billing_account_resource_id: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                end_at: Optional[datetime] = ..., 
                primary_billing_account_resource_id: Optional[str] = ..., 
                primary_resource_id: Optional[str] = ..., 
                product_code: Optional[str] = ..., 
                resource_id: Optional[str] = ..., 
                start_at: Optional[datetime] = ..., 
                status: Optional[Union[str, ConditionalCreditStatus]] = ..., 
                system_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billingbenefits.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.billingbenefits.models.Credit(TrackedResource):
        etag: Optional[str]
        id: str
        identity: Optional[ManagedServiceIdentity]
        kind: Optional[str]
        location: str
        managed_by: Optional[str]
        name: str
        plan: Optional[Plan]
        properties: Optional[CreditProperties]
        sku: Optional[Sku]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                kind: Optional[str] = ..., 
                location: str, 
                managed_by: Optional[str] = ..., 
                plan: Optional[Plan] = ..., 
                properties: Optional[CreditProperties] = ..., 
                sku: Optional[Sku] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.billingbenefits.models.CreditBreakdownItem(_Model):
        allocation: Optional[Commitment]
        dimensions: Optional[list[CreditDimension]]
        end_at: Optional[datetime]
        start_at: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                allocation: Optional[Commitment] = ..., 
                dimensions: Optional[list[CreditDimension]] = ..., 
                end_at: Optional[datetime] = ..., 
                start_at: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billingbenefits.models.CreditDimension(_Model):
        key: str
        value: str

        @overload
        def __init__(
                self, 
                *, 
                key: str, 
                value: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billingbenefits.models.CreditExpirationPolicy(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SUSPEND_BILLING_PROFILE = "SuspendBillingProfile"


    class azure.mgmt.billingbenefits.models.CreditPatchProperties(_Model):
        breakdown: Optional[list[CreditBreakdownItem]]
        credit: Optional[Commitment]
        end_at: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                breakdown: Optional[list[CreditBreakdownItem]] = ..., 
                credit: Optional[Commitment] = ..., 
                end_at: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billingbenefits.models.CreditPatchRequest(_Model):
        properties: Optional[CreditPatchProperties]
        tags: Optional[dict[str, str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[CreditPatchProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.billingbenefits.models.CreditPolicies(_Model):
        expiration: Optional[Union[str, CreditExpirationPolicy]]
        redemption: Optional[Union[str, CreditRedemptionPolicy]]

        @overload
        def __init__(
                self, 
                *, 
                expiration: Optional[Union[str, CreditExpirationPolicy]] = ..., 
                redemption: Optional[Union[str, CreditRedemptionPolicy]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billingbenefits.models.CreditProperties(_Model):
        billing_account_resource_id: Optional[str]
        billing_profile_resource_id: Optional[str]
        breakdown: Optional[list[CreditBreakdownItem]]
        credit: Optional[Commitment]
        customer_id: Optional[str]
        end_at: Optional[datetime]
        policies: Optional[CreditPolicies]
        product_code: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        reason: Optional[CreditReason]
        resource_id: Optional[str]
        start_at: Optional[datetime]
        status: Optional[Union[str, CreditStatus]]
        system_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                billing_account_resource_id: Optional[str] = ..., 
                breakdown: Optional[list[CreditBreakdownItem]] = ..., 
                credit: Optional[Commitment] = ..., 
                end_at: Optional[datetime] = ..., 
                policies: Optional[CreditPolicies] = ..., 
                product_code: Optional[str] = ..., 
                reason: Optional[CreditReason] = ..., 
                resource_id: Optional[str] = ..., 
                start_at: Optional[datetime] = ..., 
                status: Optional[Union[str, CreditStatus]] = ..., 
                system_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billingbenefits.models.CreditReason(_Model):
        code: Optional[str]
        description: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                description: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billingbenefits.models.CreditRedemptionPolicy(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTO_REDEEM = "AutoRedeem"
        MANUAL_REDEEM = "ManualRedeem"
        NOT_APPLICABLE = "NotApplicable"


    class azure.mgmt.billingbenefits.models.CreditSource(TrackedResource):
        etag: Optional[str]
        id: str
        identity: Optional[ManagedServiceIdentity]
        kind: Optional[str]
        location: str
        managed_by: Optional[str]
        name: str
        plan: Optional[Plan]
        properties: Optional[CreditSourceProperties]
        sku: Optional[Sku]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                kind: Optional[str] = ..., 
                location: str, 
                managed_by: Optional[str] = ..., 
                plan: Optional[Plan] = ..., 
                properties: Optional[CreditSourceProperties] = ..., 
                sku: Optional[Sku] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.billingbenefits.models.CreditSourcePatchRequest(_Model):
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billingbenefits.models.CreditSourceProperties(_Model):
        credit: Optional[Commitment]
        impacted_billing_period: Optional[str]
        source_resource_id: Optional[str]
        status: Optional[Union[str, CreditStatus]]

        @overload
        def __init__(
                self, 
                *, 
                credit: Optional[Commitment] = ..., 
                impacted_billing_period: Optional[str] = ..., 
                source_resource_id: Optional[str] = ..., 
                status: Optional[Union[str, CreditStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billingbenefits.models.CreditStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        CANCELED = "Canceled"
        EXHAUSTED = "Exhausted"
        EXPIRED = "Expired"
        FAILED = "Failed"
        NOT_STARTED = "NotStarted"
        PENDING = "Pending"
        SUCCEEDED = "Succeeded"
        UNKNOWN = "Unknown"


    class azure.mgmt.billingbenefits.models.CreditsValidateModel(BenefitValidateModel, discriminator='Credits'):
        benefit_type: Literal[BenefitType.CREDITS]
        properties: Optional[Credit]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[Credit] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billingbenefits.models.CustomPriceProperties(_Model):
        billing_period: Optional[str]
        catalog_claims: list[CatalogClaimsItem]
        catalog_id: str
        market_set_prices: list[MarketSetPricesItems]
        meter_type: Optional[str]
        rule_type: Union[str, DiscountRuleType]
        term_units: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                billing_period: Optional[str] = ..., 
                catalog_claims: list[CatalogClaimsItem], 
                catalog_id: str, 
                market_set_prices: list[MarketSetPricesItems], 
                meter_type: Optional[str] = ..., 
                rule_type: Union[str, DiscountRuleType], 
                term_units: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billingbenefits.models.Discount(TrackedResource):
        etag: Optional[str]
        id: str
        identity: Optional[ServiceManagedIdentity]
        kind: Optional[str]
        location: str
        managed_by: Optional[str]
        name: str
        plan: Optional[Plan]
        properties: Optional[DiscountProperties]
        sku: Optional[Sku]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ServiceManagedIdentity] = ..., 
                kind: Optional[str] = ..., 
                location: str, 
                managed_by: Optional[str] = ..., 
                plan: Optional[Plan] = ..., 
                properties: Optional[DiscountProperties] = ..., 
                sku: Optional[Sku] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billingbenefits.models.DiscountAppliedScopeType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BILLING_ACCOUNT = "BillingAccount"
        BILLING_PROFILE = "BillingProfile"
        CUSTOMER = "Customer"


    class azure.mgmt.billingbenefits.models.DiscountCombinationRule(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BEST_OF = "BestOf"
        STACKABLE = "Stackable"


    class azure.mgmt.billingbenefits.models.DiscountEntityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AFFILIATE = "Affiliate"
        PRIMARY = "Primary"


    class azure.mgmt.billingbenefits.models.DiscountPatchRequest(_Model):
        properties: Optional[DiscountPatchRequestProperties]
        tags: Optional[dict[str, str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[DiscountPatchRequestProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.billingbenefits.models.DiscountPatchRequestProperties(_Model):
        display_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                display_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billingbenefits.models.DiscountProperties(_Model):
        applied_scope_type: Optional[Union[str, DiscountAppliedScopeType]]
        benefit_resource_id: Optional[str]
        billing_account_resource_id: Optional[str]
        billing_profile_resource_id: Optional[str]
        customer_resource_id: Optional[str]
        display_name: Optional[str]
        entity_type: str
        product_code: str
        provisioning_state: Optional[Union[str, DiscountProvisioningState]]
        start_at: datetime
        status: Optional[Union[str, DiscountStatus]]
        system_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                applied_scope_type: Optional[Union[str, DiscountAppliedScopeType]] = ..., 
                display_name: Optional[str] = ..., 
                entity_type: str, 
                product_code: str, 
                start_at: datetime, 
                system_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billingbenefits.models.DiscountProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        FAILED = "Failed"
        PENDING = "Pending"
        SUCCEEDED = "Succeeded"
        UNKNOWN = "Unknown"


    class azure.mgmt.billingbenefits.models.DiscountRuleType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FIXED_LIST_PRICE = "FixedListPrice"
        FIXED_PRICE_LOCK = "FixedPriceLock"
        PRICE_CEILING = "PriceCeiling"


    class azure.mgmt.billingbenefits.models.DiscountStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        CANCELED = "Canceled"
        EXPIRED = "Expired"
        FAILED = "Failed"
        PENDING = "Pending"


    class azure.mgmt.billingbenefits.models.DiscountType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CUSTOM_PRICE = "CustomPrice"
        CUSTOM_PRICE_MULTI_CURRENCY = "CustomPriceMultiCurrency"
        PRODUCT = "Product"
        PRODUCT_FAMILY = "ProductFamily"
        SKU = "Sku"


    class azure.mgmt.billingbenefits.models.DiscountTypeCustomPrice(DiscountTypeProperties, discriminator='CustomPrice'):
        apply_discount_on: Union[str, ApplyDiscountOn]
        conditions: list[ConditionsItem]
        custom_price_properties: Optional[CustomPriceProperties]
        discount_combination_rule: Union[str, DiscountCombinationRule]
        discount_percentage: float
        discount_type: Literal[DiscountType.CUSTOM_PRICE]
        price_guarantee_properties: PriceGuaranteeProperties
        product_family_name: Optional[str]
        product_id: Optional[str]
        sku_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                apply_discount_on: Union[str, ApplyDiscountOn], 
                conditions: Optional[list[ConditionsItem]] = ..., 
                custom_price_properties: Optional[CustomPriceProperties] = ..., 
                discount_combination_rule: Optional[Union[str, DiscountCombinationRule]] = ..., 
                discount_percentage: Optional[float] = ..., 
                price_guarantee_properties: Optional[PriceGuaranteeProperties] = ..., 
                product_family_name: Optional[str] = ..., 
                product_id: Optional[str] = ..., 
                sku_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billingbenefits.models.DiscountTypeCustomPriceMultiCurrency(DiscountTypeCustomPrice, discriminator='CustomPriceMultiCurrency'):
        apply_discount_on: Union[str, ApplyDiscountOn]
        conditions: list[ConditionsItem]
        custom_price_properties: CustomPriceProperties
        discount_combination_rule: Union[str, DiscountCombinationRule]
        discount_percentage: float
        discount_type: Literal[DiscountType.CUSTOM_PRICE_MULTI_CURRENCY]
        price_guarantee_properties: PriceGuaranteeProperties
        product_family_name: str
        product_id: str
        sku_id: str

        @overload
        def __init__(
                self, 
                *, 
                apply_discount_on: Union[str, ApplyDiscountOn], 
                conditions: Optional[list[ConditionsItem]] = ..., 
                custom_price_properties: Optional[CustomPriceProperties] = ..., 
                discount_combination_rule: Optional[Union[str, DiscountCombinationRule]] = ..., 
                discount_percentage: Optional[float] = ..., 
                price_guarantee_properties: Optional[PriceGuaranteeProperties] = ..., 
                product_family_name: Optional[str] = ..., 
                product_id: Optional[str] = ..., 
                sku_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billingbenefits.models.DiscountTypeProduct(DiscountTypeProperties, discriminator='Product'):
        apply_discount_on: Union[str, ApplyDiscountOn]
        conditions: list[ConditionsItem]
        discount_combination_rule: Union[str, DiscountCombinationRule]
        discount_percentage: float
        discount_type: Literal[DiscountType.PRODUCT]
        price_guarantee_properties: PriceGuaranteeProperties
        product_family_name: Optional[str]
        product_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                apply_discount_on: Union[str, ApplyDiscountOn], 
                conditions: Optional[list[ConditionsItem]] = ..., 
                discount_combination_rule: Optional[Union[str, DiscountCombinationRule]] = ..., 
                discount_percentage: Optional[float] = ..., 
                price_guarantee_properties: Optional[PriceGuaranteeProperties] = ..., 
                product_family_name: Optional[str] = ..., 
                product_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billingbenefits.models.DiscountTypeProductFamily(DiscountTypeProperties, discriminator='ProductFamily'):
        apply_discount_on: Union[str, ApplyDiscountOn]
        conditions: list[ConditionsItem]
        discount_combination_rule: Union[str, DiscountCombinationRule]
        discount_percentage: float
        discount_type: Literal[DiscountType.PRODUCT_FAMILY]
        price_guarantee_properties: PriceGuaranteeProperties
        product_family_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                apply_discount_on: Union[str, ApplyDiscountOn], 
                conditions: Optional[list[ConditionsItem]] = ..., 
                discount_combination_rule: Optional[Union[str, DiscountCombinationRule]] = ..., 
                discount_percentage: Optional[float] = ..., 
                price_guarantee_properties: Optional[PriceGuaranteeProperties] = ..., 
                product_family_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billingbenefits.models.DiscountTypeProductSku(DiscountTypeProperties, discriminator='Sku'):
        apply_discount_on: Union[str, ApplyDiscountOn]
        conditions: list[ConditionsItem]
        discount_combination_rule: Union[str, DiscountCombinationRule]
        discount_percentage: float
        discount_type: Literal[DiscountType.SKU]
        price_guarantee_properties: PriceGuaranteeProperties
        product_family_name: Optional[str]
        product_id: Optional[str]
        sku_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                apply_discount_on: Union[str, ApplyDiscountOn], 
                conditions: Optional[list[ConditionsItem]] = ..., 
                discount_combination_rule: Optional[Union[str, DiscountCombinationRule]] = ..., 
                discount_percentage: Optional[float] = ..., 
                price_guarantee_properties: Optional[PriceGuaranteeProperties] = ..., 
                product_family_name: Optional[str] = ..., 
                product_id: Optional[str] = ..., 
                sku_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billingbenefits.models.DiscountTypeProperties(_Model):
        apply_discount_on: Union[str, ApplyDiscountOn]
        conditions: Optional[list[ConditionsItem]]
        discount_combination_rule: Optional[Union[str, DiscountCombinationRule]]
        discount_percentage: Optional[float]
        discount_type: str
        price_guarantee_properties: Optional[PriceGuaranteeProperties]

        @overload
        def __init__(
                self, 
                *, 
                apply_discount_on: Union[str, ApplyDiscountOn], 
                conditions: Optional[list[ConditionsItem]] = ..., 
                discount_combination_rule: Optional[Union[str, DiscountCombinationRule]] = ..., 
                discount_percentage: Optional[float] = ..., 
                discount_type: str, 
                price_guarantee_properties: Optional[PriceGuaranteeProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billingbenefits.models.EnablementMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"
        UNKNOWN = "Unknown"


    class azure.mgmt.billingbenefits.models.EntityTypeAffiliateDiscount(DiscountProperties, discriminator='Affiliate'):
        applied_scope_type: Union[str, DiscountAppliedScopeType]
        benefit_resource_id: str
        billing_account_resource_id: str
        billing_profile_resource_id: str
        customer_resource_id: str
        display_name: str
        end_at: Optional[datetime]
        entity_type: Literal[DiscountEntityType.AFFILIATE]
        primary_resource_id: Optional[str]
        product_code: str
        provisioning_state: Union[str, DiscountProvisioningState]
        start_at: datetime
        status: Union[str, DiscountStatus]
        system_id: str

        @overload
        def __init__(
                self, 
                *, 
                applied_scope_type: Optional[Union[str, DiscountAppliedScopeType]] = ..., 
                display_name: Optional[str] = ..., 
                product_code: str, 
                start_at: datetime, 
                system_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billingbenefits.models.EntityTypePrimaryDiscount(DiscountProperties, discriminator='Primary'):
        applied_scope_type: Union[str, DiscountAppliedScopeType]
        benefit_resource_id: str
        billing_account_resource_id: str
        billing_profile_resource_id: str
        customer_resource_id: str
        discount_type_properties: Optional[DiscountTypeProperties]
        display_name: str
        end_at: datetime
        entity_type: Literal[DiscountEntityType.PRIMARY]
        product_code: str
        provisioning_state: Union[str, DiscountProvisioningState]
        start_at: datetime
        status: Union[str, DiscountStatus]
        system_id: str

        @overload
        def __init__(
                self, 
                *, 
                applied_scope_type: Optional[Union[str, DiscountAppliedScopeType]] = ..., 
                discount_type_properties: Optional[DiscountTypeProperties] = ..., 
                display_name: Optional[str] = ..., 
                end_at: datetime, 
                product_code: str, 
                start_at: datetime, 
                system_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billingbenefits.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.billingbenefits.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.billingbenefits.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billingbenefits.models.ExtendedStatusInfo(_Model):
        message: Optional[str]
        status_code: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                message: Optional[str] = ..., 
                status_code: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billingbenefits.models.FreeServices(TrackedResource):
        etag: Optional[str]
        id: str
        identity: Optional[ManagedServiceIdentity]
        kind: Optional[str]
        location: str
        managed_by: Optional[str]
        name: str
        plan: Optional[Plan]
        properties: Optional[FreeServicesProperties]
        sku: Optional[Sku]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                kind: Optional[str] = ..., 
                location: str, 
                managed_by: Optional[str] = ..., 
                plan: Optional[Plan] = ..., 
                properties: Optional[FreeServicesProperties] = ..., 
                sku: Optional[Sku] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.billingbenefits.models.FreeServicesPatchRequest(_Model):
        properties: Optional[FreeServicesPatchRequestProperties]
        tags: Optional[dict[str, str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[FreeServicesPatchRequestProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.billingbenefits.models.FreeServicesPatchRequestProperties(_Model):
        end_at: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                end_at: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billingbenefits.models.FreeServicesProperties(_Model):
        billing_account_resource_id: Optional[str]
        billing_profile_resource_id: Optional[str]
        customer_resource_id: Optional[str]
        end_at: Optional[datetime]
        product_code: Optional[str]
        provisioning_state: Optional[str]
        start_at: Optional[datetime]
        status: Optional[Union[str, FreeServicesStatus]]
        system_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                end_at: Optional[datetime] = ..., 
                product_code: Optional[str] = ..., 
                start_at: Optional[datetime] = ..., 
                status: Optional[Union[str, FreeServicesStatus]] = ..., 
                system_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billingbenefits.models.FreeServicesStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        CANCELED = "Canceled"
        COMPLETED = "Completed"
        PENDING = "Pending"
        UNKNOWN = "Unknown"


    class azure.mgmt.billingbenefits.models.InstanceFlexibility(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        OFF = "Off"
        ON = "On"


    class azure.mgmt.billingbenefits.models.Macc(TrackedResource):
        etag: Optional[str]
        id: str
        identity: Optional[ManagedServiceIdentity]
        kind: Optional[str]
        location: str
        managed_by: Optional[str]
        name: str
        plan: Optional[Plan]
        properties: Optional[MaccModelProperties]
        sku: Optional[Sku]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                kind: Optional[str] = ..., 
                location: str, 
                managed_by: Optional[str] = ..., 
                plan: Optional[Plan] = ..., 
                properties: Optional[MaccModelProperties] = ..., 
                sku: Optional[Sku] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.billingbenefits.models.MaccEntityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONTRIBUTOR = "Contributor"
        PRIMARY = "Primary"


    class azure.mgmt.billingbenefits.models.MaccMilestone(_Model):
        automatic_shortfall: Optional[Union[str, EnablementMode]]
        automatic_shortfall_suppress_reason: Optional[AutomaticShortfallSuppressReason]
        commitment: Optional[Price]
        end_at: Optional[datetime]
        milestone_id: Optional[str]
        shortfall: Optional[Shortfall]
        status: Optional[Union[str, MaccMilestoneStatus]]

        @overload
        def __init__(
                self, 
                *, 
                automatic_shortfall: Optional[Union[str, EnablementMode]] = ..., 
                automatic_shortfall_suppress_reason: Optional[AutomaticShortfallSuppressReason] = ..., 
                commitment: Optional[Price] = ..., 
                end_at: Optional[datetime] = ..., 
                milestone_id: Optional[str] = ..., 
                shortfall: Optional[Shortfall] = ..., 
                status: Optional[Union[str, MaccMilestoneStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billingbenefits.models.MaccMilestoneStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        CANCELED = "Canceled"
        COMPLETED = "Completed"
        FAILED = "Failed"
        PENDING = "Pending"
        PENDING_SETTLEMENT = "PendingSettlement"
        REMOVED = "Removed"
        SCHEDULED = "Scheduled"
        SHORTFALL_CHARGED = "ShortfallCharged"
        SHORTFALL_WAIVED = "ShortfallWaived"
        UNKNOWN = "Unknown"


    class azure.mgmt.billingbenefits.models.MaccModelProperties(_Model):
        allow_contributors: Optional[bool]
        automatic_shortfall: Optional[Union[str, EnablementMode]]
        automatic_shortfall_suppress_reason: Optional[AutomaticShortfallSuppressReason]
        billing_account_resource_id: Optional[str]
        commitment: Optional[Commitment]
        display_name: Optional[str]
        end_at: Optional[datetime]
        entity_type: Union[str, MaccEntityType]
        milestones: Optional[list[MaccMilestone]]
        primary_billing_account_resource_id: Optional[str]
        primary_resource_id: Optional[str]
        product_code: Optional[str]
        provisioning_state: Optional[str]
        resource_id: Optional[str]
        shortfall: Optional[Shortfall]
        start_at: Optional[datetime]
        status: Optional[Union[str, MaccStatus]]
        system_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                allow_contributors: Optional[bool] = ..., 
                automatic_shortfall: Optional[Union[str, EnablementMode]] = ..., 
                automatic_shortfall_suppress_reason: Optional[AutomaticShortfallSuppressReason] = ..., 
                billing_account_resource_id: Optional[str] = ..., 
                commitment: Optional[Commitment] = ..., 
                display_name: Optional[str] = ..., 
                end_at: Optional[datetime] = ..., 
                entity_type: Union[str, MaccEntityType], 
                milestones: Optional[list[MaccMilestone]] = ..., 
                primary_billing_account_resource_id: Optional[str] = ..., 
                primary_resource_id: Optional[str] = ..., 
                product_code: Optional[str] = ..., 
                resource_id: Optional[str] = ..., 
                shortfall: Optional[Shortfall] = ..., 
                start_at: Optional[datetime] = ..., 
                status: Optional[Union[str, MaccStatus]] = ..., 
                system_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billingbenefits.models.MaccPatchRequest(_Model):
        properties: Optional[MaccPatchRequestProperties]
        tags: Optional[dict[str, str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[MaccPatchRequestProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.billingbenefits.models.MaccPatchRequestProperties(_Model):
        allow_contributors: Optional[bool]
        automatic_shortfall: Optional[Union[str, EnablementMode]]
        automatic_shortfall_suppress_reason: Optional[AutomaticShortfallSuppressReason]
        commitment: Optional[Commitment]
        display_name: Optional[str]
        end_at: Optional[datetime]
        milestones: Optional[list[MaccMilestone]]
        primary_billing_account_resource_id: Optional[str]
        primary_resource_id: Optional[str]
        status: Optional[Union[str, MaccMilestoneStatus]]

        @overload
        def __init__(
                self, 
                *, 
                allow_contributors: Optional[bool] = ..., 
                automatic_shortfall: Optional[Union[str, EnablementMode]] = ..., 
                automatic_shortfall_suppress_reason: Optional[AutomaticShortfallSuppressReason] = ..., 
                commitment: Optional[Commitment] = ..., 
                display_name: Optional[str] = ..., 
                end_at: Optional[datetime] = ..., 
                milestones: Optional[list[MaccMilestone]] = ..., 
                primary_billing_account_resource_id: Optional[str] = ..., 
                primary_resource_id: Optional[str] = ..., 
                status: Optional[Union[str, MaccMilestoneStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billingbenefits.models.MaccStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        CANCELED = "Canceled"
        COMPLETED = "Completed"
        FAILED = "Failed"
        PENDING = "Pending"
        PENDING_SETTLEMENT = "PendingSettlement"
        SCHEDULED = "Scheduled"
        SHORTFALL_CHARGED = "ShortfallCharged"
        SHORTFALL_WAIVED = "ShortfallWaived"
        STOPPED = "Stopped"
        UNKNOWN = "Unknown"


    class azure.mgmt.billingbenefits.models.MaccValidateModel(BenefitValidateModel, discriminator='MACC'):
        benefit_type: Literal[BenefitType.MACC]
        properties: Optional[MaccModelProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[MaccModelProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.billingbenefits.models.ManagedServiceIdentity(_Model):
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


    class azure.mgmt.billingbenefits.models.ManagedServiceIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        SYSTEM_ASSIGNED_USER_ASSIGNED = "SystemAssigned,UserAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.billingbenefits.models.MarketSetPricesItems(_Model):
        currency: str
        markets: list[str]
        value: float

        @overload
        def __init__(
                self, 
                *, 
                currency: str, 
                markets: list[str], 
                value: float
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billingbenefits.models.MilestoneStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        CANCELED = "Canceled"
        COMPLETED = "Completed"
        FAILED = "Failed"
        MISSED = "Missed"
        PENDING = "Pending"
        PENDING_SETTLEMENT = "PendingSettlement"
        REMOVED = "Removed"
        SCHEDULED = "Scheduled"
        UNKNOWN = "Unknown"


    class azure.mgmt.billingbenefits.models.Operation(_Model):
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


    class azure.mgmt.billingbenefits.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.billingbenefits.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.billingbenefits.models.PaymentDetail(_Model):
        billing_account: Optional[str]
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
                billing_account: Optional[str] = ..., 
                billing_currency_total: Optional[Price] = ..., 
                due_date: Optional[date] = ..., 
                payment_date: Optional[date] = ..., 
                pricing_currency_total: Optional[Price] = ..., 
                status: Optional[Union[str, PaymentStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billingbenefits.models.PaymentStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELLED = "Cancelled"
        FAILED = "Failed"
        SCHEDULED = "Scheduled"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.billingbenefits.models.Plan(_Model):
        name: str
        product: str
        promotion_code: Optional[str]
        publisher: str
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                product: str, 
                promotion_code: Optional[str] = ..., 
                publisher: str, 
                version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billingbenefits.models.Price(_Model):
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


    class azure.mgmt.billingbenefits.models.PriceGuaranteeProperties(_Model):
        price_guarantee_date: Optional[datetime]
        pricing_policy: Optional[Union[str, PricingPolicy]]

        @overload
        def __init__(
                self, 
                *, 
                price_guarantee_date: Optional[datetime] = ..., 
                pricing_policy: Optional[Union[str, PricingPolicy]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billingbenefits.models.PricingPolicy(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LOCKED = "Locked"
        PROTECTED = "Protected"


    class azure.mgmt.billingbenefits.models.PrimaryConditionalCreditProperties(ConditionalCreditProperties, discriminator='Primary'):
        allow_contributors: Optional[Union[str, EnablementMode]]
        benefit_resource_id: str
        billing_account_resource_id: str
        display_name: str
        end_at: datetime
        entity_type: Literal[ConditionalCreditEntityType.PRIMARY]
        milestones: Optional[list[ConditionalCreditMilestone]]
        product_code: str
        provisioning_state: Union[str, ConditionalCreditsProvisioningState]
        resource_id: str
        start_at: datetime
        status: Union[str, ConditionalCreditStatus]
        system_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                allow_contributors: Optional[Union[str, EnablementMode]] = ..., 
                billing_account_resource_id: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                end_at: Optional[datetime] = ..., 
                milestones: Optional[list[ConditionalCreditMilestone]] = ..., 
                product_code: Optional[str] = ..., 
                resource_id: Optional[str] = ..., 
                start_at: Optional[datetime] = ..., 
                status: Optional[Union[str, ConditionalCreditStatus]] = ..., 
                system_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billingbenefits.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELLED = "Cancelled"
        CONFIRMED_BILLING = "ConfirmedBilling"
        CREATED = "Created"
        CREATING = "Creating"
        EXPIRED = "Expired"
        FAILED = "Failed"
        PENDING_BILLING = "PendingBilling"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.billingbenefits.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.billingbenefits.models.PurchaseRequest(_Model):
        properties: Optional[PurchaseRequestProperties]
        sku: Optional[ResourceSku]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[PurchaseRequestProperties] = ..., 
                sku: Optional[ResourceSku] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.billingbenefits.models.PurchaseRequestProperties(_Model):
        applied_scope_properties: Optional[AppliedScopeProperties]
        applied_scope_type: Optional[Union[str, AppliedScopeType]]
        billing_plan: Optional[Union[str, BillingPlan]]
        billing_scope_id: Optional[str]
        commitment: Optional[Commitment]
        display_name: Optional[str]
        effective_date_time: Optional[datetime]
        renew: Optional[bool]
        term: Optional[Union[str, Term]]

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
                term: Optional[Union[str, Term]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billingbenefits.models.RenewProperties(_Model):
        purchase_properties: Optional[PurchaseRequest]

        @overload
        def __init__(
                self, 
                *, 
                purchase_properties: Optional[PurchaseRequest] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billingbenefits.models.ReservationOrderAliasRequest(Resource):
        id: str
        location: Optional[str]
        name: str
        properties: Optional[ReservationOrderAliasRequestProperties]
        sku: ResourceSku
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                properties: Optional[ReservationOrderAliasRequestProperties] = ..., 
                sku: ResourceSku
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.billingbenefits.models.ReservationOrderAliasRequestProperties(_Model):
        applied_scope_properties: Optional[AppliedScopeProperties]
        applied_scope_type: Optional[Union[str, AppliedScopeType]]
        billing_plan: Optional[Union[str, BillingPlan]]
        billing_scope_id: Optional[str]
        display_name: Optional[str]
        quantity: Optional[int]
        renew: Optional[bool]
        reserved_resource_properties: Optional[ReservationOrderAliasRequestPropertiesReservedResourceProperties]
        reserved_resource_type: Optional[Union[str, ReservedResourceType]]
        review_date_time: Optional[datetime]
        term: Optional[Union[str, Term]]

        @overload
        def __init__(
                self, 
                *, 
                applied_scope_properties: Optional[AppliedScopeProperties] = ..., 
                applied_scope_type: Optional[Union[str, AppliedScopeType]] = ..., 
                billing_plan: Optional[Union[str, BillingPlan]] = ..., 
                billing_scope_id: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                quantity: Optional[int] = ..., 
                renew: Optional[bool] = ..., 
                reserved_resource_properties: Optional[ReservationOrderAliasRequestPropertiesReservedResourceProperties] = ..., 
                reserved_resource_type: Optional[Union[str, ReservedResourceType]] = ..., 
                review_date_time: Optional[datetime] = ..., 
                term: Optional[Union[str, Term]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billingbenefits.models.ReservationOrderAliasRequestPropertiesReservedResourceProperties(_Model):
        instance_flexibility: Optional[Union[str, InstanceFlexibility]]

        @overload
        def __init__(
                self, 
                *, 
                instance_flexibility: Optional[Union[str, InstanceFlexibility]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billingbenefits.models.ReservationOrderAliasResponse(ProxyResource):
        id: str
        location: Optional[str]
        name: str
        properties: Optional[ReservationOrderAliasResponseProperties]
        sku: ResourceSku
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                properties: Optional[ReservationOrderAliasResponseProperties] = ..., 
                sku: ResourceSku
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.billingbenefits.models.ReservationOrderAliasResponseProperties(_Model):
        applied_scope_properties: Optional[AppliedScopeProperties]
        applied_scope_type: Optional[Union[str, AppliedScopeType]]
        billing_plan: Optional[Union[str, BillingPlan]]
        billing_scope_id: Optional[str]
        display_name: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        quantity: Optional[int]
        renew: Optional[bool]
        reservation_order_id: Optional[str]
        reserved_resource_properties: Optional[ReservationOrderAliasResponsePropertiesReservedResourceProperties]
        reserved_resource_type: Optional[Union[str, ReservedResourceType]]
        review_date_time: Optional[datetime]
        term: Optional[Union[str, Term]]

        @overload
        def __init__(
                self, 
                *, 
                applied_scope_properties: Optional[AppliedScopeProperties] = ..., 
                applied_scope_type: Optional[Union[str, AppliedScopeType]] = ..., 
                billing_plan: Optional[Union[str, BillingPlan]] = ..., 
                billing_scope_id: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                quantity: Optional[int] = ..., 
                renew: Optional[bool] = ..., 
                reserved_resource_properties: Optional[ReservationOrderAliasResponsePropertiesReservedResourceProperties] = ..., 
                reserved_resource_type: Optional[Union[str, ReservedResourceType]] = ..., 
                review_date_time: Optional[datetime] = ..., 
                term: Optional[Union[str, Term]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billingbenefits.models.ReservationOrderAliasResponsePropertiesReservedResourceProperties(_Model):
        instance_flexibility: Optional[Union[str, InstanceFlexibility]]

        @overload
        def __init__(
                self, 
                *, 
                instance_flexibility: Optional[Union[str, InstanceFlexibility]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billingbenefits.models.ReservedResourceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APP_SERVICE = "AppService"
        AVS = "AVS"
        AZURE_DATA_EXPLORER = "AzureDataExplorer"
        AZURE_FILES = "AzureFiles"
        BLOCK_BLOB = "BlockBlob"
        COSMOS_DB = "CosmosDb"
        DATABRICKS = "Databricks"
        DATA_FACTORY = "DataFactory"
        DEDICATED_HOST = "DedicatedHost"
        MANAGED_DISK = "ManagedDisk"
        MARIA_DB = "MariaDb"
        MY_SQL = "MySql"
        NET_APP_STORAGE = "NetAppStorage"
        POSTGRE_SQL = "PostgreSql"
        REDIS_CACHE = "RedisCache"
        RED_HAT = "RedHat"
        RED_HAT_OSA = "RedHatOsa"
        SAP_HANA = "SapHana"
        SQL_AZURE_HYBRID_BENEFIT = "SqlAzureHybridBenefit"
        SQL_DATABASES = "SqlDatabases"
        SQL_DATA_WAREHOUSE = "SqlDataWarehouse"
        SQL_EDGE = "SqlEdge"
        SUSE_LINUX = "SuseLinux"
        VIRTUAL_MACHINES = "VirtualMachines"
        VIRTUAL_MACHINE_SOFTWARE = "VirtualMachineSoftware"
        V_MWARE_CLOUD_SIMPLE = "VMwareCloudSimple"


    class azure.mgmt.billingbenefits.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.billingbenefits.models.ResourceSku(_Model):
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billingbenefits.models.RoleAssignmentEntity(_Model):
        id: Optional[str]
        name: Optional[str]
        properties: Optional[RoleAssignmentEntityProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                properties: Optional[RoleAssignmentEntityProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.billingbenefits.models.RoleAssignmentEntityProperties(_Model):
        principal_id: Optional[str]
        role_definition_id: Optional[str]
        scope: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                principal_id: Optional[str] = ..., 
                role_definition_id: Optional[str] = ..., 
                scope: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billingbenefits.models.SavingsPlanModel(ProxyResource):
        id: str
        name: str
        properties: Optional[SavingsPlanModelProperties]
        sku: ResourceSku
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SavingsPlanModelProperties] = ..., 
                sku: ResourceSku
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.billingbenefits.models.SavingsPlanModelProperties(_Model):
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
        provisioning_state: Optional[Union[str, ProvisioningState]]
        purchase_date_time: Optional[datetime]
        renew: Optional[bool]
        renew_destination: Optional[str]
        renew_properties: Optional[RenewProperties]
        renew_source: Optional[str]
        term: Optional[Union[str, Term]]
        user_friendly_applied_scope_type: Optional[str]
        utilization: Optional[Utilization]

        @overload
        def __init__(
                self, 
                *, 
                applied_scope_properties: Optional[AppliedScopeProperties] = ..., 
                applied_scope_type: Optional[Union[str, AppliedScopeType]] = ..., 
                benefit_start_time: Optional[datetime] = ..., 
                billing_plan: Optional[Union[str, BillingPlan]] = ..., 
                billing_scope_id: Optional[str] = ..., 
                commitment: Optional[Commitment] = ..., 
                display_name: Optional[str] = ..., 
                renew: Optional[bool] = ..., 
                renew_destination: Optional[str] = ..., 
                renew_properties: Optional[RenewProperties] = ..., 
                renew_source: Optional[str] = ..., 
                term: Optional[Union[str, Term]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billingbenefits.models.SavingsPlanOrderAliasModel(ProxyResource):
        id: str
        kind: Optional[str]
        name: str
        properties: Optional[SavingsPlanOrderAliasProperties]
        sku: ResourceSku
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                kind: Optional[str] = ..., 
                properties: Optional[SavingsPlanOrderAliasProperties] = ..., 
                sku: ResourceSku
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.billingbenefits.models.SavingsPlanOrderAliasProperties(_Model):
        applied_scope_properties: Optional[AppliedScopeProperties]
        applied_scope_type: Optional[Union[str, AppliedScopeType]]
        billing_plan: Optional[Union[str, BillingPlan]]
        billing_scope_id: Optional[str]
        commitment: Optional[Commitment]
        display_name: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        renew: Optional[bool]
        savings_plan_order_id: Optional[str]
        term: Optional[Union[str, Term]]

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
                term: Optional[Union[str, Term]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billingbenefits.models.SavingsPlanOrderModel(ProxyResource):
        id: str
        name: str
        properties: Optional[SavingsPlanOrderModelProperties]
        sku: ResourceSku
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SavingsPlanOrderModelProperties] = ..., 
                sku: ResourceSku
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.billingbenefits.models.SavingsPlanOrderModelProperties(_Model):
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
        provisioning_state: Optional[Union[str, ProvisioningState]]
        savings_plans: Optional[list[str]]
        term: Optional[Union[str, Term]]

        @overload
        def __init__(
                self, 
                *, 
                benefit_start_time: Optional[datetime] = ..., 
                billing_plan: Optional[Union[str, BillingPlan]] = ..., 
                billing_scope_id: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                plan_information: Optional[BillingPlanInformation] = ..., 
                savings_plans: Optional[list[str]] = ..., 
                term: Optional[Union[str, Term]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billingbenefits.models.SavingsPlanSummary(_Model):
        name: Optional[str]
        value: Optional[SavingsPlanSummaryCount]

        @overload
        def __init__(
                self, 
                *, 
                value: Optional[SavingsPlanSummaryCount] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billingbenefits.models.SavingsPlanSummaryCount(_Model):
        cancelled_count: Optional[float]
        expired_count: Optional[float]
        expiring_count: Optional[float]
        failed_count: Optional[float]
        no_benefit_count: Optional[float]
        pending_count: Optional[float]
        processing_count: Optional[float]
        succeeded_count: Optional[float]
        warning_count: Optional[float]


    class azure.mgmt.billingbenefits.models.SavingsPlanUpdateRequest(_Model):
        properties: Optional[SavingsPlanUpdateRequestProperties]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SavingsPlanUpdateRequestProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billingbenefits.models.SavingsPlanUpdateRequestProperties(_Model):
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


    class azure.mgmt.billingbenefits.models.SavingsPlanUpdateValidateRequest(_Model):
        benefits: Optional[list[SavingsPlanUpdateRequestProperties]]

        @overload
        def __init__(
                self, 
                *, 
                benefits: Optional[list[SavingsPlanUpdateRequestProperties]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billingbenefits.models.SavingsPlanValidResponseProperty(_Model):
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


    class azure.mgmt.billingbenefits.models.SavingsPlanValidateModel(BenefitValidateModel, discriminator='SavingsPlan'):
        benefit_type: Literal[BenefitType.SAVINGS_PLAN]
        id: Optional[str]
        kind: Optional[str]
        name: Optional[str]
        properties: Optional[SavingsPlanOrderAliasProperties]
        sku: ResourceSku
        system_data: Optional[SystemData]
        type: Optional[str]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                kind: Optional[str] = ..., 
                properties: Optional[SavingsPlanOrderAliasProperties] = ..., 
                sku: ResourceSku
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.billingbenefits.models.SavingsPlanValidateResponse(_Model):
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


    class azure.mgmt.billingbenefits.models.SellerResourceListRequest(_Model):
        properties: Optional[SellerResourceListRequestProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SellerResourceListRequestProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.billingbenefits.models.SellerResourceListRequestProperties(_Model):
        billing_account_resource_id: str
        contributors: Optional[bool]
        filter: Optional[str]
        milestones: Optional[bool]
        primary_resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                billing_account_resource_id: str, 
                contributors: Optional[bool] = ..., 
                filter: Optional[str] = ..., 
                milestones: Optional[bool] = ..., 
                primary_resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billingbenefits.models.ServiceManagedIdentity(_Model):
        principal_id: Optional[str]
        tenant_id: Optional[str]
        type: Union[str, ServiceManagedIdentityType]
        user_assigned_identities: Optional[dict[str, UserAssignedIdentity]]

        @overload
        def __init__(
                self, 
                *, 
                type: Union[str, ServiceManagedIdentityType], 
                user_assigned_identities: Optional[dict[str, UserAssignedIdentity]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billingbenefits.models.ServiceManagedIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        SYSTEM_ASSIGNED_USER_ASSIGNED = "SystemAssigned,UserAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.billingbenefits.models.Shortfall(_Model):
        balance_version: Optional[float]
        charge: Optional[Commitment]
        end_at: Optional[datetime]
        product_code: Optional[str]
        resource_id: Optional[str]
        start_at: Optional[datetime]
        system_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                balance_version: Optional[float] = ..., 
                charge: Optional[Commitment] = ..., 
                end_at: Optional[datetime] = ..., 
                product_code: Optional[str] = ..., 
                resource_id: Optional[str] = ..., 
                start_at: Optional[datetime] = ..., 
                system_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billingbenefits.models.Sku(_Model):
        capacity: Optional[int]
        family: Optional[str]
        name: str
        size: Optional[str]
        tier: Optional[Union[str, SkuTier]]

        @overload
        def __init__(
                self, 
                *, 
                capacity: Optional[int] = ..., 
                family: Optional[str] = ..., 
                name: str, 
                size: Optional[str] = ..., 
                tier: Optional[Union[str, SkuTier]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.billingbenefits.models.SkuTier(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BASIC = "Basic"
        FREE = "Free"
        PREMIUM = "Premium"
        STANDARD = "Standard"


    class azure.mgmt.billingbenefits.models.SystemData(_Model):
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


    class azure.mgmt.billingbenefits.models.Term(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        P1M = "P1M"
        P1_Y = "P1Y"
        P3_Y = "P3Y"
        P5_Y = "P5Y"


    class azure.mgmt.billingbenefits.models.TrackedResource(Resource):
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


    class azure.mgmt.billingbenefits.models.UserAssignedIdentity(_Model):
        client_id: Optional[str]
        principal_id: Optional[str]


    class azure.mgmt.billingbenefits.models.Utilization(_Model):
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


    class azure.mgmt.billingbenefits.models.UtilizationAggregates(_Model):
        grain: Optional[float]
        grain_unit: Optional[str]
        value: Optional[float]
        value_unit: Optional[str]


namespace azure.mgmt.billingbenefits.operations

    class azure.mgmt.billingbenefits.operations.ApplicableMaccsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                billing_account_id: str, 
                **kwargs: Any
            ) -> ItemPaged[ApplicableMacc]: ...


    class azure.mgmt.billingbenefits.operations.BenefitOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def validate(
                self, 
                body: BenefitValidateRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> BenefitValidateResponse: ...

        @overload
        def validate(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> BenefitValidateResponse: ...

        @overload
        def validate(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> BenefitValidateResponse: ...


    class azure.mgmt.billingbenefits.operations.ConditionalCreditContributorsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get_from_primary(
                self, 
                resource_group_name: str, 
                conditional_credit_name: str, 
                contributor_name: str, 
                **kwargs: Any
            ) -> ConditionalCreditContributor: ...

        @distributed_trace
        def list_from_applicable_conditional_credit(
                self, 
                billing_account_id: str, 
                system_id: str, 
                **kwargs: Any
            ) -> ItemPaged[ConditionalCreditContributor]: ...

        @distributed_trace
        def list_from_primary(
                self, 
                resource_group_name: str, 
                conditional_credit_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ConditionalCreditContributor]: ...


    class azure.mgmt.billingbenefits.operations.ConditionalCreditsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_cancel(
                self, 
                resource_group_name: str, 
                conditional_credit_name: str, 
                **kwargs: Any
            ) -> LROPoller[ConditionalCredit]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                conditional_credit_name: str, 
                body: ConditionalCredit, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ConditionalCredit]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                conditional_credit_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ConditionalCredit]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                conditional_credit_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ConditionalCredit]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                conditional_credit_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                conditional_credit_name: str, 
                body: ConditionalCreditPatchRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ConditionalCredit]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                conditional_credit_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ConditionalCredit]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                conditional_credit_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ConditionalCredit]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                conditional_credit_name: str, 
                **kwargs: Any
            ) -> ConditionalCredit: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ConditionalCredit]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[ConditionalCredit]: ...

        @distributed_trace
        def scope_list(
                self, 
                scope: str, 
                **kwargs: Any
            ) -> ItemPaged[ConditionalCredit]: ...


    class azure.mgmt.billingbenefits.operations.ContributorsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get_from_primary(
                self, 
                resource_group_name: str, 
                macc_name: str, 
                contributor_name: str, 
                **kwargs: Any
            ) -> Contributor: ...

        @distributed_trace
        def list_from_applicable_macc(
                self, 
                billing_account_id: str, 
                system_id: str, 
                **kwargs: Any
            ) -> ItemPaged[Contributor]: ...

        @distributed_trace
        def list_from_primary(
                self, 
                resource_group_name: str, 
                macc_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Contributor]: ...


    class azure.mgmt.billingbenefits.operations.CreditsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_cancel(
                self, 
                resource_group_name: str, 
                credit_name: str, 
                **kwargs: Any
            ) -> LROPoller[Credit]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                credit_name: str, 
                body: Credit, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Credit]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                credit_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Credit]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                credit_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Credit]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                credit_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                credit_name: str, 
                body: CreditPatchRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Credit]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                credit_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Credit]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                credit_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Credit]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                credit_name: str, 
                **kwargs: Any
            ) -> Credit: ...

        @distributed_trace
        def list_applicable(
                self, 
                scope: str, 
                **kwargs: Any
            ) -> ItemPaged[Credit]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Credit]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[Credit]: ...


    class azure.mgmt.billingbenefits.operations.DiscountOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                discount_name: str, 
                body: DiscountPatchRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Discount]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                discount_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Discount]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                discount_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Discount]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                discount_name: str, 
                **kwargs: Any
            ) -> Discount: ...


    class azure.mgmt.billingbenefits.operations.DiscountsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_cancel(
                self, 
                resource_group_name: str, 
                discount_name: str, 
                **kwargs: Any
            ) -> LROPoller[Discount]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                discount_name: str, 
                body: Discount, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Discount]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                discount_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Discount]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                discount_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Discount]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                discount_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def resource_group_list(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Discount]: ...

        @distributed_trace
        def scope_list(
                self, 
                scope: str, 
                **kwargs: Any
            ) -> ItemPaged[Discount]: ...

        @distributed_trace
        def subscription_list(self, **kwargs: Any) -> ItemPaged[Discount]: ...


    class azure.mgmt.billingbenefits.operations.FreeServicesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                free_service_name: str, 
                body: FreeServices, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[FreeServices]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                free_service_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[FreeServices]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                free_service_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[FreeServices]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                free_service_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                free_service_name: str, 
                body: FreeServicesPatchRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[FreeServices]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                free_service_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[FreeServices]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                free_service_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[FreeServices]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                free_service_name: str, 
                **kwargs: Any
            ) -> FreeServices: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[FreeServices]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[FreeServices]: ...


    class azure.mgmt.billingbenefits.operations.MaccsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_cancel(
                self, 
                resource_group_name: str, 
                macc_name: str, 
                **kwargs: Any
            ) -> LROPoller[Macc]: ...

        @overload
        def begin_charge_shortfall(
                self, 
                resource_group_name: str, 
                macc_name: str, 
                body: ChargeShortfallRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Macc]: ...

        @overload
        def begin_charge_shortfall(
                self, 
                resource_group_name: str, 
                macc_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Macc]: ...

        @overload
        def begin_charge_shortfall(
                self, 
                resource_group_name: str, 
                macc_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Macc]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                macc_name: str, 
                body: Macc, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Macc]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                macc_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Macc]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                macc_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Macc]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                macc_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                macc_name: str, 
                body: MaccPatchRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Macc]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                macc_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Macc]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                macc_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Macc]: ...

        @distributed_trace
        def begin_write_off(
                self, 
                resource_group_name: str, 
                macc_name: str, 
                **kwargs: Any
            ) -> LROPoller[Macc]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                macc_name: str, 
                **kwargs: Any
            ) -> Macc: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Macc]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[Macc]: ...


    class azure.mgmt.billingbenefits.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


    class azure.mgmt.billingbenefits.operations.ReservationOrderAliasOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create(
                self, 
                reservation_order_alias_name: str, 
                body: ReservationOrderAliasRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ReservationOrderAliasResponse]: ...

        @overload
        def begin_create(
                self, 
                reservation_order_alias_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ReservationOrderAliasResponse]: ...

        @overload
        def begin_create(
                self, 
                reservation_order_alias_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ReservationOrderAliasResponse]: ...

        @distributed_trace
        def get(
                self, 
                reservation_order_alias_name: str, 
                **kwargs: Any
            ) -> ReservationOrderAliasResponse: ...


    class azure.mgmt.billingbenefits.operations.SavingsPlanOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_update(
                self, 
                savings_plan_order_id: str, 
                savings_plan_id: str, 
                body: SavingsPlanUpdateRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SavingsPlanModel]: ...

        @overload
        def begin_update(
                self, 
                savings_plan_order_id: str, 
                savings_plan_id: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SavingsPlanModel]: ...

        @overload
        def begin_update(
                self, 
                savings_plan_order_id: str, 
                savings_plan_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SavingsPlanModel]: ...

        @distributed_trace
        def get(
                self, 
                savings_plan_order_id: str, 
                savings_plan_id: str, 
                **kwargs: Any
            ) -> SavingsPlanModel: ...

        @distributed_trace
        def list(
                self, 
                savings_plan_order_id: str, 
                **kwargs: Any
            ) -> ItemPaged[SavingsPlanModel]: ...

        @distributed_trace
        def list_all(
                self, 
                *, 
                filter: Optional[str] = ..., 
                orderby: Optional[str] = ..., 
                refresh_summary: Optional[str] = ..., 
                selected_state: Optional[str] = ..., 
                skiptoken: Optional[float] = ..., 
                take: Optional[float] = ..., 
                **kwargs: Any
            ) -> ItemPaged[SavingsPlanModel]: ...

        @overload
        def validate_update(
                self, 
                savings_plan_order_id: str, 
                savings_plan_id: str, 
                body: SavingsPlanUpdateValidateRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SavingsPlanValidateResponse: ...

        @overload
        def validate_update(
                self, 
                savings_plan_order_id: str, 
                savings_plan_id: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SavingsPlanValidateResponse: ...

        @overload
        def validate_update(
                self, 
                savings_plan_order_id: str, 
                savings_plan_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SavingsPlanValidateResponse: ...


    class azure.mgmt.billingbenefits.operations.SavingsPlanOrderAliasOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create(
                self, 
                savings_plan_order_alias_name: str, 
                body: SavingsPlanOrderAliasModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SavingsPlanOrderAliasModel]: ...

        @overload
        def begin_create(
                self, 
                savings_plan_order_alias_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SavingsPlanOrderAliasModel]: ...

        @overload
        def begin_create(
                self, 
                savings_plan_order_alias_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SavingsPlanOrderAliasModel]: ...

        @distributed_trace
        def get(
                self, 
                savings_plan_order_alias_name: str, 
                **kwargs: Any
            ) -> SavingsPlanOrderAliasModel: ...


    class azure.mgmt.billingbenefits.operations.SavingsPlanOrderOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def elevate(
                self, 
                savings_plan_order_id: str, 
                **kwargs: Any
            ) -> RoleAssignmentEntity: ...

        @distributed_trace
        def get(
                self, 
                savings_plan_order_id: str, 
                **kwargs: Any
            ) -> SavingsPlanOrderModel: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[SavingsPlanOrderModel]: ...


    class azure.mgmt.billingbenefits.operations.SellerResourceOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def list(
                self, 
                body: SellerResourceListRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> List[Macc]: ...

        @overload
        def list(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> List[Macc]: ...

        @overload
        def list(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> List[Macc]: ...


    class azure.mgmt.billingbenefits.operations.SourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                credit_name: str, 
                source_name: str, 
                body: CreditSource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CreditSource: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                credit_name: str, 
                source_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CreditSource: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                credit_name: str, 
                source_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CreditSource: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                credit_name: str, 
                source_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                credit_name: str, 
                source_name: str, 
                **kwargs: Any
            ) -> CreditSource: ...

        @distributed_trace
        def list_by_credit(
                self, 
                resource_group_name: str, 
                credit_name: str, 
                **kwargs: Any
            ) -> ItemPaged[CreditSource]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                credit_name: str, 
                source_name: str, 
                body: CreditSourcePatchRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CreditSource: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                credit_name: str, 
                source_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CreditSource: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                credit_name: str, 
                source_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CreditSource: ...


```