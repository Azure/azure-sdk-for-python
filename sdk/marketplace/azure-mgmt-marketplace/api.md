```py
namespace azure.mgmt.marketplace

    class azure.mgmt.marketplace.MarketplaceMgmtClient(_MarketplaceMgmtClientOperationsMixin): implements ContextManager 
        operations: Operations
        private_store: PrivateStoreOperations
        private_store_collection: PrivateStoreCollectionOperations
        private_store_collection_offer: PrivateStoreCollectionOfferOperations

        def __init__(
                self, 
                credential: TokenCredential, 
                base_url: Optional[str] = None, 
                *, 
                api_version: str = ..., 
                cloud_setting: Optional[AzureClouds] = ..., 
                **kwargs: Any
            ) -> None: ...

        def close(self) -> None: ...

        @distributed_trace
        def query_rules(
                self, 
                private_store_id: str, 
                collection_id: str, 
                **kwargs: Any
            ) -> RuleListResponse: ...

        @overload
        def query_user_rules(
                self, 
                private_store_id: str, 
                payload: Optional[QueryUserRulesProperties] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RuleListResponse: ...

        @overload
        def query_user_rules(
                self, 
                private_store_id: str, 
                payload: Optional[QueryUserRulesProperties] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RuleListResponse: ...

        @overload
        def query_user_rules(
                self, 
                private_store_id: str, 
                payload: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RuleListResponse: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> HttpResponse: ...

        @overload
        def set_collection_rules(
                self, 
                private_store_id: str, 
                collection_id: str, 
                payload: Optional[SetRulesRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def set_collection_rules(
                self, 
                private_store_id: str, 
                collection_id: str, 
                payload: Optional[SetRulesRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def set_collection_rules(
                self, 
                private_store_id: str, 
                collection_id: str, 
                payload: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...


namespace azure.mgmt.marketplace.aio

    class azure.mgmt.marketplace.aio.MarketplaceMgmtClient(_MarketplaceMgmtClientOperationsMixin): implements AsyncContextManager 
        operations: Operations
        private_store: PrivateStoreOperations
        private_store_collection: PrivateStoreCollectionOperations
        private_store_collection_offer: PrivateStoreCollectionOfferOperations

        def __init__(
                self, 
                credential: AsyncTokenCredential, 
                base_url: Optional[str] = None, 
                *, 
                api_version: str = ..., 
                cloud_setting: Optional[AzureClouds] = ..., 
                **kwargs: Any
            ) -> None: ...

        async def close(self) -> None: ...

        @distributed_trace_async
        async def query_rules(
                self, 
                private_store_id: str, 
                collection_id: str, 
                **kwargs: Any
            ) -> RuleListResponse: ...

        @overload
        async def query_user_rules(
                self, 
                private_store_id: str, 
                payload: Optional[QueryUserRulesProperties] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RuleListResponse: ...

        @overload
        async def query_user_rules(
                self, 
                private_store_id: str, 
                payload: Optional[QueryUserRulesProperties] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RuleListResponse: ...

        @overload
        async def query_user_rules(
                self, 
                private_store_id: str, 
                payload: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RuleListResponse: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> Awaitable[AsyncHttpResponse]: ...

        @overload
        async def set_collection_rules(
                self, 
                private_store_id: str, 
                collection_id: str, 
                payload: Optional[SetRulesRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def set_collection_rules(
                self, 
                private_store_id: str, 
                collection_id: str, 
                payload: Optional[SetRulesRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def set_collection_rules(
                self, 
                private_store_id: str, 
                collection_id: str, 
                payload: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...


namespace azure.mgmt.marketplace.aio.operations

    class azure.mgmt.marketplace.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[SingleOperation]: ...


    class azure.mgmt.marketplace.aio.operations.PrivateStoreCollectionOfferOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def contexts_view(
                self, 
                private_store_id: str, 
                collection_id: str, 
                offer_id: str, 
                payload: Optional[CollectionOffersByAllContextsPayload] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Offer: ...

        @overload
        async def contexts_view(
                self, 
                private_store_id: str, 
                collection_id: str, 
                offer_id: str, 
                payload: Optional[CollectionOffersByAllContextsPayload] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Offer: ...

        @overload
        async def contexts_view(
                self, 
                private_store_id: str, 
                collection_id: str, 
                offer_id: str, 
                payload: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Offer: ...

        @overload
        async def create_or_update(
                self, 
                private_store_id: str, 
                collection_id: str, 
                offer_id: str, 
                payload: Offer, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Offer: ...

        @overload
        async def create_or_update(
                self, 
                private_store_id: str, 
                collection_id: str, 
                offer_id: str, 
                payload: Offer, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Offer: ...

        @overload
        async def create_or_update(
                self, 
                private_store_id: str, 
                collection_id: str, 
                offer_id: str, 
                payload: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Offer: ...

        @distributed_trace_async
        async def delete(
                self, 
                private_store_id: str, 
                collection_id: str, 
                offer_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                private_store_id: str, 
                collection_id: str, 
                offer_id: str, 
                **kwargs: Any
            ) -> Offer: ...

        @distributed_trace
        def list(
                self, 
                private_store_id: str, 
                collection_id: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Offer]: ...

        @overload
        def list_by_contexts(
                self, 
                private_store_id: str, 
                collection_id: str, 
                payload: Optional[CollectionOffersByAllContextsPayload] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncItemPaged[CollectionOffersByContext]: ...

        @overload
        def list_by_contexts(
                self, 
                private_store_id: str, 
                collection_id: str, 
                payload: Optional[CollectionOffersByAllContextsPayload] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncItemPaged[CollectionOffersByContext]: ...

        @overload
        def list_by_contexts(
                self, 
                private_store_id: str, 
                collection_id: str, 
                payload: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncItemPaged[CollectionOffersByContext]: ...

        @distributed_trace_async
        async def post(
                self, 
                private_store_id: str, 
                collection_id: str, 
                offer_id: str, 
                payload: Optional[Union[str, Operation]] = None, 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def upsert_offer_with_multi_context(
                self, 
                private_store_id: str, 
                collection_id: str, 
                offer_id: str, 
                payload: Optional[MultiContextAndPlansPayload] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Offer: ...

        @overload
        async def upsert_offer_with_multi_context(
                self, 
                private_store_id: str, 
                collection_id: str, 
                offer_id: str, 
                payload: Optional[MultiContextAndPlansPayload] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Offer: ...

        @overload
        async def upsert_offer_with_multi_context(
                self, 
                private_store_id: str, 
                collection_id: str, 
                offer_id: str, 
                payload: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Offer: ...


    class azure.mgmt.marketplace.aio.operations.PrivateStoreCollectionOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def approve_all_items(
                self, 
                private_store_id: str, 
                collection_id: str, 
                **kwargs: Any
            ) -> Collection: ...

        @overload
        async def create_or_update(
                self, 
                private_store_id: str, 
                collection_id: str, 
                payload: Optional[Collection] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Collection: ...

        @overload
        async def create_or_update(
                self, 
                private_store_id: str, 
                collection_id: str, 
                payload: Optional[Collection] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Collection: ...

        @overload
        async def create_or_update(
                self, 
                private_store_id: str, 
                collection_id: str, 
                payload: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Collection: ...

        @distributed_trace_async
        async def delete(
                self, 
                private_store_id: str, 
                collection_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def disable_approve_all_items(
                self, 
                private_store_id: str, 
                collection_id: str, 
                **kwargs: Any
            ) -> Collection: ...

        @distributed_trace_async
        async def get(
                self, 
                private_store_id: str, 
                collection_id: str, 
                **kwargs: Any
            ) -> Collection: ...

        @distributed_trace_async
        async def list(
                self, 
                private_store_id: str, 
                **kwargs: Any
            ) -> CollectionsList: ...

        @distributed_trace_async
        async def post(
                self, 
                private_store_id: str, 
                collection_id: str, 
                payload: Optional[Union[str, Operation]] = None, 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def transfer_offers(
                self, 
                private_store_id: str, 
                collection_id: str, 
                payload: Optional[TransferOffersProperties] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TransferOffersResponse: ...

        @overload
        async def transfer_offers(
                self, 
                private_store_id: str, 
                collection_id: str, 
                payload: Optional[TransferOffersProperties] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TransferOffersResponse: ...

        @overload
        async def transfer_offers(
                self, 
                private_store_id: str, 
                collection_id: str, 
                payload: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TransferOffersResponse: ...


    class azure.mgmt.marketplace.aio.operations.PrivateStoreOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def acknowledge_offer_notification(
                self, 
                private_store_id: str, 
                offer_id: str, 
                payload: Optional[AcknowledgeOfferNotificationProperties] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def acknowledge_offer_notification(
                self, 
                private_store_id: str, 
                offer_id: str, 
                payload: Optional[AcknowledgeOfferNotificationProperties] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def acknowledge_offer_notification(
                self, 
                private_store_id: str, 
                offer_id: str, 
                payload: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def admin_request_approvals_list(
                self, 
                private_store_id: str, 
                **kwargs: Any
            ) -> AdminRequestApprovalsList: ...

        @distributed_trace_async
        async def any_existing_offers_in_the_collections(
                self, 
                private_store_id: str, 
                **kwargs: Any
            ) -> AnyExistingOffersInTheCollectionsResponse: ...

        @distributed_trace_async
        async def billing_accounts(
                self, 
                private_store_id: str, 
                **kwargs: Any
            ) -> BillingAccountsResponse: ...

        @overload
        async def bulk_collections_action(
                self, 
                private_store_id: str, 
                payload: Optional[BulkCollectionsPayload] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> BulkCollectionsResponse: ...

        @overload
        async def bulk_collections_action(
                self, 
                private_store_id: str, 
                payload: Optional[BulkCollectionsPayload] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> BulkCollectionsResponse: ...

        @overload
        async def bulk_collections_action(
                self, 
                private_store_id: str, 
                payload: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> BulkCollectionsResponse: ...

        @overload
        async def collections_to_subscriptions_mapping(
                self, 
                private_store_id: str, 
                payload: Optional[CollectionsToSubscriptionsMappingPayload] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CollectionsToSubscriptionsMappingResponse: ...

        @overload
        async def collections_to_subscriptions_mapping(
                self, 
                private_store_id: str, 
                payload: Optional[CollectionsToSubscriptionsMappingPayload] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CollectionsToSubscriptionsMappingResponse: ...

        @overload
        async def collections_to_subscriptions_mapping(
                self, 
                private_store_id: str, 
                payload: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CollectionsToSubscriptionsMappingResponse: ...

        @overload
        async def create_approval_request(
                self, 
                private_store_id: str, 
                request_approval_id: str, 
                payload: RequestApprovalResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RequestApprovalResource: ...

        @overload
        async def create_approval_request(
                self, 
                private_store_id: str, 
                request_approval_id: str, 
                payload: RequestApprovalResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RequestApprovalResource: ...

        @overload
        async def create_approval_request(
                self, 
                private_store_id: str, 
                request_approval_id: str, 
                payload: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RequestApprovalResource: ...

        @overload
        async def create_or_update(
                self, 
                private_store_id: str, 
                payload: Optional[PrivateStore] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                private_store_id: str, 
                payload: Optional[PrivateStore] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                private_store_id: str, 
                payload: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def delete(
                self, 
                private_store_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def fetch_all_subscriptions_in_tenant(
                self, 
                private_store_id: str, 
                *, 
                next_page_token: Optional[str] = ..., 
                **kwargs: Any
            ) -> SubscriptionsResponse: ...

        @distributed_trace_async
        async def get(
                self, 
                private_store_id: str, 
                **kwargs: Any
            ) -> PrivateStore: ...

        @distributed_trace_async
        async def get_admin_request_approval(
                self, 
                private_store_id: str, 
                admin_request_approval_id: str, 
                *, 
                publisher_id: str, 
                **kwargs: Any
            ) -> AdminRequestApprovalsResource: ...

        @distributed_trace_async
        async def get_approval_requests_list(
                self, 
                private_store_id: str, 
                **kwargs: Any
            ) -> RequestApprovalsList: ...

        @distributed_trace_async
        async def get_request_approval(
                self, 
                private_store_id: str, 
                request_approval_id: str, 
                **kwargs: Any
            ) -> RequestApprovalResource: ...

        @distributed_trace
        def list(
                self, 
                *, 
                use_cache: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[PrivateStore]: ...

        @distributed_trace_async
        async def list_new_plans_notifications(
                self, 
                private_store_id: str, 
                **kwargs: Any
            ) -> NewPlansNotificationsList: ...

        @overload
        async def list_stop_sell_offers_plans_notifications(
                self, 
                private_store_id: str, 
                stop_sell_subscriptions: Optional[StopSellSubscriptions] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StopSellOffersPlansNotificationsList: ...

        @overload
        async def list_stop_sell_offers_plans_notifications(
                self, 
                private_store_id: str, 
                stop_sell_subscriptions: Optional[StopSellSubscriptions] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StopSellOffersPlansNotificationsList: ...

        @overload
        async def list_stop_sell_offers_plans_notifications(
                self, 
                private_store_id: str, 
                stop_sell_subscriptions: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StopSellOffersPlansNotificationsList: ...

        @distributed_trace_async
        async def list_subscriptions_context(
                self, 
                private_store_id: str, 
                **kwargs: Any
            ) -> SubscriptionsContextList: ...

        @overload
        async def query_approved_plans(
                self, 
                private_store_id: str, 
                payload: Optional[QueryApprovedPlansPayload] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> QueryApprovedPlansResponse: ...

        @overload
        async def query_approved_plans(
                self, 
                private_store_id: str, 
                payload: Optional[QueryApprovedPlansPayload] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> QueryApprovedPlansResponse: ...

        @overload
        async def query_approved_plans(
                self, 
                private_store_id: str, 
                payload: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> QueryApprovedPlansResponse: ...

        @distributed_trace_async
        async def query_notifications_state(
                self, 
                private_store_id: str, 
                **kwargs: Any
            ) -> PrivateStoreNotificationsState: ...

        @distributed_trace_async
        async def query_offers(
                self, 
                private_store_id: str, 
                **kwargs: Any
            ) -> QueryOffers: ...

        @overload
        async def query_request_approval(
                self, 
                private_store_id: str, 
                request_approval_id: str, 
                payload: Optional[QueryRequestApprovalProperties] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> QueryRequestApproval: ...

        @overload
        async def query_request_approval(
                self, 
                private_store_id: str, 
                request_approval_id: str, 
                payload: Optional[QueryRequestApprovalProperties] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> QueryRequestApproval: ...

        @overload
        async def query_request_approval(
                self, 
                private_store_id: str, 
                request_approval_id: str, 
                payload: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> QueryRequestApproval: ...

        @overload
        async def query_user_offers(
                self, 
                private_store_id: str, 
                payload: Optional[QueryUserOffersProperties] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> QueryOffers: ...

        @overload
        async def query_user_offers(
                self, 
                private_store_id: str, 
                payload: Optional[QueryUserOffersProperties] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> QueryOffers: ...

        @overload
        async def query_user_offers(
                self, 
                private_store_id: str, 
                payload: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> QueryOffers: ...

        @overload
        async def update_admin_request_approval(
                self, 
                private_store_id: str, 
                admin_request_approval_id: str, 
                payload: Optional[AdminRequestApprovalsResource] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AdminRequestApprovalsResource: ...

        @overload
        async def update_admin_request_approval(
                self, 
                private_store_id: str, 
                admin_request_approval_id: str, 
                payload: Optional[AdminRequestApprovalsResource] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AdminRequestApprovalsResource: ...

        @overload
        async def update_admin_request_approval(
                self, 
                private_store_id: str, 
                admin_request_approval_id: str, 
                payload: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AdminRequestApprovalsResource: ...

        @overload
        async def withdraw_plan(
                self, 
                private_store_id: str, 
                request_approval_id: str, 
                payload: Optional[WithdrawProperties] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def withdraw_plan(
                self, 
                private_store_id: str, 
                request_approval_id: str, 
                payload: Optional[WithdrawProperties] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def withdraw_plan(
                self, 
                private_store_id: str, 
                request_approval_id: str, 
                payload: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...


namespace azure.mgmt.marketplace.models

    class azure.mgmt.marketplace.models.Accessibility(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PRIVATE_SUBSCRIPTION_ON_LEVEL = "PrivateSubscriptionOnLevel"
        PRIVATE_TENANT_ON_LEVEL = "PrivateTenantOnLevel"
        PUBLIC = "Public"
        UNKNOWN = "Unknown"


    class azure.mgmt.marketplace.models.AcknowledgeOfferNotificationDetails(_Model):
        acknowledge: Optional[bool]
        add_plans: Optional[list[str]]
        dismiss: Optional[bool]
        remove_offer: Optional[bool]
        remove_plans: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                acknowledge: Optional[bool] = ..., 
                add_plans: Optional[list[str]] = ..., 
                dismiss: Optional[bool] = ..., 
                remove_offer: Optional[bool] = ..., 
                remove_plans: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.marketplace.models.AcknowledgeOfferNotificationProperties(_Model):
        properties: Optional[AcknowledgeOfferNotificationDetails]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[AcknowledgeOfferNotificationDetails] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.marketplace.models.AdminAction(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPROVED = "Approved"
        REJECTED = "Rejected"


    class azure.mgmt.marketplace.models.AdminRequestApprovalProperties(_Model):
        admin_action: Optional[Union[str, AdminAction]]
        administrator: Optional[str]
        approved_plans: Optional[list[str]]
        collection_ids: Optional[list[str]]
        comment: Optional[str]
        display_name: Optional[str]
        icon: Optional[str]
        offer_id: Optional[str]
        plans: Optional[list[PlanRequesterDetails]]
        publisher_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                admin_action: Optional[Union[str, AdminAction]] = ..., 
                administrator: Optional[str] = ..., 
                approved_plans: Optional[list[str]] = ..., 
                collection_ids: Optional[list[str]] = ..., 
                comment: Optional[str] = ..., 
                offer_id: Optional[str] = ..., 
                publisher_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.marketplace.models.AdminRequestApprovalsList(_Model):
        next_link: Optional[str]
        value: Optional[list[AdminRequestApprovalsResource]]

        @overload
        def __init__(
                self, 
                *, 
                value: Optional[list[AdminRequestApprovalsResource]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.marketplace.models.AdminRequestApprovalsResource(ProxyResource):
        id: str
        name: str
        properties: Optional[AdminRequestApprovalProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[AdminRequestApprovalProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.marketplace.models.AnyExistingOffersInTheCollectionsResponse(_Model):
        value: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                value: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.marketplace.models.Availability(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "disabled"
        ENABLED = "enabled"


    class azure.mgmt.marketplace.models.BillingAccountsResponse(_Model):
        billing_accounts: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                billing_accounts: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.marketplace.models.BulkCollectionsDetails(_Model):
        action: Optional[str]
        collection_ids: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                action: Optional[str] = ..., 
                collection_ids: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.marketplace.models.BulkCollectionsPayload(_Model):
        properties: Optional[BulkCollectionsDetails]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[BulkCollectionsDetails] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.marketplace.models.BulkCollectionsResponse(_Model):
        failed: Optional[list[CollectionsDetails]]
        succeeded: Optional[list[CollectionsDetails]]

        @overload
        def __init__(
                self, 
                *, 
                failed: Optional[list[CollectionsDetails]] = ..., 
                succeeded: Optional[list[CollectionsDetails]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.marketplace.models.Collection(ProxyResource):
        id: str
        name: str
        properties: Optional[CollectionProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[CollectionProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.marketplace.models.CollectionOffersByAllContextsPayload(_Model):
        properties: Optional[CollectionOffersByAllContextsProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[CollectionOffersByAllContextsProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.marketplace.models.CollectionOffersByAllContextsProperties(_Model):
        subscription_ids: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                subscription_ids: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.marketplace.models.CollectionOffersByContext(_Model):
        context: Optional[str]
        offers: Optional[CollectionOffersByContextOffers]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                offers: Optional[CollectionOffersByContextOffers] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.marketplace.models.CollectionOffersByContextOffers(_Model):
        value: Optional[list[OfferProperties]]

        @overload
        def __init__(
                self, 
                *, 
                value: Optional[list[OfferProperties]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.marketplace.models.CollectionProperties(_Model):
        all_subscriptions: Optional[bool]
        applied_rules: Optional[list[Rule]]
        approve_all_items: Optional[bool]
        approve_all_items_modified_at: Optional[datetime]
        claim: Optional[str]
        collection_id: Optional[str]
        collection_name: Optional[str]
        enabled: Optional[bool]
        number_of_offers: Optional[int]
        subscriptions_list: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                all_subscriptions: Optional[bool] = ..., 
                claim: Optional[str] = ..., 
                collection_name: Optional[str] = ..., 
                enabled: Optional[bool] = ..., 
                subscriptions_list: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.marketplace.models.CollectionsDetails(_Model):
        collection_id: Optional[str]
        collection_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                collection_id: Optional[str] = ..., 
                collection_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.marketplace.models.CollectionsList(_Model):
        next_link: Optional[str]
        value: Optional[list[Collection]]

        @overload
        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[list[Collection]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.marketplace.models.CollectionsSubscriptionsMappingDetails(_Model):
        collection_name: Optional[str]
        subscriptions: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                collection_name: Optional[str] = ..., 
                subscriptions: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.marketplace.models.CollectionsToSubscriptionsMappingPayload(_Model):
        properties: Optional[CollectionsToSubscriptionsMappingProperties]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[CollectionsToSubscriptionsMappingProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.marketplace.models.CollectionsToSubscriptionsMappingProperties(_Model):
        subscription_ids: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                subscription_ids: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.marketplace.models.CollectionsToSubscriptionsMappingResponse(_Model):
        details: Optional[dict[str, CollectionsSubscriptionsMappingDetails]]

        @overload
        def __init__(
                self, 
                *, 
                details: Optional[dict[str, CollectionsSubscriptionsMappingDetails]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.marketplace.models.ContextAndPlansDetails(_Model):
        context: Optional[str]
        plan_ids: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                context: Optional[str] = ..., 
                plan_ids: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.marketplace.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.marketplace.models.ErrorResponse(_Model):
        error: Optional[ErrorResponseError]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorResponseError] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.marketplace.models.ErrorResponseError(_Model):
        code: Optional[str]
        message: Optional[str]


    class azure.mgmt.marketplace.models.MultiContextAndPlansPayload(_Model):
        properties: Optional[MultiContextAndPlansProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[MultiContextAndPlansProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.marketplace.models.MultiContextAndPlansProperties(_Model):
        e_tag: Optional[str]
        offer_id: Optional[str]
        plans_context: Optional[list[ContextAndPlansDetails]]

        @overload
        def __init__(
                self, 
                *, 
                e_tag: Optional[str] = ..., 
                offer_id: Optional[str] = ..., 
                plans_context: Optional[list[ContextAndPlansDetails]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.marketplace.models.NewNotifications(_Model):
        display_name: Optional[str]
        icon: Optional[str]
        is_future_plans_enabled: Optional[bool]
        message_code: Optional[int]
        offer_id: Optional[str]
        plans: Optional[list[PlanNotificationDetails]]

        @overload
        def __init__(
                self, 
                *, 
                display_name: Optional[str] = ..., 
                icon: Optional[str] = ..., 
                is_future_plans_enabled: Optional[bool] = ..., 
                message_code: Optional[int] = ..., 
                offer_id: Optional[str] = ..., 
                plans: Optional[list[PlanNotificationDetails]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.marketplace.models.NewPlansNotificationsList(_Model):
        new_plans_notifications: Optional[list[NewNotifications]]

        @overload
        def __init__(
                self, 
                *, 
                new_plans_notifications: Optional[list[NewNotifications]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.marketplace.models.NotificationsSettingsProperties(_Model):
        recipients: Optional[list[Recipient]]
        send_to_all_marketplace_admins: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                recipients: Optional[list[Recipient]] = ..., 
                send_to_all_marketplace_admins: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.marketplace.models.Offer(ProxyResource):
        id: str
        name: str
        properties: Optional[OfferProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[OfferProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.marketplace.models.OfferProperties(_Model):
        created_at: Optional[str]
        e_tag: Optional[str]
        icon_file_uris: Optional[dict[str, str]]
        is_stop_sell: Optional[bool]
        modified_at: Optional[str]
        offer_display_name: Optional[str]
        plans: Optional[list[Plan]]
        private_store_id: Optional[str]
        publisher_display_name: Optional[str]
        specific_plan_ids_limitation: Optional[list[str]]
        unique_offer_id: Optional[str]
        update_suppressed_due_idempotence: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                e_tag: Optional[str] = ..., 
                icon_file_uris: Optional[dict[str, str]] = ..., 
                plans: Optional[list[Plan]] = ..., 
                specific_plan_ids_limitation: Optional[list[str]] = ..., 
                update_suppressed_due_idempotence: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.marketplace.models.Operation(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DELETE_PRIVATE_STORE_COLLECTION = "DeletePrivateStoreCollection"
        DELETE_PRIVATE_STORE_COLLECTION_OFFER = "DeletePrivateStoreCollectionOffer"
        DELETE_PRIVATE_STORE_OFFER = "DeletePrivateStoreOffer"
        PING = "Ping"


    class azure.mgmt.marketplace.models.Plan(_Model):
        accessibility: Optional[Union[str, Accessibility]]
        alt_stack_reference: Optional[str]
        is_stop_sell: Optional[bool]
        plan_display_name: Optional[str]
        plan_id: Optional[str]
        sku_id: Optional[str]
        stack_type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                accessibility: Optional[Union[str, Accessibility]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.marketplace.models.PlanDetails(_Model):
        justification: Optional[str]
        plan_id: Optional[str]
        request_date: Optional[Any]
        status: Optional[Union[str, Status]]
        subscription_id: Optional[str]
        subscription_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                justification: Optional[str] = ..., 
                plan_id: Optional[str] = ..., 
                subscription_id: Optional[str] = ..., 
                subscription_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.marketplace.models.PlanNotificationDetails(_Model):
        plan_display_name: Optional[str]
        plan_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                plan_display_name: Optional[str] = ..., 
                plan_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.marketplace.models.PlanRequesterDetails(_Model):
        plan_display_name: Optional[str]
        plan_id: Optional[str]
        requesters: Optional[list[UserRequestDetails]]


    class azure.mgmt.marketplace.models.PrivateStore(ProxyResource):
        id: str
        name: str
        properties: Optional[PrivateStoreProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[PrivateStoreProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.marketplace.models.PrivateStoreNotificationsState(_Model):
        approval_requests: Optional[list[RequestApprovalsDetails]]
        new_notifications: Optional[list[NewNotifications]]
        stop_sell_notifications: Optional[list[StopSellNotifications]]

        @overload
        def __init__(
                self, 
                *, 
                approval_requests: Optional[list[RequestApprovalsDetails]] = ..., 
                new_notifications: Optional[list[NewNotifications]] = ..., 
                stop_sell_notifications: Optional[list[StopSellNotifications]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.marketplace.models.PrivateStoreProperties(_Model):
        availability: Optional[Union[str, Availability]]
        branding: Optional[dict[str, str]]
        collection_ids: Optional[list[str]]
        e_tag: Optional[str]
        is_gov: Optional[bool]
        notifications_settings: Optional[NotificationsSettingsProperties]
        private_store_id: Optional[str]
        private_store_name: Optional[str]
        tenant_id: Optional[str]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                availability: Optional[Union[str, Availability]] = ..., 
                branding: Optional[dict[str, str]] = ..., 
                e_tag: Optional[str] = ..., 
                is_gov: Optional[bool] = ..., 
                notifications_settings: Optional[NotificationsSettingsProperties] = ..., 
                private_store_name: Optional[str] = ..., 
                tenant_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.marketplace.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.marketplace.models.QueryApprovedPlans(_Model):
        offer_id: Optional[str]
        plan_ids: Optional[list[str]]
        subscription_ids: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                offer_id: Optional[str] = ..., 
                plan_ids: Optional[list[str]] = ..., 
                subscription_ids: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.marketplace.models.QueryApprovedPlansDetails(_Model):
        all_subscriptions: Optional[bool]
        plan_id: Optional[str]
        subscription_ids: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                all_subscriptions: Optional[bool] = ..., 
                plan_id: Optional[str] = ..., 
                subscription_ids: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.marketplace.models.QueryApprovedPlansPayload(_Model):
        properties: Optional[QueryApprovedPlans]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[QueryApprovedPlans] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.marketplace.models.QueryApprovedPlansResponse(_Model):
        details: Optional[list[QueryApprovedPlansDetails]]

        @overload
        def __init__(
                self, 
                *, 
                details: Optional[list[QueryApprovedPlansDetails]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.marketplace.models.QueryOffers(_Model):
        next_link: Optional[str]
        value: Optional[list[OfferProperties]]

        @overload
        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[list[OfferProperties]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.marketplace.models.QueryRequestApproval(_Model):
        etag: Optional[str]
        message_code: Optional[int]
        plans_details: Optional[dict[str, PlanDetails]]
        unique_offer_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                message_code: Optional[int] = ..., 
                plans_details: Optional[dict[str, PlanDetails]] = ..., 
                unique_offer_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.marketplace.models.QueryRequestApprovalProperties(_Model):
        properties: Optional[RequestDetails]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[RequestDetails] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.marketplace.models.QueryUserOffersDetails(_Model):
        offer_ids: Optional[list[str]]
        subscription_ids: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                offer_ids: Optional[list[str]] = ..., 
                subscription_ids: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.marketplace.models.QueryUserOffersProperties(_Model):
        properties: Optional[QueryUserOffersDetails]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[QueryUserOffersDetails] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.marketplace.models.QueryUserRulesDetails(_Model):
        subscription_ids: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                subscription_ids: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.marketplace.models.QueryUserRulesProperties(_Model):
        properties: Optional[QueryUserRulesDetails]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[QueryUserRulesDetails] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.marketplace.models.Recipient(_Model):
        display_name: Optional[str]
        email_address: Optional[str]
        principal_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                principal_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.marketplace.models.RequestApprovalProperties(_Model):
        is_closed: Optional[bool]
        message_code: Optional[int]
        offer_display_name: Optional[str]
        offer_id: Optional[str]
        plans_details: Optional[list[PlanDetails]]
        publisher_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                message_code: Optional[int] = ..., 
                offer_id: Optional[str] = ..., 
                plans_details: Optional[list[PlanDetails]] = ..., 
                publisher_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.marketplace.models.RequestApprovalResource(ProxyResource):
        id: str
        name: str
        properties: Optional[RequestApprovalProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[RequestApprovalProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.marketplace.models.RequestApprovalsDetails(_Model):
        display_name: Optional[str]
        icon: Optional[str]
        message_code: Optional[int]
        offer_id: Optional[str]
        plans: Optional[list[PlanNotificationDetails]]
        publisher_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                display_name: Optional[str] = ..., 
                icon: Optional[str] = ..., 
                message_code: Optional[int] = ..., 
                offer_id: Optional[str] = ..., 
                plans: Optional[list[PlanNotificationDetails]] = ..., 
                publisher_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.marketplace.models.RequestApprovalsList(_Model):
        next_link: Optional[str]
        value: Optional[list[RequestApprovalResource]]

        @overload
        def __init__(
                self, 
                *, 
                value: Optional[list[RequestApprovalResource]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.marketplace.models.RequestDetails(_Model):
        plan_ids: Optional[list[str]]
        publisher_id: Optional[str]
        subscription_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                plan_ids: Optional[list[str]] = ..., 
                publisher_id: Optional[str] = ..., 
                subscription_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.marketplace.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.marketplace.models.Rule(_Model):
        type: Optional[Union[str, RuleType]]
        value: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                type: Optional[Union[str, RuleType]] = ..., 
                value: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.marketplace.models.RuleListResponse(_Model):
        next_link: Optional[str]
        value: Optional[list[Rule]]

        @overload
        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.marketplace.models.RuleType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PRIVATE_PRODUCTS = "PrivateProducts"
        TERMS_AND_CONDITION = "TermsAndCondition"


    class azure.mgmt.marketplace.models.SetRulesRequest(_Model):
        next_link: Optional[str]
        value: Optional[list[Rule]]

        @overload
        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[list[Rule]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.marketplace.models.SingleOperation(_Model):
        display: Optional[SingleOperationDisplay]
        id: Optional[str]
        is_data_action: Optional[bool]
        name: Optional[str]
        origin: Optional[str]
        properties: Optional[Any]

        @overload
        def __init__(
                self, 
                *, 
                display: Optional[SingleOperationDisplay] = ..., 
                id: Optional[str] = ..., 
                is_data_action: Optional[bool] = ..., 
                name: Optional[str] = ..., 
                origin: Optional[str] = ..., 
                properties: Optional[Any] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.marketplace.models.SingleOperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.marketplace.models.Status(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPROVED = "Approved"
        NONE = "None"
        PENDING = "Pending"
        REJECTED = "Rejected"


    class azure.mgmt.marketplace.models.StopSellNotifications(_Model):
        display_name: Optional[str]
        icon: Optional[str]
        is_entire: Optional[bool]
        message_code: Optional[int]
        offer_id: Optional[str]
        plans: Optional[list[PlanNotificationDetails]]

        @overload
        def __init__(
                self, 
                *, 
                display_name: Optional[str] = ..., 
                icon: Optional[str] = ..., 
                is_entire: Optional[bool] = ..., 
                message_code: Optional[int] = ..., 
                offer_id: Optional[str] = ..., 
                plans: Optional[list[PlanNotificationDetails]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.marketplace.models.StopSellOffersPlansNotificationsList(_Model):
        stop_sell_notifications: Optional[list[StopSellOffersPlansNotificationsListProperties]]

        @overload
        def __init__(
                self, 
                *, 
                stop_sell_notifications: Optional[list[StopSellOffersPlansNotificationsListProperties]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.marketplace.models.StopSellOffersPlansNotificationsListProperties(_Model):
        display_name: Optional[str]
        icon: Optional[str]
        is_entire: Optional[bool]
        message_code: Optional[int]
        offer_id: Optional[str]
        plans: Optional[list[PlanNotificationDetails]]
        public_context: Optional[bool]
        subscriptions_ids: Optional[list[str]]


    class azure.mgmt.marketplace.models.StopSellSubscriptions(_Model):
        subscriptions: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                subscriptions: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.marketplace.models.Subscription(_Model):
        display_name: Optional[str]
        id: Optional[str]
        state: Optional[Union[str, SubscriptionState]]
        subscription_id: Optional[str]


    class azure.mgmt.marketplace.models.SubscriptionState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DELETED = "Deleted"
        DISABLED = "Disabled"
        ENABLED = "Enabled"
        PAST_DUE = "PastDue"
        WARNED = "Warned"


    class azure.mgmt.marketplace.models.SubscriptionsContextList(_Model):
        subscriptions_ids: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                subscriptions_ids: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.marketplace.models.SubscriptionsResponse(_Model):
        count: Optional[int]
        skip_token: Optional[str]
        value: Optional[list[Subscription]]


    class azure.mgmt.marketplace.models.SystemData(_Model):
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


    class azure.mgmt.marketplace.models.TransferOffersDetails(_Model):
        offer_ids_list: Optional[list[str]]
        operation: Optional[str]
        target_collections: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                offer_ids_list: Optional[list[str]] = ..., 
                operation: Optional[str] = ..., 
                target_collections: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.marketplace.models.TransferOffersProperties(_Model):
        properties: Optional[TransferOffersDetails]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[TransferOffersDetails] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.marketplace.models.TransferOffersResponse(_Model):
        failed: Optional[list[CollectionsDetails]]
        succeeded: Optional[list[CollectionsDetails]]

        @overload
        def __init__(
                self, 
                *, 
                failed: Optional[list[CollectionsDetails]] = ..., 
                succeeded: Optional[list[CollectionsDetails]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.marketplace.models.UserRequestDetails(_Model):
        date: Optional[str]
        justification: Optional[str]
        subscription_id: Optional[str]
        subscription_name: Optional[str]
        user: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                subscription_id: Optional[str] = ..., 
                subscription_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.marketplace.models.WithdrawDetails(_Model):
        plan_id: Optional[str]
        publisher_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                plan_id: Optional[str] = ..., 
                publisher_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.marketplace.models.WithdrawProperties(_Model):
        properties: Optional[WithdrawDetails]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[WithdrawDetails] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


namespace azure.mgmt.marketplace.operations

    class azure.mgmt.marketplace.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[SingleOperation]: ...


    class azure.mgmt.marketplace.operations.PrivateStoreCollectionOfferOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def contexts_view(
                self, 
                private_store_id: str, 
                collection_id: str, 
                offer_id: str, 
                payload: Optional[CollectionOffersByAllContextsPayload] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Offer: ...

        @overload
        def contexts_view(
                self, 
                private_store_id: str, 
                collection_id: str, 
                offer_id: str, 
                payload: Optional[CollectionOffersByAllContextsPayload] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Offer: ...

        @overload
        def contexts_view(
                self, 
                private_store_id: str, 
                collection_id: str, 
                offer_id: str, 
                payload: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Offer: ...

        @overload
        def create_or_update(
                self, 
                private_store_id: str, 
                collection_id: str, 
                offer_id: str, 
                payload: Offer, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Offer: ...

        @overload
        def create_or_update(
                self, 
                private_store_id: str, 
                collection_id: str, 
                offer_id: str, 
                payload: Offer, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Offer: ...

        @overload
        def create_or_update(
                self, 
                private_store_id: str, 
                collection_id: str, 
                offer_id: str, 
                payload: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Offer: ...

        @distributed_trace
        def delete(
                self, 
                private_store_id: str, 
                collection_id: str, 
                offer_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                private_store_id: str, 
                collection_id: str, 
                offer_id: str, 
                **kwargs: Any
            ) -> Offer: ...

        @distributed_trace
        def list(
                self, 
                private_store_id: str, 
                collection_id: str, 
                **kwargs: Any
            ) -> ItemPaged[Offer]: ...

        @overload
        def list_by_contexts(
                self, 
                private_store_id: str, 
                collection_id: str, 
                payload: Optional[CollectionOffersByAllContextsPayload] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ItemPaged[CollectionOffersByContext]: ...

        @overload
        def list_by_contexts(
                self, 
                private_store_id: str, 
                collection_id: str, 
                payload: Optional[CollectionOffersByAllContextsPayload] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ItemPaged[CollectionOffersByContext]: ...

        @overload
        def list_by_contexts(
                self, 
                private_store_id: str, 
                collection_id: str, 
                payload: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ItemPaged[CollectionOffersByContext]: ...

        @distributed_trace
        def post(
                self, 
                private_store_id: str, 
                collection_id: str, 
                offer_id: str, 
                payload: Optional[Union[str, Operation]] = None, 
                **kwargs: Any
            ) -> None: ...

        @overload
        def upsert_offer_with_multi_context(
                self, 
                private_store_id: str, 
                collection_id: str, 
                offer_id: str, 
                payload: Optional[MultiContextAndPlansPayload] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Offer: ...

        @overload
        def upsert_offer_with_multi_context(
                self, 
                private_store_id: str, 
                collection_id: str, 
                offer_id: str, 
                payload: Optional[MultiContextAndPlansPayload] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Offer: ...

        @overload
        def upsert_offer_with_multi_context(
                self, 
                private_store_id: str, 
                collection_id: str, 
                offer_id: str, 
                payload: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Offer: ...


    class azure.mgmt.marketplace.operations.PrivateStoreCollectionOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def approve_all_items(
                self, 
                private_store_id: str, 
                collection_id: str, 
                **kwargs: Any
            ) -> Collection: ...

        @overload
        def create_or_update(
                self, 
                private_store_id: str, 
                collection_id: str, 
                payload: Optional[Collection] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Collection: ...

        @overload
        def create_or_update(
                self, 
                private_store_id: str, 
                collection_id: str, 
                payload: Optional[Collection] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Collection: ...

        @overload
        def create_or_update(
                self, 
                private_store_id: str, 
                collection_id: str, 
                payload: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Collection: ...

        @distributed_trace
        def delete(
                self, 
                private_store_id: str, 
                collection_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def disable_approve_all_items(
                self, 
                private_store_id: str, 
                collection_id: str, 
                **kwargs: Any
            ) -> Collection: ...

        @distributed_trace
        def get(
                self, 
                private_store_id: str, 
                collection_id: str, 
                **kwargs: Any
            ) -> Collection: ...

        @distributed_trace
        def list(
                self, 
                private_store_id: str, 
                **kwargs: Any
            ) -> CollectionsList: ...

        @distributed_trace
        def post(
                self, 
                private_store_id: str, 
                collection_id: str, 
                payload: Optional[Union[str, Operation]] = None, 
                **kwargs: Any
            ) -> None: ...

        @overload
        def transfer_offers(
                self, 
                private_store_id: str, 
                collection_id: str, 
                payload: Optional[TransferOffersProperties] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TransferOffersResponse: ...

        @overload
        def transfer_offers(
                self, 
                private_store_id: str, 
                collection_id: str, 
                payload: Optional[TransferOffersProperties] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TransferOffersResponse: ...

        @overload
        def transfer_offers(
                self, 
                private_store_id: str, 
                collection_id: str, 
                payload: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TransferOffersResponse: ...


    class azure.mgmt.marketplace.operations.PrivateStoreOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def acknowledge_offer_notification(
                self, 
                private_store_id: str, 
                offer_id: str, 
                payload: Optional[AcknowledgeOfferNotificationProperties] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def acknowledge_offer_notification(
                self, 
                private_store_id: str, 
                offer_id: str, 
                payload: Optional[AcknowledgeOfferNotificationProperties] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def acknowledge_offer_notification(
                self, 
                private_store_id: str, 
                offer_id: str, 
                payload: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def admin_request_approvals_list(
                self, 
                private_store_id: str, 
                **kwargs: Any
            ) -> AdminRequestApprovalsList: ...

        @distributed_trace
        def any_existing_offers_in_the_collections(
                self, 
                private_store_id: str, 
                **kwargs: Any
            ) -> AnyExistingOffersInTheCollectionsResponse: ...

        @distributed_trace
        def billing_accounts(
                self, 
                private_store_id: str, 
                **kwargs: Any
            ) -> BillingAccountsResponse: ...

        @overload
        def bulk_collections_action(
                self, 
                private_store_id: str, 
                payload: Optional[BulkCollectionsPayload] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> BulkCollectionsResponse: ...

        @overload
        def bulk_collections_action(
                self, 
                private_store_id: str, 
                payload: Optional[BulkCollectionsPayload] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> BulkCollectionsResponse: ...

        @overload
        def bulk_collections_action(
                self, 
                private_store_id: str, 
                payload: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> BulkCollectionsResponse: ...

        @overload
        def collections_to_subscriptions_mapping(
                self, 
                private_store_id: str, 
                payload: Optional[CollectionsToSubscriptionsMappingPayload] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CollectionsToSubscriptionsMappingResponse: ...

        @overload
        def collections_to_subscriptions_mapping(
                self, 
                private_store_id: str, 
                payload: Optional[CollectionsToSubscriptionsMappingPayload] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CollectionsToSubscriptionsMappingResponse: ...

        @overload
        def collections_to_subscriptions_mapping(
                self, 
                private_store_id: str, 
                payload: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CollectionsToSubscriptionsMappingResponse: ...

        @overload
        def create_approval_request(
                self, 
                private_store_id: str, 
                request_approval_id: str, 
                payload: RequestApprovalResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RequestApprovalResource: ...

        @overload
        def create_approval_request(
                self, 
                private_store_id: str, 
                request_approval_id: str, 
                payload: RequestApprovalResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RequestApprovalResource: ...

        @overload
        def create_approval_request(
                self, 
                private_store_id: str, 
                request_approval_id: str, 
                payload: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RequestApprovalResource: ...

        @overload
        def create_or_update(
                self, 
                private_store_id: str, 
                payload: Optional[PrivateStore] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                private_store_id: str, 
                payload: Optional[PrivateStore] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                private_store_id: str, 
                payload: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def delete(
                self, 
                private_store_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def fetch_all_subscriptions_in_tenant(
                self, 
                private_store_id: str, 
                *, 
                next_page_token: Optional[str] = ..., 
                **kwargs: Any
            ) -> SubscriptionsResponse: ...

        @distributed_trace
        def get(
                self, 
                private_store_id: str, 
                **kwargs: Any
            ) -> PrivateStore: ...

        @distributed_trace
        def get_admin_request_approval(
                self, 
                private_store_id: str, 
                admin_request_approval_id: str, 
                *, 
                publisher_id: str, 
                **kwargs: Any
            ) -> AdminRequestApprovalsResource: ...

        @distributed_trace
        def get_approval_requests_list(
                self, 
                private_store_id: str, 
                **kwargs: Any
            ) -> RequestApprovalsList: ...

        @distributed_trace
        def get_request_approval(
                self, 
                private_store_id: str, 
                request_approval_id: str, 
                **kwargs: Any
            ) -> RequestApprovalResource: ...

        @distributed_trace
        def list(
                self, 
                *, 
                use_cache: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[PrivateStore]: ...

        @distributed_trace
        def list_new_plans_notifications(
                self, 
                private_store_id: str, 
                **kwargs: Any
            ) -> NewPlansNotificationsList: ...

        @overload
        def list_stop_sell_offers_plans_notifications(
                self, 
                private_store_id: str, 
                stop_sell_subscriptions: Optional[StopSellSubscriptions] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StopSellOffersPlansNotificationsList: ...

        @overload
        def list_stop_sell_offers_plans_notifications(
                self, 
                private_store_id: str, 
                stop_sell_subscriptions: Optional[StopSellSubscriptions] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StopSellOffersPlansNotificationsList: ...

        @overload
        def list_stop_sell_offers_plans_notifications(
                self, 
                private_store_id: str, 
                stop_sell_subscriptions: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StopSellOffersPlansNotificationsList: ...

        @distributed_trace
        def list_subscriptions_context(
                self, 
                private_store_id: str, 
                **kwargs: Any
            ) -> SubscriptionsContextList: ...

        @overload
        def query_approved_plans(
                self, 
                private_store_id: str, 
                payload: Optional[QueryApprovedPlansPayload] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> QueryApprovedPlansResponse: ...

        @overload
        def query_approved_plans(
                self, 
                private_store_id: str, 
                payload: Optional[QueryApprovedPlansPayload] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> QueryApprovedPlansResponse: ...

        @overload
        def query_approved_plans(
                self, 
                private_store_id: str, 
                payload: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> QueryApprovedPlansResponse: ...

        @distributed_trace
        def query_notifications_state(
                self, 
                private_store_id: str, 
                **kwargs: Any
            ) -> PrivateStoreNotificationsState: ...

        @distributed_trace
        def query_offers(
                self, 
                private_store_id: str, 
                **kwargs: Any
            ) -> QueryOffers: ...

        @overload
        def query_request_approval(
                self, 
                private_store_id: str, 
                request_approval_id: str, 
                payload: Optional[QueryRequestApprovalProperties] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> QueryRequestApproval: ...

        @overload
        def query_request_approval(
                self, 
                private_store_id: str, 
                request_approval_id: str, 
                payload: Optional[QueryRequestApprovalProperties] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> QueryRequestApproval: ...

        @overload
        def query_request_approval(
                self, 
                private_store_id: str, 
                request_approval_id: str, 
                payload: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> QueryRequestApproval: ...

        @overload
        def query_user_offers(
                self, 
                private_store_id: str, 
                payload: Optional[QueryUserOffersProperties] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> QueryOffers: ...

        @overload
        def query_user_offers(
                self, 
                private_store_id: str, 
                payload: Optional[QueryUserOffersProperties] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> QueryOffers: ...

        @overload
        def query_user_offers(
                self, 
                private_store_id: str, 
                payload: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> QueryOffers: ...

        @overload
        def update_admin_request_approval(
                self, 
                private_store_id: str, 
                admin_request_approval_id: str, 
                payload: Optional[AdminRequestApprovalsResource] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AdminRequestApprovalsResource: ...

        @overload
        def update_admin_request_approval(
                self, 
                private_store_id: str, 
                admin_request_approval_id: str, 
                payload: Optional[AdminRequestApprovalsResource] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AdminRequestApprovalsResource: ...

        @overload
        def update_admin_request_approval(
                self, 
                private_store_id: str, 
                admin_request_approval_id: str, 
                payload: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AdminRequestApprovalsResource: ...

        @overload
        def withdraw_plan(
                self, 
                private_store_id: str, 
                request_approval_id: str, 
                payload: Optional[WithdrawProperties] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def withdraw_plan(
                self, 
                private_store_id: str, 
                request_approval_id: str, 
                payload: Optional[WithdrawProperties] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def withdraw_plan(
                self, 
                private_store_id: str, 
                request_approval_id: str, 
                payload: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...


namespace azure.mgmt.marketplace.types

    class azure.mgmt.marketplace.types.AcknowledgeOfferNotificationDetails(TypedDict, total=False):
        key "acknowledge": bool
        key "dismiss": bool
        key "removeOffer": bool
        acknowledge: bool
        addPlans: list[str]
        add_plans: list[str]
        dismiss: bool
        removePlans: list[str]
        remove_offer: bool
        remove_plans: list[str]


    class azure.mgmt.marketplace.types.AcknowledgeOfferNotificationProperties(TypedDict, total=False):
        key "properties": ForwardRef('AcknowledgeOfferNotificationDetails', module='types')
        properties: AcknowledgeOfferNotificationDetails


    class azure.mgmt.marketplace.types.AdminRequestApprovalProperties(TypedDict, total=False):
        key "adminAction": Union[str, AdminAction]
        key "administrator": str
        key "comment": str
        key "displayName": str
        key "icon": str
        key "offerId": str
        key "publisherId": str
        admin_action: Union[str, AdminAction]
        administrator: str
        approvedPlans: list[str]
        approved_plans: list[str]
        collectionIds: list[str]
        collection_ids: list[str]
        comment: str
        display_name: str
        icon: str
        offer_id: str
        plans: list[PlanRequesterDetails]
        publisher_id: str


    class azure.mgmt.marketplace.types.AdminRequestApprovalsResource(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('AdminRequestApprovalProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: AdminRequestApprovalProperties
        system_data: SystemData
        type: str


    class azure.mgmt.marketplace.types.BulkCollectionsDetails(TypedDict, total=False):
        key "action": str
        action: str
        collectionIds: list[str]
        collection_ids: list[str]


    class azure.mgmt.marketplace.types.BulkCollectionsPayload(TypedDict, total=False):
        key "properties": ForwardRef('BulkCollectionsDetails', module='types')
        properties: BulkCollectionsDetails


    class azure.mgmt.marketplace.types.Collection(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('CollectionProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: CollectionProperties
        system_data: SystemData
        type: str


    class azure.mgmt.marketplace.types.CollectionOffersByAllContextsPayload(TypedDict, total=False):
        key "properties": ForwardRef('CollectionOffersByAllContextsProperties', module='types')
        properties: CollectionOffersByAllContextsProperties


    class azure.mgmt.marketplace.types.CollectionOffersByAllContextsProperties(TypedDict, total=False):
        subscriptionIds: list[str]
        subscription_ids: list[str]


    class azure.mgmt.marketplace.types.CollectionProperties(TypedDict, total=False):
        key "allSubscriptions": bool
        key "approveAllItems": bool
        key "approveAllItemsModifiedAt": str
        key "claim": str
        key "collectionId": str
        key "collectionName": str
        key "enabled": bool
        key "numberOfOffers": int
        all_subscriptions: bool
        appliedRules: list[Rule]
        applied_rules: list[Rule]
        approve_all_items: bool
        approve_all_items_modified_at: str
        claim: str
        collection_id: str
        collection_name: str
        enabled: bool
        number_of_offers: int
        subscriptionsList: list[str]
        subscriptions_list: list[str]


    class azure.mgmt.marketplace.types.CollectionsToSubscriptionsMappingPayload(TypedDict, total=False):
        key "properties": ForwardRef('CollectionsToSubscriptionsMappingProperties', module='types')
        properties: CollectionsToSubscriptionsMappingProperties


    class azure.mgmt.marketplace.types.CollectionsToSubscriptionsMappingProperties(TypedDict, total=False):
        subscriptionIds: list[str]
        subscription_ids: list[str]


    class azure.mgmt.marketplace.types.ContextAndPlansDetails(TypedDict, total=False):
        key "context": str
        context: str
        planIds: list[str]
        plan_ids: list[str]


    class azure.mgmt.marketplace.types.MultiContextAndPlansPayload(TypedDict, total=False):
        key "properties": ForwardRef('MultiContextAndPlansProperties', module='types')
        properties: MultiContextAndPlansProperties


    class azure.mgmt.marketplace.types.MultiContextAndPlansProperties(TypedDict, total=False):
        key "eTag": str
        key "offerId": str
        e_tag: str
        offer_id: str
        plansContext: list[ContextAndPlansDetails]
        plans_context: list[ContextAndPlansDetails]


    class azure.mgmt.marketplace.types.NotificationsSettingsProperties(TypedDict, total=False):
        key "sendToAllMarketplaceAdmins": bool
        recipients: list[Recipient]
        send_to_all_marketplace_admins: bool


    class azure.mgmt.marketplace.types.Offer(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('OfferProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: OfferProperties
        system_data: SystemData
        type: str


    class azure.mgmt.marketplace.types.OfferProperties(TypedDict, total=False):
        key "createdAt": str
        key "eTag": str
        key "isStopSell": bool
        key "modifiedAt": str
        key "offerDisplayName": str
        key "privateStoreId": str
        key "publisherDisplayName": str
        key "uniqueOfferId": str
        key "updateSuppressedDueIdempotence": bool
        created_at: str
        e_tag: str
        iconFileUris: dict[str, str]
        icon_file_uris: dict[str, str]
        is_stop_sell: bool
        modified_at: str
        offer_display_name: str
        plans: list[Plan]
        private_store_id: str
        publisher_display_name: str
        specificPlanIdsLimitation: list[str]
        specific_plan_ids_limitation: list[str]
        unique_offer_id: str
        update_suppressed_due_idempotence: bool


    class azure.mgmt.marketplace.types.Plan(TypedDict, total=False):
        key "accessibility": Union[str, Accessibility]
        key "altStackReference": str
        key "isStopSell": bool
        key "planDisplayName": str
        key "planId": str
        key "skuId": str
        key "stackType": str
        accessibility: Union[str, Accessibility]
        alt_stack_reference: str
        is_stop_sell: bool
        plan_display_name: str
        plan_id: str
        sku_id: str
        stack_type: str


    class azure.mgmt.marketplace.types.PlanDetails(TypedDict, total=False):
        key "justification": str
        key "planId": str
        key "requestDate": Any
        key "status": Union[str, Status]
        key "subscriptionId": str
        key "subscriptionName": str
        justification: str
        plan_id: str
        request_date: Any
        status: Union[str, Status]
        subscription_id: str
        subscription_name: str


    class azure.mgmt.marketplace.types.PlanRequesterDetails(TypedDict, total=False):
        key "planDisplayName": str
        key "planId": str
        plan_display_name: str
        plan_id: str
        requesters: list[UserRequestDetails]


    class azure.mgmt.marketplace.types.PrivateStore(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('PrivateStoreProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: PrivateStoreProperties
        system_data: SystemData
        type: str


    class azure.mgmt.marketplace.types.PrivateStoreProperties(TypedDict, total=False):
        key "availability": Union[str, Availability]
        key "eTag": str
        key "isGov": bool
        key "notificationsSettings": ForwardRef('NotificationsSettingsProperties', module='types')
        key "privateStoreId": str
        key "privateStoreName": str
        key "tenantId": str
        availability: Union[str, Availability]
        branding: dict[str, str]
        collectionIds: list[str]
        collection_ids: list[str]
        e_tag: str
        is_gov: bool
        notifications_settings: NotificationsSettingsProperties
        private_store_id: str
        private_store_name: str
        tenant_id: str


    class azure.mgmt.marketplace.types.ProxyResource(Resource):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.marketplace.types.QueryApprovedPlans(TypedDict, total=False):
        key "offerId": str
        offer_id: str
        planIds: list[str]
        plan_ids: list[str]
        subscriptionIds: list[str]
        subscription_ids: list[str]


    class azure.mgmt.marketplace.types.QueryApprovedPlansPayload(TypedDict, total=False):
        key "properties": ForwardRef('QueryApprovedPlans', module='types')
        properties: QueryApprovedPlans


    class azure.mgmt.marketplace.types.QueryRequestApprovalProperties(TypedDict, total=False):
        key "properties": ForwardRef('RequestDetails', module='types')
        properties: RequestDetails


    class azure.mgmt.marketplace.types.QueryUserOffersDetails(TypedDict, total=False):
        offerIds: list[str]
        offer_ids: list[str]
        subscriptionIds: list[str]
        subscription_ids: list[str]


    class azure.mgmt.marketplace.types.QueryUserOffersProperties(TypedDict, total=False):
        key "properties": ForwardRef('QueryUserOffersDetails', module='types')
        properties: QueryUserOffersDetails


    class azure.mgmt.marketplace.types.QueryUserRulesDetails(TypedDict, total=False):
        subscriptionIds: list[str]
        subscription_ids: list[str]


    class azure.mgmt.marketplace.types.QueryUserRulesProperties(TypedDict, total=False):
        key "properties": ForwardRef('QueryUserRulesDetails', module='types')
        properties: QueryUserRulesDetails


    class azure.mgmt.marketplace.types.Recipient(TypedDict, total=False):
        key "displayName": str
        key "emailAddress": str
        key "principalId": str
        display_name: str
        email_address: str
        principal_id: str


    class azure.mgmt.marketplace.types.RequestApprovalProperties(TypedDict, total=False):
        key "isClosed": bool
        key "messageCode": int
        key "offerDisplayName": str
        key "offerId": str
        key "publisherId": str
        is_closed: bool
        message_code: int
        offer_display_name: str
        offer_id: str
        plansDetails: list[PlanDetails]
        plans_details: list[PlanDetails]
        publisher_id: str


    class azure.mgmt.marketplace.types.RequestApprovalResource(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('RequestApprovalProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: RequestApprovalProperties
        system_data: SystemData
        type: str


    class azure.mgmt.marketplace.types.RequestDetails(TypedDict, total=False):
        key "publisherId": str
        key "subscriptionId": str
        planIds: list[str]
        plan_ids: list[str]
        publisher_id: str
        subscription_id: str


    class azure.mgmt.marketplace.types.Resource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.marketplace.types.Rule(TypedDict, total=False):
        key "type": Union[str, RuleType]
        type: Union[str, RuleType]
        value: list[str]


    class azure.mgmt.marketplace.types.SetRulesRequest(TypedDict, total=False):
        key "nextLink": str
        next_link: str
        value: list[Rule]


    class azure.mgmt.marketplace.types.StopSellSubscriptions(TypedDict, total=False):
        subscriptions: list[str]


    class azure.mgmt.marketplace.types.SystemData(TypedDict, total=False):
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


    class azure.mgmt.marketplace.types.TransferOffersDetails(TypedDict, total=False):
        key "operation": str
        offerIdsList: list[str]
        offer_ids_list: list[str]
        operation: str
        targetCollections: list[str]
        target_collections: list[str]


    class azure.mgmt.marketplace.types.TransferOffersProperties(TypedDict, total=False):
        key "properties": ForwardRef('TransferOffersDetails', module='types')
        properties: TransferOffersDetails


    class azure.mgmt.marketplace.types.UserRequestDetails(TypedDict, total=False):
        key "date": str
        key "justification": str
        key "subscriptionId": str
        key "subscriptionName": str
        key "user": str
        date: str
        justification: str
        subscription_id: str
        subscription_name: str
        user: str


    class azure.mgmt.marketplace.types.WithdrawDetails(TypedDict, total=False):
        key "planId": str
        key "publisherId": str
        plan_id: str
        publisher_id: str


    class azure.mgmt.marketplace.types.WithdrawProperties(TypedDict, total=False):
        key "properties": ForwardRef('WithdrawDetails', module='types')
        properties: WithdrawDetails


```