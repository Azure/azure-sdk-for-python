```py
namespace azure.mgmt.quota

    class azure.mgmt.quota.QuotaMgmtClient: implements ContextManager 
        group_quota_limits: GroupQuotaLimitsOperations
        group_quota_limits_request: GroupQuotaLimitsRequestOperations
        group_quota_location_settings: GroupQuotaLocationSettingsOperations
        group_quota_subscription_allocation: GroupQuotaSubscriptionAllocationOperations
        group_quota_subscription_allocation_request: GroupQuotaSubscriptionAllocationRequestOperations
        group_quota_subscription_requests: GroupQuotaSubscriptionRequestsOperations
        group_quota_subscriptions: GroupQuotaSubscriptionsOperations
        group_quota_usages: GroupQuotaUsagesOperations
        group_quotas: GroupQuotasOperations
        incoming_quota_transfers: IncomingQuotaTransfersOperations
        quota: QuotaOperations
        quota_operation: QuotaOperationOperations
        quota_request_status: QuotaRequestStatusOperations
        quota_transfers: QuotaTransfersOperations
        usages: UsagesOperations

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


namespace azure.mgmt.quota.aio

    class azure.mgmt.quota.aio.QuotaMgmtClient: implements AsyncContextManager 
        group_quota_limits: GroupQuotaLimitsOperations
        group_quota_limits_request: GroupQuotaLimitsRequestOperations
        group_quota_location_settings: GroupQuotaLocationSettingsOperations
        group_quota_subscription_allocation: GroupQuotaSubscriptionAllocationOperations
        group_quota_subscription_allocation_request: GroupQuotaSubscriptionAllocationRequestOperations
        group_quota_subscription_requests: GroupQuotaSubscriptionRequestsOperations
        group_quota_subscriptions: GroupQuotaSubscriptionsOperations
        group_quota_usages: GroupQuotaUsagesOperations
        group_quotas: GroupQuotasOperations
        incoming_quota_transfers: IncomingQuotaTransfersOperations
        quota: QuotaOperations
        quota_operation: QuotaOperationOperations
        quota_request_status: QuotaRequestStatusOperations
        quota_transfers: QuotaTransfersOperations
        usages: UsagesOperations

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


namespace azure.mgmt.quota.aio.operations

    class azure.mgmt.quota.aio.operations.GroupQuotaLimitsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def list(
                self, 
                management_group_id: str, 
                group_quota_name: str, 
                resource_provider_name: str, 
                location: str, 
                **kwargs: Any
            ) -> GroupQuotaLimitList: ...


    class azure.mgmt.quota.aio.operations.GroupQuotaLimitsRequestOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_update(
                self, 
                management_group_id: str, 
                group_quota_name: str, 
                resource_provider_name: str, 
                location: str, 
                group_quota_request: Optional[GroupQuotaLimitList] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GroupQuotaLimitList]: ...

        @overload
        async def begin_update(
                self, 
                management_group_id: str, 
                group_quota_name: str, 
                resource_provider_name: str, 
                location: str, 
                group_quota_request: Optional[GroupQuotaLimitList] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GroupQuotaLimitList]: ...

        @overload
        async def begin_update(
                self, 
                management_group_id: str, 
                group_quota_name: str, 
                resource_provider_name: str, 
                location: str, 
                group_quota_request: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GroupQuotaLimitList]: ...

        @distributed_trace_async
        async def get(
                self, 
                management_group_id: str, 
                group_quota_name: str, 
                request_id_parameter: str, 
                **kwargs: Any
            ) -> SubmittedResourceRequestStatus: ...

        @distributed_trace
        def list(
                self, 
                management_group_id: str, 
                group_quota_name: str, 
                resource_provider_name: str, 
                *, 
                filter: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[SubmittedResourceRequestStatus]: ...


    class azure.mgmt.quota.aio.operations.GroupQuotaLocationSettingsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                management_group_id: str, 
                group_quota_name: str, 
                resource_provider_name: str, 
                location: str, 
                location_settings: Optional[GroupQuotasEnforcementStatus] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GroupQuotasEnforcementStatus]: ...

        @overload
        async def begin_create_or_update(
                self, 
                management_group_id: str, 
                group_quota_name: str, 
                resource_provider_name: str, 
                location: str, 
                location_settings: Optional[GroupQuotasEnforcementStatus] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GroupQuotasEnforcementStatus]: ...

        @overload
        async def begin_create_or_update(
                self, 
                management_group_id: str, 
                group_quota_name: str, 
                resource_provider_name: str, 
                location: str, 
                location_settings: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GroupQuotasEnforcementStatus]: ...

        @overload
        async def begin_update(
                self, 
                management_group_id: str, 
                group_quota_name: str, 
                resource_provider_name: str, 
                location: str, 
                location_settings: Optional[GroupQuotasEnforcementStatus] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GroupQuotasEnforcementStatus]: ...

        @overload
        async def begin_update(
                self, 
                management_group_id: str, 
                group_quota_name: str, 
                resource_provider_name: str, 
                location: str, 
                location_settings: Optional[GroupQuotasEnforcementStatus] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GroupQuotasEnforcementStatus]: ...

        @overload
        async def begin_update(
                self, 
                management_group_id: str, 
                group_quota_name: str, 
                resource_provider_name: str, 
                location: str, 
                location_settings: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GroupQuotasEnforcementStatus]: ...

        @distributed_trace_async
        async def get(
                self, 
                management_group_id: str, 
                group_quota_name: str, 
                resource_provider_name: str, 
                location: str, 
                **kwargs: Any
            ) -> GroupQuotasEnforcementStatus: ...


    class azure.mgmt.quota.aio.operations.GroupQuotaSubscriptionAllocationOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def list(
                self, 
                management_group_id: str, 
                group_quota_name: str, 
                resource_provider_name: str, 
                location: str, 
                **kwargs: Any
            ) -> SubscriptionQuotaAllocationsList: ...


    class azure.mgmt.quota.aio.operations.GroupQuotaSubscriptionAllocationRequestOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_update(
                self, 
                management_group_id: str, 
                group_quota_name: str, 
                resource_provider_name: str, 
                location: str, 
                allocate_quota_request: SubscriptionQuotaAllocationsList, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SubscriptionQuotaAllocationsList]: ...

        @overload
        async def begin_update(
                self, 
                management_group_id: str, 
                group_quota_name: str, 
                resource_provider_name: str, 
                location: str, 
                allocate_quota_request: SubscriptionQuotaAllocationsList, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SubscriptionQuotaAllocationsList]: ...

        @overload
        async def begin_update(
                self, 
                management_group_id: str, 
                group_quota_name: str, 
                resource_provider_name: str, 
                location: str, 
                allocate_quota_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SubscriptionQuotaAllocationsList]: ...

        @distributed_trace_async
        async def get(
                self, 
                management_group_id: str, 
                group_quota_name: str, 
                resource_provider_name: str, 
                allocation_id: str, 
                **kwargs: Any
            ) -> QuotaAllocationRequestStatus: ...

        @distributed_trace
        def list(
                self, 
                management_group_id: str, 
                group_quota_name: str, 
                resource_provider_name: str, 
                *, 
                filter: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[QuotaAllocationRequestStatus]: ...


    class azure.mgmt.quota.aio.operations.GroupQuotaSubscriptionRequestsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                management_group_id: str, 
                group_quota_name: str, 
                request_id_parameter: str, 
                **kwargs: Any
            ) -> GroupQuotaSubscriptionRequestStatus: ...

        @distributed_trace
        def list(
                self, 
                management_group_id: str, 
                group_quota_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[GroupQuotaSubscriptionRequestStatus]: ...


    class azure.mgmt.quota.aio.operations.GroupQuotaSubscriptionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_create_or_update(
                self, 
                management_group_id: str, 
                group_quota_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[GroupQuotaSubscriptionId]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                management_group_id: str, 
                group_quota_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_update(
                self, 
                management_group_id: str, 
                group_quota_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[GroupQuotaSubscriptionId]: ...

        @distributed_trace_async
        async def get(
                self, 
                management_group_id: str, 
                group_quota_name: str, 
                **kwargs: Any
            ) -> GroupQuotaSubscriptionId: ...

        @distributed_trace
        def list(
                self, 
                management_group_id: str, 
                group_quota_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[GroupQuotaSubscriptionId]: ...


    class azure.mgmt.quota.aio.operations.GroupQuotaUsagesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                management_group_id: str, 
                group_quota_name: str, 
                resource_provider_name: str, 
                location: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ResourceUsages]: ...


    class azure.mgmt.quota.aio.operations.GroupQuotasOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                management_group_id: str, 
                group_quota_name: str, 
                group_quota_put_request_body: Optional[GroupQuotasEntity] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GroupQuotasEntity]: ...

        @overload
        async def begin_create_or_update(
                self, 
                management_group_id: str, 
                group_quota_name: str, 
                group_quota_put_request_body: Optional[GroupQuotasEntity] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GroupQuotasEntity]: ...

        @overload
        async def begin_create_or_update(
                self, 
                management_group_id: str, 
                group_quota_name: str, 
                group_quota_put_request_body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GroupQuotasEntity]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                management_group_id: str, 
                group_quota_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                management_group_id: str, 
                group_quota_name: str, 
                group_quotas_patch_request_body: Optional[GroupQuotasEntityPatch] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GroupQuotasEntity]: ...

        @overload
        async def begin_update(
                self, 
                management_group_id: str, 
                group_quota_name: str, 
                group_quotas_patch_request_body: Optional[GroupQuotasEntityPatch] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GroupQuotasEntity]: ...

        @overload
        async def begin_update(
                self, 
                management_group_id: str, 
                group_quota_name: str, 
                group_quotas_patch_request_body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GroupQuotasEntity]: ...

        @distributed_trace_async
        async def get(
                self, 
                management_group_id: str, 
                group_quota_name: str, 
                **kwargs: Any
            ) -> GroupQuotasEntity: ...

        @distributed_trace
        def list(
                self, 
                management_group_id: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[GroupQuotasEntity]: ...


    class azure.mgmt.quota.aio.operations.IncomingQuotaTransfersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_approve(
                self, 
                target_provider: str, 
                region: str, 
                transfer_id: str, 
                body: Optional[IncomingQuotaTransferApproveRequest] = None, 
                *, 
                content_type: str = "application/json", 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> AsyncLROPoller[IncomingQuotaTransfer]: ...

        @overload
        async def begin_approve(
                self, 
                target_provider: str, 
                region: str, 
                transfer_id: str, 
                body: Optional[IncomingQuotaTransferApproveRequest] = None, 
                *, 
                content_type: str = "application/json", 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> AsyncLROPoller[IncomingQuotaTransfer]: ...

        @overload
        async def begin_approve(
                self, 
                target_provider: str, 
                region: str, 
                transfer_id: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> AsyncLROPoller[IncomingQuotaTransfer]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-09-01-preview', params_added_on={'2026-09-01-preview': ['api_version', 'subscription_id', 'target_provider', 'region', 'transfer_id', 'accept']}, api_versions_list=['2026-09-01-preview'])
        async def get(
                self, 
                target_provider: str, 
                region: str, 
                transfer_id: str, 
                **kwargs: Any
            ) -> IncomingQuotaTransfer: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-09-01-preview', params_added_on={'2026-09-01-preview': ['api_version', 'subscription_id', 'target_provider', 'region', 'accept']}, api_versions_list=['2026-09-01-preview'])
        def list(
                self, 
                target_provider: str, 
                region: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[IncomingQuotaTransfer]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-09-01-preview', params_added_on={'2026-09-01-preview': ['api_version', 'subscription_id', 'accept']}, api_versions_list=['2026-09-01-preview'])
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[IncomingQuotaTransfer]: ...

        @overload
        async def reject(
                self, 
                target_provider: str, 
                region: str, 
                transfer_id: str, 
                body: Optional[IncomingQuotaTransferRejectRequest] = None, 
                *, 
                content_type: str = "application/json", 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> IncomingQuotaTransfer: ...

        @overload
        async def reject(
                self, 
                target_provider: str, 
                region: str, 
                transfer_id: str, 
                body: Optional[IncomingQuotaTransferRejectRequest] = None, 
                *, 
                content_type: str = "application/json", 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> IncomingQuotaTransfer: ...

        @overload
        async def reject(
                self, 
                target_provider: str, 
                region: str, 
                transfer_id: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> IncomingQuotaTransfer: ...


    class azure.mgmt.quota.aio.operations.QuotaOperationOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[OperationResponse]: ...


    class azure.mgmt.quota.aio.operations.QuotaOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_name: str, 
                scope: str, 
                create_quota_request: CurrentQuotaLimitBase, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CurrentQuotaLimitBase]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_name: str, 
                scope: str, 
                create_quota_request: CurrentQuotaLimitBase, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CurrentQuotaLimitBase]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_name: str, 
                scope: str, 
                create_quota_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CurrentQuotaLimitBase]: ...

        @overload
        async def begin_update(
                self, 
                resource_name: str, 
                scope: str, 
                create_quota_request: CurrentQuotaLimitBase, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CurrentQuotaLimitBase]: ...

        @overload
        async def begin_update(
                self, 
                resource_name: str, 
                scope: str, 
                create_quota_request: CurrentQuotaLimitBase, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CurrentQuotaLimitBase]: ...

        @overload
        async def begin_update(
                self, 
                resource_name: str, 
                scope: str, 
                create_quota_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CurrentQuotaLimitBase]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_name: str, 
                scope: str, 
                **kwargs: Any
            ) -> CurrentQuotaLimitBase: ...

        @distributed_trace
        def list(
                self, 
                scope: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[CurrentQuotaLimitBase]: ...


    class azure.mgmt.quota.aio.operations.QuotaRequestStatusOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                id: str, 
                scope: str, 
                **kwargs: Any
            ) -> QuotaRequestDetails: ...

        @distributed_trace
        def list(
                self, 
                scope: str, 
                *, 
                filter: Optional[str] = ..., 
                skiptoken: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[QuotaRequestDetails]: ...


    class azure.mgmt.quota.aio.operations.QuotaTransfersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                target_provider: str, 
                region: str, 
                transfer_name: str, 
                resource: QuotaTransfer, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[QuotaTransfer]: ...

        @overload
        async def begin_create_or_update(
                self, 
                target_provider: str, 
                region: str, 
                transfer_name: str, 
                resource: QuotaTransfer, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[QuotaTransfer]: ...

        @overload
        async def begin_create_or_update(
                self, 
                target_provider: str, 
                region: str, 
                transfer_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[QuotaTransfer]: ...

        @overload
        async def cancel(
                self, 
                target_provider: str, 
                region: str, 
                transfer_name: str, 
                body: Optional[QuotaTransferCancelRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> QuotaTransfer: ...

        @overload
        async def cancel(
                self, 
                target_provider: str, 
                region: str, 
                transfer_name: str, 
                body: Optional[QuotaTransferCancelRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> QuotaTransfer: ...

        @overload
        async def cancel(
                self, 
                target_provider: str, 
                region: str, 
                transfer_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> QuotaTransfer: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-09-01-preview', params_added_on={'2026-09-01-preview': ['api_version', 'subscription_id', 'target_provider', 'region', 'transfer_name']}, api_versions_list=['2026-09-01-preview'])
        async def delete(
                self, 
                target_provider: str, 
                region: str, 
                transfer_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-09-01-preview', params_added_on={'2026-09-01-preview': ['api_version', 'subscription_id', 'target_provider', 'region', 'transfer_name', 'accept']}, api_versions_list=['2026-09-01-preview'])
        async def get(
                self, 
                target_provider: str, 
                region: str, 
                transfer_name: str, 
                **kwargs: Any
            ) -> QuotaTransfer: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-09-01-preview', params_added_on={'2026-09-01-preview': ['api_version', 'subscription_id', 'target_provider', 'region', 'accept']}, api_versions_list=['2026-09-01-preview'])
        def list(
                self, 
                target_provider: str, 
                region: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[QuotaTransfer]: ...


    class azure.mgmt.quota.aio.operations.UsagesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_name: str, 
                scope: str, 
                **kwargs: Any
            ) -> CurrentUsagesBase: ...

        @distributed_trace
        def list(
                self, 
                scope: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[CurrentUsagesBase]: ...


namespace azure.mgmt.quota.models

    class azure.mgmt.quota.models.AllocatedQuotaToSubscriptionList(_Model):
        value: Optional[list[AllocatedToSubscription]]

        @overload
        def __init__(
                self, 
                *, 
                value: Optional[list[AllocatedToSubscription]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.quota.models.AllocatedToSubscription(_Model):
        quota_allocated: Optional[int]
        subscription_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                quota_allocated: Optional[int] = ..., 
                subscription_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.quota.models.ApprovalRecord(_Model):
        actor: str
        comment: Optional[str]
        occurred_at: datetime

        @overload
        def __init__(
                self, 
                *, 
                actor: str, 
                comment: Optional[str] = ..., 
                occurred_at: datetime
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.quota.models.CancellationRecord(_Model):
        actor: str
        occurred_at: datetime
        reason: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                actor: str, 
                occurred_at: datetime, 
                reason: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.quota.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.quota.models.CurrentQuotaLimitBase(ExtensionResource):
        id: str
        name: str
        properties: Optional[QuotaProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[QuotaProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.quota.models.CurrentUsagesBase(ExtensionResource):
        id: str
        name: str
        properties: Optional[UsagesProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[UsagesProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.quota.models.EnforcementState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"
        NOT_AVAILABLE = "NotAvailable"


    class azure.mgmt.quota.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.quota.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.quota.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.quota.models.ExceptionResponse(_Model):
        error: Optional[ServiceError]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ServiceError] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.quota.models.ExtensionResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.quota.models.GroupQuotaDetails(_Model):
        allocated_to_subscriptions: Optional[AllocatedQuotaToSubscriptionList]
        available_limit: Optional[int]
        comment: Optional[str]
        limit: Optional[int]
        name: Optional[GroupQuotaDetailsName]
        resource_name: Optional[str]
        unit: Optional[str]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                comment: Optional[str] = ..., 
                limit: Optional[int] = ..., 
                resource_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.quota.models.GroupQuotaDetailsName(_Model):
        localized_value: Optional[str]
        value: Optional[str]


    class azure.mgmt.quota.models.GroupQuotaLimit(_Model):
        properties: Optional[GroupQuotaLimitProperties]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[GroupQuotaLimitProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.quota.models.GroupQuotaLimitList(ProxyResource):
        id: str
        name: str
        properties: Optional[GroupQuotaLimitListProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[GroupQuotaLimitListProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.quota.models.GroupQuotaLimitListProperties(_Model):
        next_link: Optional[str]
        provisioning_state: Optional[Union[str, RequestState]]
        value: Optional[list[GroupQuotaLimit]]

        @overload
        def __init__(
                self, 
                *, 
                value: Optional[list[GroupQuotaLimit]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.quota.models.GroupQuotaLimitProperties(GroupQuotaDetails):
        allocated_to_subscriptions: AllocatedQuotaToSubscriptionList
        available_limit: int
        comment: str
        limit: int
        name: GroupQuotaDetailsName
        resource_name: str
        unit: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                comment: Optional[str] = ..., 
                limit: Optional[int] = ..., 
                resource_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.quota.models.GroupQuotaRequestBase(_Model):
        properties: Optional[GroupQuotaRequestBaseProperties]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[GroupQuotaRequestBaseProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.quota.models.GroupQuotaRequestBaseProperties(_Model):
        comments: Optional[str]
        limit: Optional[int]
        name: Optional[GroupQuotaRequestBasePropertiesName]
        region: Optional[str]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                comments: Optional[str] = ..., 
                limit: Optional[int] = ..., 
                region: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.quota.models.GroupQuotaRequestBasePropertiesName(_Model):
        localized_value: Optional[str]
        value: Optional[str]


    class azure.mgmt.quota.models.GroupQuotaSubscriptionId(ProxyResource):
        id: str
        name: str
        properties: Optional[GroupQuotaSubscriptionIdProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[GroupQuotaSubscriptionIdProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.quota.models.GroupQuotaSubscriptionIdProperties(_Model):
        provisioning_state: Optional[Union[str, RequestState]]
        subscription_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                subscription_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.quota.models.GroupQuotaSubscriptionRequestStatus(ProxyResource):
        id: str
        name: str
        properties: Optional[GroupQuotaSubscriptionRequestStatusProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[GroupQuotaSubscriptionRequestStatusProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.quota.models.GroupQuotaSubscriptionRequestStatusProperties(_Model):
        provisioning_state: Optional[Union[str, RequestState]]
        request_submit_time: Optional[datetime]
        subscription_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                request_submit_time: Optional[datetime] = ..., 
                subscription_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.quota.models.GroupQuotaUsagesBase(_Model):
        limit: Optional[int]
        name: Optional[GroupQuotaUsagesBaseName]
        unit: Optional[str]
        usages: Optional[int]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                limit: Optional[int] = ..., 
                name: Optional[GroupQuotaUsagesBaseName] = ..., 
                usages: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.quota.models.GroupQuotaUsagesBaseName(_Model):
        localized_value: Optional[str]
        value: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                value: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.quota.models.GroupQuotasEnforcementStatus(ProxyResource):
        id: str
        name: str
        properties: Optional[GroupQuotasEnforcementStatusProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[GroupQuotasEnforcementStatusProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.quota.models.GroupQuotasEnforcementStatusProperties(_Model):
        enforced_group_name: Optional[str]
        enforcement_enabled: Optional[Union[str, EnforcementState]]
        fault_code: Optional[str]
        provisioning_state: Optional[Union[str, RequestState]]

        @overload
        def __init__(
                self, 
                *, 
                enforcement_enabled: Optional[Union[str, EnforcementState]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.quota.models.GroupQuotasEntity(ExtensionResource):
        id: str
        name: str
        properties: Optional[GroupQuotasEntityProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[GroupQuotasEntityProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.quota.models.GroupQuotasEntityBase(_Model):
        display_name: Optional[str]
        group_type: Optional[Union[str, GroupType]]
        provisioning_state: Optional[Union[str, RequestState]]

        @overload
        def __init__(
                self, 
                *, 
                display_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.quota.models.GroupQuotasEntityBasePatch(_Model):
        display_name: Optional[str]
        provisioning_state: Optional[Union[str, RequestState]]

        @overload
        def __init__(
                self, 
                *, 
                display_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.quota.models.GroupQuotasEntityPatch(ProxyResource):
        id: str
        name: str
        properties: Optional[GroupQuotasEntityPatchProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[GroupQuotasEntityPatchProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.quota.models.GroupQuotasEntityPatchProperties(GroupQuotasEntityBasePatch):
        display_name: str
        provisioning_state: Union[str, RequestState]

        @overload
        def __init__(
                self, 
                *, 
                display_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.quota.models.GroupQuotasEntityProperties(GroupQuotasEntityBase):
        display_name: str
        group_type: Union[str, GroupType]
        provisioning_state: Union[str, RequestState]

        @overload
        def __init__(
                self, 
                *, 
                display_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.quota.models.GroupType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALLOCATION_GROUP = "AllocationGroup"
        ENFORCED_GROUP = "EnforcedGroup"


    class azure.mgmt.quota.models.IncomingQuotaTransfer(ProxyResource):
        etag: Optional[str]
        id: str
        name: str
        properties: Optional[IncomingQuotaTransferProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[IncomingQuotaTransferProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.quota.models.IncomingQuotaTransferApproveRequest(_Model):
        comment: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                comment: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.quota.models.IncomingQuotaTransferProperties(_Model):
        amount: Optional[int]
        approval: Optional[ApprovalRecord]
        billing_account_id: Optional[str]
        provisioning_state: Optional[Union[str, TransferProvisioningState]]
        rejection: Optional[RejectionRecord]
        resource_name: Optional[str]
        source_etag: Optional[str]
        source_subscription_id: Optional[str]
        source_tenant_id: Optional[str]
        transfer_id: Optional[str]
        transfer_ref: Optional[str]
        transfer_status: Optional[Union[str, TransferStatus]]


    class azure.mgmt.quota.models.IncomingQuotaTransferRejectRequest(_Model):
        reason: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                reason: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.quota.models.LimitJsonObject(_Model):
        limit_object_type: str

        @overload
        def __init__(
                self, 
                *, 
                limit_object_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.quota.models.LimitObject(LimitJsonObject, discriminator='LimitValue'):
        limit_object_type: Literal[LimitType.LIMIT_VALUE]
        limit_type: Optional[Union[str, QuotaLimitTypes]]
        value: int

        @overload
        def __init__(
                self, 
                *, 
                limit_type: Optional[Union[str, QuotaLimitTypes]] = ..., 
                value: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.quota.models.LimitType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LIMIT_VALUE = "LimitValue"


    class azure.mgmt.quota.models.OperationDisplay(_Model):
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


    class azure.mgmt.quota.models.OperationResponse(_Model):
        display: Optional[OperationDisplay]
        name: Optional[str]
        origin: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                display: Optional[OperationDisplay] = ..., 
                name: Optional[str] = ..., 
                origin: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.quota.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.quota.models.QuotaAllocationRequestBase(_Model):
        properties: Optional[QuotaAllocationRequestBaseProperties]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[QuotaAllocationRequestBaseProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.quota.models.QuotaAllocationRequestBaseProperties(_Model):
        limit: Optional[int]
        name: Optional[QuotaAllocationRequestBasePropertiesName]
        region: Optional[str]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                limit: Optional[int] = ..., 
                region: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.quota.models.QuotaAllocationRequestBasePropertiesName(_Model):
        localized_value: Optional[str]
        value: Optional[str]


    class azure.mgmt.quota.models.QuotaAllocationRequestStatus(ExtensionResource):
        id: str
        name: str
        properties: Optional[QuotaAllocationRequestStatusProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[QuotaAllocationRequestStatusProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.quota.models.QuotaAllocationRequestStatusProperties(_Model):
        fault_code: Optional[str]
        provisioning_state: Optional[Union[str, RequestState]]
        request_submit_time: Optional[datetime]
        requested_resource: Optional[QuotaAllocationRequestBase]

        @overload
        def __init__(
                self, 
                *, 
                requested_resource: Optional[QuotaAllocationRequestBase] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.quota.models.QuotaLimitTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INDEPENDENT = "Independent"
        SHARED = "Shared"


    class azure.mgmt.quota.models.QuotaProperties(_Model):
        is_quota_applicable: Optional[bool]
        limit: Optional[LimitJsonObject]
        name: Optional[ResourceName]
        properties: Optional[Any]
        quota_period: Optional[str]
        resource_type: Optional[str]
        unit: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                limit: Optional[LimitJsonObject] = ..., 
                name: Optional[ResourceName] = ..., 
                properties: Optional[Any] = ..., 
                resource_type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.quota.models.QuotaRequestDetails(ExtensionResource):
        id: str
        name: str
        properties: Optional[QuotaRequestProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[QuotaRequestProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.quota.models.QuotaRequestProperties(_Model):
        error: Optional[ServiceErrorDetail]
        message: Optional[str]
        provisioning_state: Optional[Union[str, QuotaRequestState]]
        request_submit_time: Optional[datetime]
        value: Optional[list[SubRequest]]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ServiceErrorDetail] = ..., 
                value: Optional[list[SubRequest]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.quota.models.QuotaRequestState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        FAILED = "Failed"
        INVALID = "Invalid"
        IN_PROGRESS = "InProgress"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.quota.models.QuotaTransfer(ProxyResource):
        etag: Optional[str]
        id: str
        name: str
        properties: Optional[QuotaTransferProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[QuotaTransferProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.quota.models.QuotaTransferCancelRequest(_Model):
        reason: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                reason: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.quota.models.QuotaTransferProperties(_Model):
        amount: int
        approval: Optional[ApprovalRecord]
        auto_approve: Optional[bool]
        billing_account_id: str
        cancellation: Optional[CancellationRecord]
        comment: Optional[str]
        created_at: Optional[datetime]
        created_by: Optional[str]
        destination_subscription_id: str
        destination_tenant_id: Optional[str]
        display_name: str
        expires_at: Optional[datetime]
        provisioning_state: Optional[Union[str, TransferProvisioningState]]
        resource_name: str
        transfer_id: Optional[str]
        transfer_status: Optional[Union[str, TransferStatus]]

        @overload
        def __init__(
                self, 
                *, 
                amount: int, 
                auto_approve: Optional[bool] = ..., 
                billing_account_id: str, 
                comment: Optional[str] = ..., 
                destination_subscription_id: str, 
                display_name: str, 
                resource_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.quota.models.RejectionRecord(_Model):
        actor: str
        occurred_at: datetime
        reason: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                actor: str, 
                occurred_at: datetime, 
                reason: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.quota.models.RequestState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        CANCELED = "Canceled"
        CREATED = "Created"
        ESCALATED = "Escalated"
        FAILED = "Failed"
        INVALID = "Invalid"
        IN_PROGRESS = "InProgress"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.quota.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.quota.models.ResourceName(_Model):
        localized_value: Optional[str]
        value: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                value: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.quota.models.ResourceUsages(ProxyResource):
        id: str
        name: str
        properties: Optional[GroupQuotaUsagesBase]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[GroupQuotaUsagesBase] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.quota.models.ServiceError(_Model):
        code: Optional[str]
        details: Optional[list[ServiceErrorDetail]]
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


    class azure.mgmt.quota.models.ServiceErrorDetail(_Model):
        code: Optional[str]
        message: Optional[str]


    class azure.mgmt.quota.models.SubRequest(_Model):
        limit: Optional[LimitJsonObject]
        message: Optional[str]
        name: Optional[ResourceName]
        provisioning_state: Optional[Union[str, QuotaRequestState]]
        resource_type: Optional[str]
        sub_request_id: Optional[str]
        unit: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                limit: Optional[LimitJsonObject] = ..., 
                name: Optional[ResourceName] = ..., 
                unit: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.quota.models.SubmittedResourceRequestStatus(ProxyResource):
        id: str
        name: str
        properties: Optional[SubmittedResourceRequestStatusProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SubmittedResourceRequestStatusProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.quota.models.SubmittedResourceRequestStatusProperties(_Model):
        fault_code: Optional[str]
        provisioning_state: Optional[Union[str, RequestState]]
        request_submit_time: Optional[datetime]
        requested_resource: Optional[GroupQuotaRequestBase]

        @overload
        def __init__(
                self, 
                *, 
                requested_resource: Optional[GroupQuotaRequestBase] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.quota.models.SubscriptionQuotaAllocations(_Model):
        properties: Optional[SubscriptionQuotaAllocationsProperties]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SubscriptionQuotaAllocationsProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.quota.models.SubscriptionQuotaAllocationsList(ExtensionResource):
        id: str
        name: str
        properties: Optional[SubscriptionQuotaAllocationsListProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SubscriptionQuotaAllocationsListProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.quota.models.SubscriptionQuotaAllocationsListProperties(_Model):
        next_link: Optional[str]
        provisioning_state: Optional[Union[str, RequestState]]
        value: Optional[list[SubscriptionQuotaAllocations]]

        @overload
        def __init__(
                self, 
                *, 
                value: Optional[list[SubscriptionQuotaAllocations]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.quota.models.SubscriptionQuotaAllocationsProperties(SubscriptionQuotaDetails):
        limit: int
        name: SubscriptionQuotaDetailsName
        resource_name: str
        shareable_quota: int

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                limit: Optional[int] = ..., 
                resource_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.quota.models.SubscriptionQuotaDetails(_Model):
        limit: Optional[int]
        name: Optional[SubscriptionQuotaDetailsName]
        resource_name: Optional[str]
        shareable_quota: Optional[int]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                limit: Optional[int] = ..., 
                resource_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.quota.models.SubscriptionQuotaDetailsName(_Model):
        localized_value: Optional[str]
        value: Optional[str]


    class azure.mgmt.quota.models.SystemData(_Model):
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


    class azure.mgmt.quota.models.TransferProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.quota.models.TransferStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        CANCELLED = "Cancelled"
        COMPLETED = "Completed"
        EXPIRED = "Expired"
        FAILED = "Failed"
        PENDING = "Pending"
        REJECTED = "Rejected"


    class azure.mgmt.quota.models.UsagesObject(_Model):
        usages_type: Optional[Union[str, UsagesTypes]]
        value: int

        @overload
        def __init__(
                self, 
                *, 
                usages_type: Optional[Union[str, UsagesTypes]] = ..., 
                value: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.quota.models.UsagesProperties(_Model):
        is_quota_applicable: Optional[bool]
        name: Optional[ResourceName]
        properties: Optional[Any]
        quota_period: Optional[str]
        resource_type: Optional[str]
        unit: Optional[str]
        usages: Optional[UsagesObject]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[ResourceName] = ..., 
                properties: Optional[Any] = ..., 
                resource_type: Optional[str] = ..., 
                usages: Optional[UsagesObject] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.quota.models.UsagesTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMBINED = "Combined"
        INDIVIDUAL = "Individual"


namespace azure.mgmt.quota.operations

    class azure.mgmt.quota.operations.GroupQuotaLimitsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                management_group_id: str, 
                group_quota_name: str, 
                resource_provider_name: str, 
                location: str, 
                **kwargs: Any
            ) -> GroupQuotaLimitList: ...


    class azure.mgmt.quota.operations.GroupQuotaLimitsRequestOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_update(
                self, 
                management_group_id: str, 
                group_quota_name: str, 
                resource_provider_name: str, 
                location: str, 
                group_quota_request: Optional[GroupQuotaLimitList] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GroupQuotaLimitList]: ...

        @overload
        def begin_update(
                self, 
                management_group_id: str, 
                group_quota_name: str, 
                resource_provider_name: str, 
                location: str, 
                group_quota_request: Optional[GroupQuotaLimitList] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GroupQuotaLimitList]: ...

        @overload
        def begin_update(
                self, 
                management_group_id: str, 
                group_quota_name: str, 
                resource_provider_name: str, 
                location: str, 
                group_quota_request: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GroupQuotaLimitList]: ...

        @distributed_trace
        def get(
                self, 
                management_group_id: str, 
                group_quota_name: str, 
                request_id_parameter: str, 
                **kwargs: Any
            ) -> SubmittedResourceRequestStatus: ...

        @distributed_trace
        def list(
                self, 
                management_group_id: str, 
                group_quota_name: str, 
                resource_provider_name: str, 
                *, 
                filter: str, 
                **kwargs: Any
            ) -> ItemPaged[SubmittedResourceRequestStatus]: ...


    class azure.mgmt.quota.operations.GroupQuotaLocationSettingsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                management_group_id: str, 
                group_quota_name: str, 
                resource_provider_name: str, 
                location: str, 
                location_settings: Optional[GroupQuotasEnforcementStatus] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GroupQuotasEnforcementStatus]: ...

        @overload
        def begin_create_or_update(
                self, 
                management_group_id: str, 
                group_quota_name: str, 
                resource_provider_name: str, 
                location: str, 
                location_settings: Optional[GroupQuotasEnforcementStatus] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GroupQuotasEnforcementStatus]: ...

        @overload
        def begin_create_or_update(
                self, 
                management_group_id: str, 
                group_quota_name: str, 
                resource_provider_name: str, 
                location: str, 
                location_settings: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GroupQuotasEnforcementStatus]: ...

        @overload
        def begin_update(
                self, 
                management_group_id: str, 
                group_quota_name: str, 
                resource_provider_name: str, 
                location: str, 
                location_settings: Optional[GroupQuotasEnforcementStatus] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GroupQuotasEnforcementStatus]: ...

        @overload
        def begin_update(
                self, 
                management_group_id: str, 
                group_quota_name: str, 
                resource_provider_name: str, 
                location: str, 
                location_settings: Optional[GroupQuotasEnforcementStatus] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GroupQuotasEnforcementStatus]: ...

        @overload
        def begin_update(
                self, 
                management_group_id: str, 
                group_quota_name: str, 
                resource_provider_name: str, 
                location: str, 
                location_settings: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GroupQuotasEnforcementStatus]: ...

        @distributed_trace
        def get(
                self, 
                management_group_id: str, 
                group_quota_name: str, 
                resource_provider_name: str, 
                location: str, 
                **kwargs: Any
            ) -> GroupQuotasEnforcementStatus: ...


    class azure.mgmt.quota.operations.GroupQuotaSubscriptionAllocationOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                management_group_id: str, 
                group_quota_name: str, 
                resource_provider_name: str, 
                location: str, 
                **kwargs: Any
            ) -> SubscriptionQuotaAllocationsList: ...


    class azure.mgmt.quota.operations.GroupQuotaSubscriptionAllocationRequestOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_update(
                self, 
                management_group_id: str, 
                group_quota_name: str, 
                resource_provider_name: str, 
                location: str, 
                allocate_quota_request: SubscriptionQuotaAllocationsList, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SubscriptionQuotaAllocationsList]: ...

        @overload
        def begin_update(
                self, 
                management_group_id: str, 
                group_quota_name: str, 
                resource_provider_name: str, 
                location: str, 
                allocate_quota_request: SubscriptionQuotaAllocationsList, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SubscriptionQuotaAllocationsList]: ...

        @overload
        def begin_update(
                self, 
                management_group_id: str, 
                group_quota_name: str, 
                resource_provider_name: str, 
                location: str, 
                allocate_quota_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SubscriptionQuotaAllocationsList]: ...

        @distributed_trace
        def get(
                self, 
                management_group_id: str, 
                group_quota_name: str, 
                resource_provider_name: str, 
                allocation_id: str, 
                **kwargs: Any
            ) -> QuotaAllocationRequestStatus: ...

        @distributed_trace
        def list(
                self, 
                management_group_id: str, 
                group_quota_name: str, 
                resource_provider_name: str, 
                *, 
                filter: str, 
                **kwargs: Any
            ) -> ItemPaged[QuotaAllocationRequestStatus]: ...


    class azure.mgmt.quota.operations.GroupQuotaSubscriptionRequestsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                management_group_id: str, 
                group_quota_name: str, 
                request_id_parameter: str, 
                **kwargs: Any
            ) -> GroupQuotaSubscriptionRequestStatus: ...

        @distributed_trace
        def list(
                self, 
                management_group_id: str, 
                group_quota_name: str, 
                **kwargs: Any
            ) -> ItemPaged[GroupQuotaSubscriptionRequestStatus]: ...


    class azure.mgmt.quota.operations.GroupQuotaSubscriptionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_create_or_update(
                self, 
                management_group_id: str, 
                group_quota_name: str, 
                **kwargs: Any
            ) -> LROPoller[GroupQuotaSubscriptionId]: ...

        @distributed_trace
        def begin_delete(
                self, 
                management_group_id: str, 
                group_quota_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_update(
                self, 
                management_group_id: str, 
                group_quota_name: str, 
                **kwargs: Any
            ) -> LROPoller[GroupQuotaSubscriptionId]: ...

        @distributed_trace
        def get(
                self, 
                management_group_id: str, 
                group_quota_name: str, 
                **kwargs: Any
            ) -> GroupQuotaSubscriptionId: ...

        @distributed_trace
        def list(
                self, 
                management_group_id: str, 
                group_quota_name: str, 
                **kwargs: Any
            ) -> ItemPaged[GroupQuotaSubscriptionId]: ...


    class azure.mgmt.quota.operations.GroupQuotaUsagesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                management_group_id: str, 
                group_quota_name: str, 
                resource_provider_name: str, 
                location: str, 
                **kwargs: Any
            ) -> ItemPaged[ResourceUsages]: ...


    class azure.mgmt.quota.operations.GroupQuotasOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                management_group_id: str, 
                group_quota_name: str, 
                group_quota_put_request_body: Optional[GroupQuotasEntity] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GroupQuotasEntity]: ...

        @overload
        def begin_create_or_update(
                self, 
                management_group_id: str, 
                group_quota_name: str, 
                group_quota_put_request_body: Optional[GroupQuotasEntity] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GroupQuotasEntity]: ...

        @overload
        def begin_create_or_update(
                self, 
                management_group_id: str, 
                group_quota_name: str, 
                group_quota_put_request_body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GroupQuotasEntity]: ...

        @distributed_trace
        def begin_delete(
                self, 
                management_group_id: str, 
                group_quota_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                management_group_id: str, 
                group_quota_name: str, 
                group_quotas_patch_request_body: Optional[GroupQuotasEntityPatch] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GroupQuotasEntity]: ...

        @overload
        def begin_update(
                self, 
                management_group_id: str, 
                group_quota_name: str, 
                group_quotas_patch_request_body: Optional[GroupQuotasEntityPatch] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GroupQuotasEntity]: ...

        @overload
        def begin_update(
                self, 
                management_group_id: str, 
                group_quota_name: str, 
                group_quotas_patch_request_body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GroupQuotasEntity]: ...

        @distributed_trace
        def get(
                self, 
                management_group_id: str, 
                group_quota_name: str, 
                **kwargs: Any
            ) -> GroupQuotasEntity: ...

        @distributed_trace
        def list(
                self, 
                management_group_id: str, 
                **kwargs: Any
            ) -> ItemPaged[GroupQuotasEntity]: ...


    class azure.mgmt.quota.operations.IncomingQuotaTransfersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_approve(
                self, 
                target_provider: str, 
                region: str, 
                transfer_id: str, 
                body: Optional[IncomingQuotaTransferApproveRequest] = None, 
                *, 
                content_type: str = "application/json", 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> LROPoller[IncomingQuotaTransfer]: ...

        @overload
        def begin_approve(
                self, 
                target_provider: str, 
                region: str, 
                transfer_id: str, 
                body: Optional[IncomingQuotaTransferApproveRequest] = None, 
                *, 
                content_type: str = "application/json", 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> LROPoller[IncomingQuotaTransfer]: ...

        @overload
        def begin_approve(
                self, 
                target_provider: str, 
                region: str, 
                transfer_id: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> LROPoller[IncomingQuotaTransfer]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-09-01-preview', params_added_on={'2026-09-01-preview': ['api_version', 'subscription_id', 'target_provider', 'region', 'transfer_id', 'accept']}, api_versions_list=['2026-09-01-preview'])
        def get(
                self, 
                target_provider: str, 
                region: str, 
                transfer_id: str, 
                **kwargs: Any
            ) -> IncomingQuotaTransfer: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-09-01-preview', params_added_on={'2026-09-01-preview': ['api_version', 'subscription_id', 'target_provider', 'region', 'accept']}, api_versions_list=['2026-09-01-preview'])
        def list(
                self, 
                target_provider: str, 
                region: str, 
                **kwargs: Any
            ) -> ItemPaged[IncomingQuotaTransfer]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-09-01-preview', params_added_on={'2026-09-01-preview': ['api_version', 'subscription_id', 'accept']}, api_versions_list=['2026-09-01-preview'])
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[IncomingQuotaTransfer]: ...

        @overload
        def reject(
                self, 
                target_provider: str, 
                region: str, 
                transfer_id: str, 
                body: Optional[IncomingQuotaTransferRejectRequest] = None, 
                *, 
                content_type: str = "application/json", 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> IncomingQuotaTransfer: ...

        @overload
        def reject(
                self, 
                target_provider: str, 
                region: str, 
                transfer_id: str, 
                body: Optional[IncomingQuotaTransferRejectRequest] = None, 
                *, 
                content_type: str = "application/json", 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> IncomingQuotaTransfer: ...

        @overload
        def reject(
                self, 
                target_provider: str, 
                region: str, 
                transfer_id: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> IncomingQuotaTransfer: ...


    class azure.mgmt.quota.operations.QuotaOperationOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[OperationResponse]: ...


    class azure.mgmt.quota.operations.QuotaOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_name: str, 
                scope: str, 
                create_quota_request: CurrentQuotaLimitBase, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CurrentQuotaLimitBase]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_name: str, 
                scope: str, 
                create_quota_request: CurrentQuotaLimitBase, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CurrentQuotaLimitBase]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_name: str, 
                scope: str, 
                create_quota_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CurrentQuotaLimitBase]: ...

        @overload
        def begin_update(
                self, 
                resource_name: str, 
                scope: str, 
                create_quota_request: CurrentQuotaLimitBase, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CurrentQuotaLimitBase]: ...

        @overload
        def begin_update(
                self, 
                resource_name: str, 
                scope: str, 
                create_quota_request: CurrentQuotaLimitBase, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CurrentQuotaLimitBase]: ...

        @overload
        def begin_update(
                self, 
                resource_name: str, 
                scope: str, 
                create_quota_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CurrentQuotaLimitBase]: ...

        @distributed_trace
        def get(
                self, 
                resource_name: str, 
                scope: str, 
                **kwargs: Any
            ) -> CurrentQuotaLimitBase: ...

        @distributed_trace
        def list(
                self, 
                scope: str, 
                **kwargs: Any
            ) -> ItemPaged[CurrentQuotaLimitBase]: ...


    class azure.mgmt.quota.operations.QuotaRequestStatusOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                id: str, 
                scope: str, 
                **kwargs: Any
            ) -> QuotaRequestDetails: ...

        @distributed_trace
        def list(
                self, 
                scope: str, 
                *, 
                filter: Optional[str] = ..., 
                skiptoken: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[QuotaRequestDetails]: ...


    class azure.mgmt.quota.operations.QuotaTransfersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                target_provider: str, 
                region: str, 
                transfer_name: str, 
                resource: QuotaTransfer, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[QuotaTransfer]: ...

        @overload
        def begin_create_or_update(
                self, 
                target_provider: str, 
                region: str, 
                transfer_name: str, 
                resource: QuotaTransfer, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[QuotaTransfer]: ...

        @overload
        def begin_create_or_update(
                self, 
                target_provider: str, 
                region: str, 
                transfer_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[QuotaTransfer]: ...

        @overload
        def cancel(
                self, 
                target_provider: str, 
                region: str, 
                transfer_name: str, 
                body: Optional[QuotaTransferCancelRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> QuotaTransfer: ...

        @overload
        def cancel(
                self, 
                target_provider: str, 
                region: str, 
                transfer_name: str, 
                body: Optional[QuotaTransferCancelRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> QuotaTransfer: ...

        @overload
        def cancel(
                self, 
                target_provider: str, 
                region: str, 
                transfer_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> QuotaTransfer: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-09-01-preview', params_added_on={'2026-09-01-preview': ['api_version', 'subscription_id', 'target_provider', 'region', 'transfer_name']}, api_versions_list=['2026-09-01-preview'])
        def delete(
                self, 
                target_provider: str, 
                region: str, 
                transfer_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-09-01-preview', params_added_on={'2026-09-01-preview': ['api_version', 'subscription_id', 'target_provider', 'region', 'transfer_name', 'accept']}, api_versions_list=['2026-09-01-preview'])
        def get(
                self, 
                target_provider: str, 
                region: str, 
                transfer_name: str, 
                **kwargs: Any
            ) -> QuotaTransfer: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-09-01-preview', params_added_on={'2026-09-01-preview': ['api_version', 'subscription_id', 'target_provider', 'region', 'accept']}, api_versions_list=['2026-09-01-preview'])
        def list(
                self, 
                target_provider: str, 
                region: str, 
                **kwargs: Any
            ) -> ItemPaged[QuotaTransfer]: ...


    class azure.mgmt.quota.operations.UsagesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_name: str, 
                scope: str, 
                **kwargs: Any
            ) -> CurrentUsagesBase: ...

        @distributed_trace
        def list(
                self, 
                scope: str, 
                **kwargs: Any
            ) -> ItemPaged[CurrentUsagesBase]: ...


namespace azure.mgmt.quota.types

    class azure.mgmt.quota.types.AllocatedQuotaToSubscriptionList(TypedDict, total=False):
        value: list[AllocatedToSubscription]


    class azure.mgmt.quota.types.AllocatedToSubscription(TypedDict, total=False):
        key "quotaAllocated": int
        key "subscriptionId": str
        quotaAllocated: int
        subscriptionId: str


    class azure.mgmt.quota.types.ApprovalRecord(TypedDict, total=False):
        key "actor": Required[str]
        key "comment": str
        key "occurredAt": Required[str]
        actor: str
        comment: str
        occurredAt: str


    class azure.mgmt.quota.types.CancellationRecord(TypedDict, total=False):
        key "actor": Required[str]
        key "occurredAt": Required[str]
        key "reason": str
        actor: str
        occurredAt: str
        reason: str


    class azure.mgmt.quota.types.CurrentQuotaLimitBase(ExtensionResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('QuotaProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: QuotaProperties
        systemData: SystemData
        type: str


    class azure.mgmt.quota.types.ExtensionResource(Resource):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        systemData: SystemData
        type: str


    class azure.mgmt.quota.types.GroupQuotaDetails(TypedDict, total=False):
        key "allocatedToSubscriptions": ForwardRef('AllocatedQuotaToSubscriptionList', module='types')
        key "availableLimit": int
        key "comment": str
        key "limit": int
        key "name": ForwardRef('GroupQuotaDetailsName', module='types')
        key "resourceName": str
        key "unit": str
        allocatedToSubscriptions: AllocatedQuotaToSubscriptionList
        availableLimit: int
        comment: str
        limit: int
        name: GroupQuotaDetailsName
        resourceName: str
        unit: str


    class azure.mgmt.quota.types.GroupQuotaDetailsName(TypedDict, total=False):
        key "localizedValue": str
        key "value": str
        localizedValue: str
        value: str


    class azure.mgmt.quota.types.GroupQuotaLimit(TypedDict, total=False):
        key "properties": ForwardRef('GroupQuotaLimitProperties', module='types')
        properties: GroupQuotaLimitProperties


    class azure.mgmt.quota.types.GroupQuotaLimitList(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('GroupQuotaLimitListProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: GroupQuotaLimitListProperties
        systemData: SystemData
        type: str


    class azure.mgmt.quota.types.GroupQuotaLimitListProperties(TypedDict, total=False):
        key "nextLink": str
        key "provisioningState": Union[str, RequestState]
        nextLink: str
        provisioningState: Union[str, RequestState]
        value: list[GroupQuotaLimit]


    class azure.mgmt.quota.types.GroupQuotaLimitProperties(GroupQuotaDetails):
        key "allocatedToSubscriptions": ForwardRef('AllocatedQuotaToSubscriptionList', module='types')
        key "availableLimit": int
        key "comment": str
        key "limit": int
        key "name": ForwardRef('GroupQuotaDetailsName', module='types')
        key "resourceName": str
        key "unit": str
        allocatedToSubscriptions: AllocatedQuotaToSubscriptionList
        availableLimit: int
        comment: str
        limit: int
        name: GroupQuotaDetailsName
        resourceName: str
        unit: str


    class azure.mgmt.quota.types.GroupQuotasEnforcementStatus(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('GroupQuotasEnforcementStatusProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: GroupQuotasEnforcementStatusProperties
        systemData: SystemData
        type: str


    class azure.mgmt.quota.types.GroupQuotasEnforcementStatusProperties(TypedDict, total=False):
        key "enforcedGroupName": str
        key "enforcementEnabled": Union[str, EnforcementState]
        key "faultCode": str
        key "provisioningState": Union[str, RequestState]
        enforcedGroupName: str
        enforcementEnabled: Union[str, EnforcementState]
        faultCode: str
        provisioningState: Union[str, RequestState]


    class azure.mgmt.quota.types.GroupQuotasEntity(ExtensionResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('GroupQuotasEntityProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: GroupQuotasEntityProperties
        systemData: SystemData
        type: str


    class azure.mgmt.quota.types.GroupQuotasEntityBase(TypedDict, total=False):
        key "displayName": str
        key "groupType": Union[str, GroupType]
        key "provisioningState": Union[str, RequestState]
        displayName: str
        groupType: Union[str, GroupType]
        provisioningState: Union[str, RequestState]


    class azure.mgmt.quota.types.GroupQuotasEntityBasePatch(TypedDict, total=False):
        key "displayName": str
        key "provisioningState": Union[str, RequestState]
        displayName: str
        provisioningState: Union[str, RequestState]


    class azure.mgmt.quota.types.GroupQuotasEntityPatch(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('GroupQuotasEntityPatchProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: GroupQuotasEntityPatchProperties
        systemData: SystemData
        type: str


    class azure.mgmt.quota.types.GroupQuotasEntityPatchProperties(GroupQuotasEntityBasePatch):
        key "displayName": str
        key "provisioningState": Union[str, RequestState]
        displayName: str
        provisioningState: Union[str, RequestState]


    class azure.mgmt.quota.types.GroupQuotasEntityProperties(GroupQuotasEntityBase):
        key "displayName": str
        key "groupType": Union[str, GroupType]
        key "provisioningState": Union[str, RequestState]
        displayName: str
        groupType: Union[str, GroupType]
        provisioningState: Union[str, RequestState]


    class azure.mgmt.quota.types.IncomingQuotaTransferApproveRequest(TypedDict, total=False):
        key "comment": str
        comment: str


    class azure.mgmt.quota.types.IncomingQuotaTransferRejectRequest(TypedDict, total=False):
        key "reason": str
        reason: str


    class azure.mgmt.quota.types.LimitJsonObject(TypedDict, total=False):
        key "limitObjectType": Required[Literal[LimitType.LIMIT_VALUE]]
        key "limitType": Union[str, QuotaLimitTypes]
        key "value": Required[int]
        limitObjectType: Literal[LimitType.LIMIT_VALUE]
        limitType: Union[str, QuotaLimitTypes]
        value: int


    class azure.mgmt.quota.types.LimitObject(TypedDict, total=False):
        key "limitObjectType": Required[Literal[LimitType.LIMIT_VALUE]]
        key "limitType": Union[str, QuotaLimitTypes]
        key "value": Required[int]
        limitObjectType: Literal[LimitType.LIMIT_VALUE]
        limitType: Union[str, QuotaLimitTypes]
        value: int


    class azure.mgmt.quota.types.LimitType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LIMIT_VALUE = "LimitValue"


    class azure.mgmt.quota.types.ProxyResource(Resource):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        systemData: SystemData
        type: str


    class azure.mgmt.quota.types.QuotaProperties(TypedDict, total=False):
        key "isQuotaApplicable": bool
        key "limit": ForwardRef('LimitJsonObject', module='types')
        key "name": ForwardRef('ResourceName', module='types')
        key "properties": Any
        key "quotaPeriod": str
        key "resourceType": str
        key "unit": str
        isQuotaApplicable: bool
        limit: LimitJsonObject
        name: ResourceName
        properties: Any
        quotaPeriod: str
        resourceType: str
        unit: str


    class azure.mgmt.quota.types.QuotaTransfer(ProxyResource):
        key "etag": str
        key "id": str
        key "name": str
        key "properties": ForwardRef('QuotaTransferProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        id: str
        name: str
        properties: QuotaTransferProperties
        systemData: SystemData
        type: str


    class azure.mgmt.quota.types.QuotaTransferCancelRequest(TypedDict, total=False):
        key "reason": str
        reason: str


    class azure.mgmt.quota.types.QuotaTransferProperties(TypedDict, total=False):
        key "amount": Required[int]
        key "approval": ForwardRef('ApprovalRecord', module='types')
        key "autoApprove": bool
        key "billingAccountId": Required[str]
        key "cancellation": ForwardRef('CancellationRecord', module='types')
        key "comment": str
        key "createdAt": str
        key "createdBy": str
        key "destinationSubscriptionId": Required[str]
        key "destinationTenantId": str
        key "displayName": Required[str]
        key "expiresAt": str
        key "provisioningState": Union[str, TransferProvisioningState]
        key "resourceName": Required[str]
        key "transferId": str
        key "transferStatus": Union[str, TransferStatus]
        amount: int
        approval: ApprovalRecord
        autoApprove: bool
        billingAccountId: str
        cancellation: CancellationRecord
        comment: str
        createdAt: str
        createdBy: str
        destinationSubscriptionId: str
        destinationTenantId: str
        displayName: str
        expiresAt: str
        provisioningState: Union[str, TransferProvisioningState]
        resourceName: str
        transferId: str
        transferStatus: Union[str, TransferStatus]


    class azure.mgmt.quota.types.Resource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        systemData: SystemData
        type: str


    class azure.mgmt.quota.types.ResourceName(TypedDict, total=False):
        key "localizedValue": str
        key "value": str
        localizedValue: str
        value: str


    class azure.mgmt.quota.types.SubscriptionQuotaAllocations(TypedDict, total=False):
        key "properties": ForwardRef('SubscriptionQuotaAllocationsProperties', module='types')
        properties: SubscriptionQuotaAllocationsProperties


    class azure.mgmt.quota.types.SubscriptionQuotaAllocationsList(ExtensionResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('SubscriptionQuotaAllocationsListProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: SubscriptionQuotaAllocationsListProperties
        systemData: SystemData
        type: str


    class azure.mgmt.quota.types.SubscriptionQuotaAllocationsListProperties(TypedDict, total=False):
        key "nextLink": str
        key "provisioningState": Union[str, RequestState]
        nextLink: str
        provisioningState: Union[str, RequestState]
        value: list[SubscriptionQuotaAllocations]


    class azure.mgmt.quota.types.SubscriptionQuotaAllocationsProperties(SubscriptionQuotaDetails):
        key "limit": int
        key "name": ForwardRef('SubscriptionQuotaDetailsName', module='types')
        key "resourceName": str
        key "shareableQuota": int
        limit: int
        name: SubscriptionQuotaDetailsName
        resourceName: str
        shareableQuota: int


    class azure.mgmt.quota.types.SubscriptionQuotaDetails(TypedDict, total=False):
        key "limit": int
        key "name": ForwardRef('SubscriptionQuotaDetailsName', module='types')
        key "resourceName": str
        key "shareableQuota": int
        limit: int
        name: SubscriptionQuotaDetailsName
        resourceName: str
        shareableQuota: int


    class azure.mgmt.quota.types.SubscriptionQuotaDetailsName(TypedDict, total=False):
        key "localizedValue": str
        key "value": str
        localizedValue: str
        value: str


    class azure.mgmt.quota.types.SystemData(TypedDict, total=False):
        key "createdAt": str
        key "createdBy": str
        key "createdByType": Union[str, CreatedByType]
        key "lastModifiedAt": str
        key "lastModifiedBy": str
        key "lastModifiedByType": Union[str, CreatedByType]
        createdAt: str
        createdBy: str
        createdByType: Union[str, CreatedByType]
        lastModifiedAt: str
        lastModifiedBy: str
        lastModifiedByType: Union[str, CreatedByType]


```