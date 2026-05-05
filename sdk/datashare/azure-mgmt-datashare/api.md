```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.datashare

    class azure.mgmt.datashare.DataShareManagementClient: implements ContextManager 
        accounts: AccountsOperations
        consumer_invitations: ConsumerInvitationsOperations
        consumer_source_data_sets: ConsumerSourceDataSetsOperations
        data_set_mappings: DataSetMappingsOperations
        data_sets: DataSetsOperations
        email_registrations: EmailRegistrationsOperations
        invitations: InvitationsOperations
        operations: Operations
        provider_share_subscriptions: ProviderShareSubscriptionsOperations
        share_subscriptions: ShareSubscriptionsOperations
        shares: SharesOperations
        synchronization_settings: SynchronizationSettingsOperations
        triggers: TriggersOperations

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


namespace azure.mgmt.datashare.aio

    class azure.mgmt.datashare.aio.DataShareManagementClient: implements AsyncContextManager 
        accounts: AccountsOperations
        consumer_invitations: ConsumerInvitationsOperations
        consumer_source_data_sets: ConsumerSourceDataSetsOperations
        data_set_mappings: DataSetMappingsOperations
        data_sets: DataSetsOperations
        email_registrations: EmailRegistrationsOperations
        invitations: InvitationsOperations
        operations: Operations
        provider_share_subscriptions: ProviderShareSubscriptionsOperations
        share_subscriptions: ShareSubscriptionsOperations
        shares: SharesOperations
        synchronization_settings: SynchronizationSettingsOperations
        triggers: TriggersOperations

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


namespace azure.mgmt.datashare.aio.operations

    class azure.mgmt.datashare.aio.operations.AccountsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                account: Account, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Account]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                account: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Account]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationResponse]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Account: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                skip_token: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[Account]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                skip_token: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[Account]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                account_update_parameters: AccountUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Account: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                account_update_parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Account: ...


    class azure.mgmt.datashare.aio.operations.ConsumerInvitationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                location: str, 
                invitation_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ConsumerInvitation: ...

        @distributed_trace
        def list_invitations(
                self, 
                skip_token: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[ConsumerInvitation]: ...

        @overload
        async def reject_invitation(
                self, 
                location: str, 
                invitation: ConsumerInvitation, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConsumerInvitation: ...

        @overload
        async def reject_invitation(
                self, 
                location: str, 
                invitation: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConsumerInvitation: ...


    class azure.mgmt.datashare.aio.operations.ConsumerSourceDataSetsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_by_share_subscription(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_subscription_name: str, 
                skip_token: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[ConsumerSourceDataSet]: ...


    class azure.mgmt.datashare.aio.operations.DataSetMappingsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_subscription_name: str, 
                data_set_mapping_name: str, 
                data_set_mapping: DataSetMapping, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DataSetMapping: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_subscription_name: str, 
                data_set_mapping_name: str, 
                data_set_mapping: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DataSetMapping: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_subscription_name: str, 
                data_set_mapping_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_subscription_name: str, 
                data_set_mapping_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> DataSetMapping: ...

        @distributed_trace
        def list_by_share_subscription(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_subscription_name: str, 
                skip_token: Optional[str] = None, 
                filter: Optional[str] = None, 
                orderby: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[DataSetMapping]: ...


    class azure.mgmt.datashare.aio.operations.DataSetsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_name: str, 
                data_set_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_name: str, 
                data_set_name: str, 
                data_set: DataSet, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DataSet: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_name: str, 
                data_set_name: str, 
                data_set: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DataSet: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_name: str, 
                data_set_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> DataSet: ...

        @distributed_trace
        def list_by_share(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_name: str, 
                skip_token: Optional[str] = None, 
                filter: Optional[str] = None, 
                orderby: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[DataSet]: ...


    class azure.mgmt.datashare.aio.operations.EmailRegistrationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def activate_email(
                self, 
                location: str, 
                email_registration: EmailRegistration, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EmailRegistration: ...

        @overload
        async def activate_email(
                self, 
                location: str, 
                email_registration: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EmailRegistration: ...

        @distributed_trace_async
        async def register_email(
                self, 
                location: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> EmailRegistration: ...


    class azure.mgmt.datashare.aio.operations.InvitationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_name: str, 
                invitation_name: str, 
                invitation: Invitation, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Invitation: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_name: str, 
                invitation_name: str, 
                invitation: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Invitation: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_name: str, 
                invitation_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_name: str, 
                invitation_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Invitation: ...

        @distributed_trace
        def list_by_share(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_name: str, 
                skip_token: Optional[str] = None, 
                filter: Optional[str] = None, 
                orderby: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[Invitation]: ...


    class azure.mgmt.datashare.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[OperationModel]: ...


    class azure.mgmt.datashare.aio.operations.ProviderShareSubscriptionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def adjust(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_name: str, 
                provider_share_subscription_id: str, 
                provider_share_subscription: ProviderShareSubscription, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ProviderShareSubscription: ...

        @overload
        async def adjust(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_name: str, 
                provider_share_subscription_id: str, 
                provider_share_subscription: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ProviderShareSubscription: ...

        @distributed_trace_async
        async def begin_revoke(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_name: str, 
                provider_share_subscription_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[ProviderShareSubscription]: ...

        @distributed_trace_async
        async def get_by_share(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_name: str, 
                provider_share_subscription_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ProviderShareSubscription: ...

        @distributed_trace
        def list_by_share(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_name: str, 
                skip_token: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[ProviderShareSubscription]: ...

        @overload
        async def reinstate(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_name: str, 
                provider_share_subscription_id: str, 
                provider_share_subscription: ProviderShareSubscription, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ProviderShareSubscription: ...

        @overload
        async def reinstate(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_name: str, 
                provider_share_subscription_id: str, 
                provider_share_subscription: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ProviderShareSubscription: ...


    class azure.mgmt.datashare.aio.operations.ShareSubscriptionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_cancel_synchronization(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_subscription_name: str, 
                share_subscription_synchronization: ShareSubscriptionSynchronization, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ShareSubscriptionSynchronization]: ...

        @overload
        async def begin_cancel_synchronization(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_subscription_name: str, 
                share_subscription_synchronization: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ShareSubscriptionSynchronization]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_subscription_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationResponse]: ...

        @overload
        async def begin_synchronize(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_subscription_name: str, 
                synchronize: Synchronize, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ShareSubscriptionSynchronization]: ...

        @overload
        async def begin_synchronize(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_subscription_name: str, 
                synchronize: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ShareSubscriptionSynchronization]: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_subscription_name: str, 
                share_subscription: ShareSubscription, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ShareSubscription: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_subscription_name: str, 
                share_subscription: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ShareSubscription: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_subscription_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ShareSubscription: ...

        @distributed_trace
        def list_by_account(
                self, 
                resource_group_name: str, 
                account_name: str, 
                skip_token: Optional[str] = None, 
                filter: Optional[str] = None, 
                orderby: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[ShareSubscription]: ...

        @distributed_trace
        def list_source_share_synchronization_settings(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_subscription_name: str, 
                skip_token: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[SourceShareSynchronizationSetting]: ...

        @overload
        def list_synchronization_details(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_subscription_name: str, 
                share_subscription_synchronization: ShareSubscriptionSynchronization, 
                skip_token: Optional[str] = None, 
                filter: Optional[str] = None, 
                orderby: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncIterable[SynchronizationDetails]: ...

        @overload
        def list_synchronization_details(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_subscription_name: str, 
                share_subscription_synchronization: IO, 
                skip_token: Optional[str] = None, 
                filter: Optional[str] = None, 
                orderby: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncIterable[SynchronizationDetails]: ...

        @distributed_trace
        def list_synchronizations(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_subscription_name: str, 
                skip_token: Optional[str] = None, 
                filter: Optional[str] = None, 
                orderby: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[ShareSubscriptionSynchronization]: ...


    class azure.mgmt.datashare.aio.operations.SharesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationResponse]: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_name: str, 
                share: Share, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Share: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_name: str, 
                share: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Share: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Share: ...

        @distributed_trace
        def list_by_account(
                self, 
                resource_group_name: str, 
                account_name: str, 
                skip_token: Optional[str] = None, 
                filter: Optional[str] = None, 
                orderby: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[Share]: ...

        @overload
        def list_synchronization_details(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_name: str, 
                share_synchronization: ShareSynchronization, 
                skip_token: Optional[str] = None, 
                filter: Optional[str] = None, 
                orderby: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncIterable[SynchronizationDetails]: ...

        @overload
        def list_synchronization_details(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_name: str, 
                share_synchronization: IO, 
                skip_token: Optional[str] = None, 
                filter: Optional[str] = None, 
                orderby: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncIterable[SynchronizationDetails]: ...

        @distributed_trace
        def list_synchronizations(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_name: str, 
                skip_token: Optional[str] = None, 
                filter: Optional[str] = None, 
                orderby: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[ShareSynchronization]: ...


    class azure.mgmt.datashare.aio.operations.SynchronizationSettingsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_name: str, 
                synchronization_setting_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationResponse]: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_name: str, 
                synchronization_setting_name: str, 
                synchronization_setting: SynchronizationSetting, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SynchronizationSetting: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_name: str, 
                synchronization_setting_name: str, 
                synchronization_setting: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SynchronizationSetting: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_name: str, 
                synchronization_setting_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> SynchronizationSetting: ...

        @distributed_trace
        def list_by_share(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_name: str, 
                skip_token: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[SynchronizationSetting]: ...


    class azure.mgmt.datashare.aio.operations.TriggersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_subscription_name: str, 
                trigger_name: str, 
                trigger: Trigger, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Trigger]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_subscription_name: str, 
                trigger_name: str, 
                trigger: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Trigger]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_subscription_name: str, 
                trigger_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationResponse]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_subscription_name: str, 
                trigger_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Trigger: ...

        @distributed_trace
        def list_by_share_subscription(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_subscription_name: str, 
                skip_token: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[Trigger]: ...


namespace azure.mgmt.datashare.models

    class azure.mgmt.datashare.models.ADLSGen1FileDataSet(DataSet):
        account_name: str
        data_set_id: str
        file_name: str
        folder_path: str
        id: str
        kind: Union[str, DataSetKind]
        name: str
        resource_group: str
        subscription_id: str
        system_data: SystemData
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                account_name: str, 
                file_name: str, 
                folder_path: str, 
                resource_group: str, 
                subscription_id: str, 
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


    class azure.mgmt.datashare.models.ADLSGen1FolderDataSet(DataSet):
        account_name: str
        data_set_id: str
        folder_path: str
        id: str
        kind: Union[str, DataSetKind]
        name: str
        resource_group: str
        subscription_id: str
        system_data: SystemData
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                account_name: str, 
                folder_path: str, 
                resource_group: str, 
                subscription_id: str, 
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


    class azure.mgmt.datashare.models.ADLSGen2FileDataSet(DataSet):
        data_set_id: str
        file_path: str
        file_system: str
        id: str
        kind: Union[str, DataSetKind]
        name: str
        resource_group: str
        storage_account_name: str
        subscription_id: str
        system_data: SystemData
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                file_path: str, 
                file_system: str, 
                resource_group: str, 
                storage_account_name: str, 
                subscription_id: str, 
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


    class azure.mgmt.datashare.models.ADLSGen2FileDataSetMapping(DataSetMapping):
        data_set_id: str
        data_set_mapping_status: Union[str, DataSetMappingStatus]
        file_path: str
        file_system: str
        id: str
        kind: Union[str, DataSetMappingKind]
        name: str
        output_type: Union[str, OutputType]
        provisioning_state: Union[str, ProvisioningState]
        resource_group: str
        storage_account_name: str
        subscription_id: str
        system_data: SystemData
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                data_set_id: str, 
                file_path: str, 
                file_system: str, 
                output_type: Optional[Union[str, OutputType]] = ..., 
                resource_group: str, 
                storage_account_name: str, 
                subscription_id: str, 
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


    class azure.mgmt.datashare.models.ADLSGen2FileSystemDataSet(DataSet):
        data_set_id: str
        file_system: str
        id: str
        kind: Union[str, DataSetKind]
        name: str
        resource_group: str
        storage_account_name: str
        subscription_id: str
        system_data: SystemData
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                file_system: str, 
                resource_group: str, 
                storage_account_name: str, 
                subscription_id: str, 
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


    class azure.mgmt.datashare.models.ADLSGen2FileSystemDataSetMapping(DataSetMapping):
        data_set_id: str
        data_set_mapping_status: Union[str, DataSetMappingStatus]
        file_system: str
        id: str
        kind: Union[str, DataSetMappingKind]
        name: str
        provisioning_state: Union[str, ProvisioningState]
        resource_group: str
        storage_account_name: str
        subscription_id: str
        system_data: SystemData
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                data_set_id: str, 
                file_system: str, 
                resource_group: str, 
                storage_account_name: str, 
                subscription_id: str, 
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


    class azure.mgmt.datashare.models.ADLSGen2FolderDataSet(DataSet):
        data_set_id: str
        file_system: str
        folder_path: str
        id: str
        kind: Union[str, DataSetKind]
        name: str
        resource_group: str
        storage_account_name: str
        subscription_id: str
        system_data: SystemData
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                file_system: str, 
                folder_path: str, 
                resource_group: str, 
                storage_account_name: str, 
                subscription_id: str, 
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


    class azure.mgmt.datashare.models.ADLSGen2FolderDataSetMapping(DataSetMapping):
        data_set_id: str
        data_set_mapping_status: Union[str, DataSetMappingStatus]
        file_system: str
        folder_path: str
        id: str
        kind: Union[str, DataSetMappingKind]
        name: str
        provisioning_state: Union[str, ProvisioningState]
        resource_group: str
        storage_account_name: str
        subscription_id: str
        system_data: SystemData
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                data_set_id: str, 
                file_system: str, 
                folder_path: str, 
                resource_group: str, 
                storage_account_name: str, 
                subscription_id: str, 
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


    class azure.mgmt.datashare.models.Account(DefaultDto):
        created_at: datetime
        id: str
        identity: Identity
        location: str
        name: str
        provisioning_state: Union[str, ProvisioningState]
        system_data: SystemData
        tags: dict[str, str]
        type: str
        user_email: str
        user_name: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                identity: Identity, 
                location: Optional[str] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
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


    class azure.mgmt.datashare.models.AccountList(Model):
        next_link: str
        value: list[Account]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: List[Account], 
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


    class azure.mgmt.datashare.models.AccountUpdateParameters(Model):
        tags: dict[str, str]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                tags: Optional[Dict[str, str]] = ..., 
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


    class azure.mgmt.datashare.models.BlobContainerDataSet(DataSet):
        container_name: str
        data_set_id: str
        id: str
        kind: Union[str, DataSetKind]
        name: str
        resource_group: str
        storage_account_name: str
        subscription_id: str
        system_data: SystemData
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                container_name: str, 
                resource_group: str, 
                storage_account_name: str, 
                subscription_id: str, 
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


    class azure.mgmt.datashare.models.BlobContainerDataSetMapping(DataSetMapping):
        container_name: str
        data_set_id: str
        data_set_mapping_status: Union[str, DataSetMappingStatus]
        id: str
        kind: Union[str, DataSetMappingKind]
        name: str
        provisioning_state: Union[str, ProvisioningState]
        resource_group: str
        storage_account_name: str
        subscription_id: str
        system_data: SystemData
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                container_name: str, 
                data_set_id: str, 
                resource_group: str, 
                storage_account_name: str, 
                subscription_id: str, 
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


    class azure.mgmt.datashare.models.BlobDataSet(DataSet):
        container_name: str
        data_set_id: str
        file_path: str
        id: str
        kind: Union[str, DataSetKind]
        name: str
        resource_group: str
        storage_account_name: str
        subscription_id: str
        system_data: SystemData
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                container_name: str, 
                file_path: str, 
                resource_group: str, 
                storage_account_name: str, 
                subscription_id: str, 
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


    class azure.mgmt.datashare.models.BlobDataSetMapping(DataSetMapping):
        container_name: str
        data_set_id: str
        data_set_mapping_status: Union[str, DataSetMappingStatus]
        file_path: str
        id: str
        kind: Union[str, DataSetMappingKind]
        name: str
        output_type: Union[str, OutputType]
        provisioning_state: Union[str, ProvisioningState]
        resource_group: str
        storage_account_name: str
        subscription_id: str
        system_data: SystemData
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                container_name: str, 
                data_set_id: str, 
                file_path: str, 
                output_type: Optional[Union[str, OutputType]] = ..., 
                resource_group: str, 
                storage_account_name: str, 
                subscription_id: str, 
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


    class azure.mgmt.datashare.models.BlobFolderDataSet(DataSet):
        container_name: str
        data_set_id: str
        id: str
        kind: Union[str, DataSetKind]
        name: str
        prefix: str
        resource_group: str
        storage_account_name: str
        subscription_id: str
        system_data: SystemData
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                container_name: str, 
                prefix: str, 
                resource_group: str, 
                storage_account_name: str, 
                subscription_id: str, 
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


    class azure.mgmt.datashare.models.BlobFolderDataSetMapping(DataSetMapping):
        container_name: str
        data_set_id: str
        data_set_mapping_status: Union[str, DataSetMappingStatus]
        id: str
        kind: Union[str, DataSetMappingKind]
        name: str
        prefix: str
        provisioning_state: Union[str, ProvisioningState]
        resource_group: str
        storage_account_name: str
        subscription_id: str
        system_data: SystemData
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                container_name: str, 
                data_set_id: str, 
                prefix: str, 
                resource_group: str, 
                storage_account_name: str, 
                subscription_id: str, 
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


    class azure.mgmt.datashare.models.ConsumerInvitation(ProxyDto):
        data_set_count: int
        description: str
        expiration_date: datetime
        id: str
        invitation_id: str
        invitation_status: Union[str, InvitationStatus]
        location: str
        name: str
        provider_email: str
        provider_name: str
        provider_tenant_name: str
        responded_at: datetime
        sent_at: datetime
        share_name: str
        system_data: SystemData
        terms_of_use: str
        type: str
        user_email: str
        user_name: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                invitation_id: str, 
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


    class azure.mgmt.datashare.models.ConsumerInvitationList(Model):
        next_link: str
        value: list[ConsumerInvitation]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: List[ConsumerInvitation], 
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


    class azure.mgmt.datashare.models.ConsumerSourceDataSet(ProxyDto):
        data_set_id: str
        data_set_location: str
        data_set_name: str
        data_set_path: str
        data_set_type: Union[str, DataSetType]
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


    class azure.mgmt.datashare.models.ConsumerSourceDataSetList(Model):
        next_link: str
        value: list[ConsumerSourceDataSet]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: List[ConsumerSourceDataSet], 
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


    class azure.mgmt.datashare.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.datashare.models.DataSet(ProxyDto):
        id: str
        kind: Union[str, DataSetKind]
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


    class azure.mgmt.datashare.models.DataSetKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ADLS_GEN1_FILE = "AdlsGen1File"
        ADLS_GEN1_FOLDER = "AdlsGen1Folder"
        ADLS_GEN2_FILE = "AdlsGen2File"
        ADLS_GEN2_FILE_SYSTEM = "AdlsGen2FileSystem"
        ADLS_GEN2_FOLDER = "AdlsGen2Folder"
        BLOB = "Blob"
        BLOB_FOLDER = "BlobFolder"
        CONTAINER = "Container"
        KUSTO_CLUSTER = "KustoCluster"
        KUSTO_DATABASE = "KustoDatabase"
        SQL_DB_TABLE = "SqlDBTable"
        SQL_DW_TABLE = "SqlDWTable"
        SYNAPSE_WORKSPACE_SQL_POOL_TABLE = "SynapseWorkspaceSqlPoolTable"


    class azure.mgmt.datashare.models.DataSetList(Model):
        next_link: str
        value: list[DataSet]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: List[DataSet], 
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


    class azure.mgmt.datashare.models.DataSetMapping(ProxyDto):
        id: str
        kind: Union[str, DataSetMappingKind]
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


    class azure.mgmt.datashare.models.DataSetMappingKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ADLS_GEN2_FILE = "AdlsGen2File"
        ADLS_GEN2_FILE_SYSTEM = "AdlsGen2FileSystem"
        ADLS_GEN2_FOLDER = "AdlsGen2Folder"
        BLOB = "Blob"
        BLOB_FOLDER = "BlobFolder"
        CONTAINER = "Container"
        KUSTO_CLUSTER = "KustoCluster"
        KUSTO_DATABASE = "KustoDatabase"
        SQL_DB_TABLE = "SqlDBTable"
        SQL_DW_TABLE = "SqlDWTable"
        SYNAPSE_WORKSPACE_SQL_POOL_TABLE = "SynapseWorkspaceSqlPoolTable"


    class azure.mgmt.datashare.models.DataSetMappingList(Model):
        next_link: str
        value: list[DataSetMapping]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: List[DataSetMapping], 
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


    class azure.mgmt.datashare.models.DataSetMappingStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BROKEN = "Broken"
        OK = "Ok"


    class azure.mgmt.datashare.models.DataSetType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ADLS_GEN1_FILE = "AdlsGen1File"
        ADLS_GEN1_FOLDER = "AdlsGen1Folder"
        ADLS_GEN2_FILE = "AdlsGen2File"
        ADLS_GEN2_FILE_SYSTEM = "AdlsGen2FileSystem"
        ADLS_GEN2_FOLDER = "AdlsGen2Folder"
        BLOB = "Blob"
        BLOB_FOLDER = "BlobFolder"
        CONTAINER = "Container"
        KUSTO_CLUSTER = "KustoCluster"
        KUSTO_DATABASE = "KustoDatabase"
        SQL_DB_TABLE = "SqlDBTable"
        SQL_DW_TABLE = "SqlDWTable"
        SYNAPSE_WORKSPACE_SQL_POOL_TABLE = "SynapseWorkspaceSqlPoolTable"


    class azure.mgmt.datashare.models.DataShareError(Model):
        error: DataShareErrorInfo

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                error: DataShareErrorInfo, 
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


    class azure.mgmt.datashare.models.DataShareErrorInfo(Model):
        code: str
        details: list[DataShareErrorInfo]
        message: str
        target: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                code: str, 
                details: Optional[List[DataShareErrorInfo]] = ..., 
                message: str, 
                target: Optional[str] = ..., 
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


    class azure.mgmt.datashare.models.DefaultDto(ProxyDto):
        id: str
        location: str
        name: str
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
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


    class azure.mgmt.datashare.models.DimensionProperties(Model):
        display_name: str
        name: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                display_name: Optional[str] = ..., 
                name: Optional[str] = ..., 
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


    class azure.mgmt.datashare.models.EmailRegistration(Model):
        activation_code: str
        activation_expiration_date: datetime
        email: str
        registration_status: Union[str, RegistrationStatus]
        tenant_id: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                activation_code: Optional[str] = ..., 
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


    class azure.mgmt.datashare.models.Identity(Model):
        principal_id: str
        tenant_id: str
        type: Union[str, Type]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                type: Optional[Union[str, Type]] = ..., 
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


    class azure.mgmt.datashare.models.Invitation(ProxyDto):
        expiration_date: datetime
        id: str
        invitation_id: str
        invitation_status: Union[str, InvitationStatus]
        name: str
        responded_at: datetime
        sent_at: datetime
        system_data: SystemData
        target_active_directory_id: str
        target_email: str
        target_object_id: str
        type: str
        user_email: str
        user_name: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                expiration_date: Optional[datetime] = ..., 
                target_active_directory_id: Optional[str] = ..., 
                target_email: Optional[str] = ..., 
                target_object_id: Optional[str] = ..., 
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


    class azure.mgmt.datashare.models.InvitationList(Model):
        next_link: str
        value: list[Invitation]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: List[Invitation], 
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


    class azure.mgmt.datashare.models.InvitationStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        PENDING = "Pending"
        REJECTED = "Rejected"
        WITHDRAWN = "Withdrawn"


    class azure.mgmt.datashare.models.KustoClusterDataSet(DataSet):
        data_set_id: str
        id: str
        kind: Union[str, DataSetKind]
        kusto_cluster_resource_id: str
        location: str
        name: str
        provisioning_state: Union[str, ProvisioningState]
        system_data: SystemData
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                kusto_cluster_resource_id: str, 
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


    class azure.mgmt.datashare.models.KustoClusterDataSetMapping(DataSetMapping):
        data_set_id: str
        data_set_mapping_status: Union[str, DataSetMappingStatus]
        id: str
        kind: Union[str, DataSetMappingKind]
        kusto_cluster_resource_id: str
        location: str
        name: str
        provisioning_state: Union[str, ProvisioningState]
        system_data: SystemData
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                data_set_id: str, 
                kusto_cluster_resource_id: str, 
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


    class azure.mgmt.datashare.models.KustoDatabaseDataSet(DataSet):
        data_set_id: str
        id: str
        kind: Union[str, DataSetKind]
        kusto_database_resource_id: str
        location: str
        name: str
        provisioning_state: Union[str, ProvisioningState]
        system_data: SystemData
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                kusto_database_resource_id: str, 
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


    class azure.mgmt.datashare.models.KustoDatabaseDataSetMapping(DataSetMapping):
        data_set_id: str
        data_set_mapping_status: Union[str, DataSetMappingStatus]
        id: str
        kind: Union[str, DataSetMappingKind]
        kusto_cluster_resource_id: str
        location: str
        name: str
        provisioning_state: Union[str, ProvisioningState]
        system_data: SystemData
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                data_set_id: str, 
                kusto_cluster_resource_id: str, 
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


    class azure.mgmt.datashare.models.LastModifiedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.datashare.models.OperationList(Model):
        next_link: str
        value: list[OperationModel]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: List[OperationModel], 
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


    class azure.mgmt.datashare.models.OperationMetaLogSpecification(Model):
        blob_duration: str
        display_name: str
        name: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                blob_duration: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                name: Optional[str] = ..., 
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


    class azure.mgmt.datashare.models.OperationMetaMetricSpecification(Model):
        aggregation_type: str
        dimensions: list[DimensionProperties]
        display_description: str
        display_name: str
        enable_regional_mdm_account: str
        fill_gap_with_zero: bool
        internal_metric_name: str
        name: str
        resource_id_dimension_name_override: str
        supported_aggregation_types: list[str]
        supported_time_grain_types: list[str]
        unit: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                aggregation_type: Optional[str] = ..., 
                dimensions: Optional[List[DimensionProperties]] = ..., 
                display_description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                enable_regional_mdm_account: Optional[str] = ..., 
                fill_gap_with_zero: Optional[bool] = ..., 
                internal_metric_name: Optional[str] = ..., 
                name: Optional[str] = ..., 
                resource_id_dimension_name_override: Optional[str] = ..., 
                supported_aggregation_types: Optional[List[str]] = ..., 
                supported_time_grain_types: Optional[List[str]] = ..., 
                unit: Optional[str] = ..., 
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


    class azure.mgmt.datashare.models.OperationMetaServiceSpecification(Model):
        log_specifications: list[OperationMetaLogSpecification]
        metric_specifications: list[OperationMetaMetricSpecification]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                log_specifications: Optional[List[OperationMetaLogSpecification]] = ..., 
                metric_specifications: Optional[List[OperationMetaMetricSpecification]] = ..., 
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


    class azure.mgmt.datashare.models.OperationModel(Model):
        display: OperationModelProperties
        name: str
        origin: str
        service_specification: OperationMetaServiceSpecification

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                display: Optional[OperationModelProperties] = ..., 
                name: Optional[str] = ..., 
                origin: Optional[str] = ..., 
                service_specification: Optional[OperationMetaServiceSpecification] = ..., 
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


    class azure.mgmt.datashare.models.OperationModelProperties(Model):
        description: str
        operation: str
        provider: str
        resource: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                operation: Optional[str] = ..., 
                provider: Optional[str] = ..., 
                resource: Optional[str] = ..., 
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


    class azure.mgmt.datashare.models.OperationResponse(Model):
        end_time: datetime
        error: DataShareErrorInfo
        start_time: datetime
        status: Union[str, Status]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                end_time: Optional[datetime] = ..., 
                error: Optional[DataShareErrorInfo] = ..., 
                start_time: Optional[datetime] = ..., 
                status: Union[str, Status], 
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


    class azure.mgmt.datashare.models.OutputType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CSV = "Csv"
        PARQUET = "Parquet"


    class azure.mgmt.datashare.models.ProviderShareSubscription(ProxyDto):
        consumer_email: str
        consumer_name: str
        consumer_tenant_name: str
        created_at: datetime
        expiration_date: datetime
        id: str
        name: str
        provider_email: str
        provider_name: str
        share_subscription_object_id: str
        share_subscription_status: Union[str, ShareSubscriptionStatus]
        shared_at: datetime
        system_data: SystemData
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                expiration_date: Optional[datetime] = ..., 
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


    class azure.mgmt.datashare.models.ProviderShareSubscriptionList(Model):
        next_link: str
        value: list[ProviderShareSubscription]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: List[ProviderShareSubscription], 
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


    class azure.mgmt.datashare.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        MOVING = "Moving"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.datashare.models.ProxyDto(Model):
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


    class azure.mgmt.datashare.models.RecurrenceInterval(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DAY = "Day"
        HOUR = "Hour"


    class azure.mgmt.datashare.models.RegistrationStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVATED = "Activated"
        ACTIVATION_ATTEMPTS_EXHAUSTED = "ActivationAttemptsExhausted"
        ACTIVATION_PENDING = "ActivationPending"


    class azure.mgmt.datashare.models.ScheduledSourceSynchronizationSetting(SourceShareSynchronizationSetting):
        kind: Union[str, SourceShareSynchronizationSettingKind]
        recurrence_interval: Union[str, RecurrenceInterval]
        synchronization_time: datetime

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                recurrence_interval: Optional[Union[str, RecurrenceInterval]] = ..., 
                synchronization_time: Optional[datetime] = ..., 
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


    class azure.mgmt.datashare.models.ScheduledSynchronizationSetting(SynchronizationSetting):
        created_at: datetime
        id: str
        kind: Union[str, SynchronizationSettingKind]
        name: str
        provisioning_state: Union[str, ProvisioningState]
        recurrence_interval: Union[str, RecurrenceInterval]
        synchronization_time: datetime
        system_data: SystemData
        type: str
        user_name: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                recurrence_interval: Union[str, RecurrenceInterval], 
                synchronization_time: datetime, 
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


    class azure.mgmt.datashare.models.ScheduledTrigger(Trigger):
        created_at: datetime
        id: str
        kind: Union[str, TriggerKind]
        name: str
        provisioning_state: Union[str, ProvisioningState]
        recurrence_interval: Union[str, RecurrenceInterval]
        synchronization_mode: Union[str, SynchronizationMode]
        synchronization_time: datetime
        system_data: SystemData
        trigger_status: Union[str, TriggerStatus]
        type: str
        user_name: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                recurrence_interval: Union[str, RecurrenceInterval], 
                synchronization_mode: Optional[Union[str, SynchronizationMode]] = ..., 
                synchronization_time: datetime, 
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


    class azure.mgmt.datashare.models.Share(ProxyDto):
        created_at: datetime
        description: str
        id: str
        name: str
        provisioning_state: Union[str, ProvisioningState]
        share_kind: Union[str, ShareKind]
        system_data: SystemData
        terms: str
        type: str
        user_email: str
        user_name: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                share_kind: Optional[Union[str, ShareKind]] = ..., 
                terms: Optional[str] = ..., 
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


    class azure.mgmt.datashare.models.ShareKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COPY_BASED = "CopyBased"
        IN_PLACE = "InPlace"


    class azure.mgmt.datashare.models.ShareList(Model):
        next_link: str
        value: list[Share]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: List[Share], 
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


    class azure.mgmt.datashare.models.ShareSubscription(ProxyDto):
        created_at: datetime
        expiration_date: datetime
        id: str
        invitation_id: str
        name: str
        provider_email: str
        provider_name: str
        provider_tenant_name: str
        provisioning_state: Union[str, ProvisioningState]
        share_description: str
        share_kind: Union[str, ShareKind]
        share_name: str
        share_subscription_status: Union[str, ShareSubscriptionStatus]
        share_terms: str
        source_share_location: str
        system_data: SystemData
        type: str
        user_email: str
        user_name: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                expiration_date: Optional[datetime] = ..., 
                invitation_id: str, 
                source_share_location: str, 
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


    class azure.mgmt.datashare.models.ShareSubscriptionList(Model):
        next_link: str
        value: list[ShareSubscription]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: List[ShareSubscription], 
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


    class azure.mgmt.datashare.models.ShareSubscriptionStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        REVOKED = "Revoked"
        REVOKING = "Revoking"
        SOURCE_DELETED = "SourceDeleted"


    class azure.mgmt.datashare.models.ShareSubscriptionSynchronization(Model):
        duration_ms: int
        end_time: datetime
        message: str
        start_time: datetime
        status: str
        synchronization_id: str
        synchronization_mode: Union[str, SynchronizationMode]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                synchronization_id: str, 
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


    class azure.mgmt.datashare.models.ShareSubscriptionSynchronizationList(Model):
        next_link: str
        value: list[ShareSubscriptionSynchronization]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: List[ShareSubscriptionSynchronization], 
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


    class azure.mgmt.datashare.models.ShareSynchronization(Model):
        consumer_email: str
        consumer_name: str
        consumer_tenant_name: str
        duration_ms: int
        end_time: datetime
        message: str
        start_time: datetime
        status: str
        synchronization_id: str
        synchronization_mode: Union[str, SynchronizationMode]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                consumer_email: Optional[str] = ..., 
                consumer_name: Optional[str] = ..., 
                consumer_tenant_name: Optional[str] = ..., 
                duration_ms: Optional[int] = ..., 
                end_time: Optional[datetime] = ..., 
                message: Optional[str] = ..., 
                start_time: Optional[datetime] = ..., 
                status: Optional[str] = ..., 
                synchronization_id: Optional[str] = ..., 
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


    class azure.mgmt.datashare.models.ShareSynchronizationList(Model):
        next_link: str
        value: list[ShareSynchronization]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: List[ShareSynchronization], 
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


    class azure.mgmt.datashare.models.SourceShareSynchronizationSetting(Model):
        kind: Union[str, SourceShareSynchronizationSettingKind]

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


    class azure.mgmt.datashare.models.SourceShareSynchronizationSettingKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SCHEDULE_BASED = "ScheduleBased"


    class azure.mgmt.datashare.models.SourceShareSynchronizationSettingList(Model):
        next_link: str
        value: list[SourceShareSynchronizationSetting]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: List[SourceShareSynchronizationSetting], 
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


    class azure.mgmt.datashare.models.SqlDBTableDataSet(DataSet):
        data_set_id: str
        database_name: str
        id: str
        kind: Union[str, DataSetKind]
        name: str
        schema_name: str
        sql_server_resource_id: str
        system_data: SystemData
        table_name: str
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                database_name: Optional[str] = ..., 
                schema_name: Optional[str] = ..., 
                sql_server_resource_id: Optional[str] = ..., 
                table_name: Optional[str] = ..., 
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


    class azure.mgmt.datashare.models.SqlDBTableDataSetMapping(DataSetMapping):
        data_set_id: str
        data_set_mapping_status: Union[str, DataSetMappingStatus]
        database_name: str
        id: str
        kind: Union[str, DataSetMappingKind]
        name: str
        provisioning_state: Union[str, ProvisioningState]
        schema_name: str
        sql_server_resource_id: str
        system_data: SystemData
        table_name: str
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                data_set_id: str, 
                database_name: str, 
                schema_name: str, 
                sql_server_resource_id: str, 
                table_name: str, 
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


    class azure.mgmt.datashare.models.SqlDWTableDataSet(DataSet):
        data_set_id: str
        data_warehouse_name: str
        id: str
        kind: Union[str, DataSetKind]
        name: str
        schema_name: str
        sql_server_resource_id: str
        system_data: SystemData
        table_name: str
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                data_warehouse_name: Optional[str] = ..., 
                schema_name: Optional[str] = ..., 
                sql_server_resource_id: Optional[str] = ..., 
                table_name: Optional[str] = ..., 
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


    class azure.mgmt.datashare.models.SqlDWTableDataSetMapping(DataSetMapping):
        data_set_id: str
        data_set_mapping_status: Union[str, DataSetMappingStatus]
        data_warehouse_name: str
        id: str
        kind: Union[str, DataSetMappingKind]
        name: str
        provisioning_state: Union[str, ProvisioningState]
        schema_name: str
        sql_server_resource_id: str
        system_data: SystemData
        table_name: str
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                data_set_id: str, 
                data_warehouse_name: str, 
                schema_name: str, 
                sql_server_resource_id: str, 
                table_name: str, 
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


    class azure.mgmt.datashare.models.Status(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        CANCELED = "Canceled"
        FAILED = "Failed"
        IN_PROGRESS = "InProgress"
        SUCCEEDED = "Succeeded"
        TRANSIENT_FAILURE = "TransientFailure"


    class azure.mgmt.datashare.models.SynapseWorkspaceSqlPoolTableDataSet(DataSet):
        data_set_id: str
        id: str
        kind: Union[str, DataSetKind]
        name: str
        synapse_workspace_sql_pool_table_resource_id: str
        system_data: SystemData
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                synapse_workspace_sql_pool_table_resource_id: str, 
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


    class azure.mgmt.datashare.models.SynapseWorkspaceSqlPoolTableDataSetMapping(DataSetMapping):
        data_set_id: str
        data_set_mapping_status: Union[str, DataSetMappingStatus]
        id: str
        kind: Union[str, DataSetMappingKind]
        name: str
        provisioning_state: Union[str, ProvisioningState]
        synapse_workspace_sql_pool_table_resource_id: str
        system_data: SystemData
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                data_set_id: str, 
                synapse_workspace_sql_pool_table_resource_id: str, 
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


    class azure.mgmt.datashare.models.SynchronizationDetails(Model):
        data_set_id: str
        data_set_type: Union[str, DataSetType]
        duration_ms: int
        end_time: datetime
        files_read: int
        files_written: int
        message: str
        name: str
        rows_copied: int
        rows_read: int
        size_read: int
        size_written: int
        start_time: datetime
        status: str
        v_core: int

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


    class azure.mgmt.datashare.models.SynchronizationDetailsList(Model):
        next_link: str
        value: list[SynchronizationDetails]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: List[SynchronizationDetails], 
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


    class azure.mgmt.datashare.models.SynchronizationMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FULL_SYNC = "FullSync"
        INCREMENTAL = "Incremental"


    class azure.mgmt.datashare.models.SynchronizationSetting(ProxyDto):
        id: str
        kind: Union[str, SynchronizationSettingKind]
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


    class azure.mgmt.datashare.models.SynchronizationSettingKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SCHEDULE_BASED = "ScheduleBased"


    class azure.mgmt.datashare.models.SynchronizationSettingList(Model):
        next_link: str
        value: list[SynchronizationSetting]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: List[SynchronizationSetting], 
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


    class azure.mgmt.datashare.models.Synchronize(Model):
        synchronization_mode: Union[str, SynchronizationMode]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                synchronization_mode: Optional[Union[str, SynchronizationMode]] = ..., 
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


    class azure.mgmt.datashare.models.SystemData(Model):
        created_at: datetime
        created_by: str
        created_by_type: Union[str, CreatedByType]
        last_modified_at: datetime
        last_modified_by: str
        last_modified_by_type: Union[str, LastModifiedByType]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                created_at: Optional[datetime] = ..., 
                created_by: Optional[str] = ..., 
                created_by_type: Optional[Union[str, CreatedByType]] = ..., 
                last_modified_at: Optional[datetime] = ..., 
                last_modified_by: Optional[str] = ..., 
                last_modified_by_type: Optional[Union[str, LastModifiedByType]] = ..., 
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


    class azure.mgmt.datashare.models.Trigger(ProxyDto):
        id: str
        kind: Union[str, TriggerKind]
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


    class azure.mgmt.datashare.models.TriggerKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SCHEDULE_BASED = "ScheduleBased"


    class azure.mgmt.datashare.models.TriggerList(Model):
        next_link: str
        value: list[Trigger]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: List[Trigger], 
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


    class azure.mgmt.datashare.models.TriggerStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        INACTIVE = "Inactive"
        SOURCE_SYNCHRONIZATION_SETTING_DELETED = "SourceSynchronizationSettingDeleted"


    class azure.mgmt.datashare.models.Type(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM_ASSIGNED = "SystemAssigned"


namespace azure.mgmt.datashare.operations

    class azure.mgmt.datashare.operations.AccountsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                account: Account, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Account]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                account: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Account]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[OperationResponse]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Account: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                skip_token: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[Account]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                skip_token: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[Account]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                account_update_parameters: AccountUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Account: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                account_update_parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Account: ...


    class azure.mgmt.datashare.operations.ConsumerInvitationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get(
                self, 
                location: str, 
                invitation_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ConsumerInvitation: ...

        @distributed_trace
        def list_invitations(
                self, 
                skip_token: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[ConsumerInvitation]: ...

        @overload
        def reject_invitation(
                self, 
                location: str, 
                invitation: ConsumerInvitation, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConsumerInvitation: ...

        @overload
        def reject_invitation(
                self, 
                location: str, 
                invitation: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConsumerInvitation: ...


    class azure.mgmt.datashare.operations.ConsumerSourceDataSetsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def list_by_share_subscription(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_subscription_name: str, 
                skip_token: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[ConsumerSourceDataSet]: ...


    class azure.mgmt.datashare.operations.DataSetMappingsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_subscription_name: str, 
                data_set_mapping_name: str, 
                data_set_mapping: DataSetMapping, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DataSetMapping: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_subscription_name: str, 
                data_set_mapping_name: str, 
                data_set_mapping: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DataSetMapping: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_subscription_name: str, 
                data_set_mapping_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_subscription_name: str, 
                data_set_mapping_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> DataSetMapping: ...

        @distributed_trace
        def list_by_share_subscription(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_subscription_name: str, 
                skip_token: Optional[str] = None, 
                filter: Optional[str] = None, 
                orderby: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[DataSetMapping]: ...


    class azure.mgmt.datashare.operations.DataSetsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_name: str, 
                data_set_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_name: str, 
                data_set_name: str, 
                data_set: DataSet, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DataSet: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_name: str, 
                data_set_name: str, 
                data_set: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DataSet: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_name: str, 
                data_set_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> DataSet: ...

        @distributed_trace
        def list_by_share(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_name: str, 
                skip_token: Optional[str] = None, 
                filter: Optional[str] = None, 
                orderby: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[DataSet]: ...


    class azure.mgmt.datashare.operations.EmailRegistrationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def activate_email(
                self, 
                location: str, 
                email_registration: EmailRegistration, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EmailRegistration: ...

        @overload
        def activate_email(
                self, 
                location: str, 
                email_registration: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EmailRegistration: ...

        @distributed_trace
        def register_email(
                self, 
                location: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> EmailRegistration: ...


    class azure.mgmt.datashare.operations.InvitationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_name: str, 
                invitation_name: str, 
                invitation: Invitation, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Invitation: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_name: str, 
                invitation_name: str, 
                invitation: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Invitation: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_name: str, 
                invitation_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_name: str, 
                invitation_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Invitation: ...

        @distributed_trace
        def list_by_share(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_name: str, 
                skip_token: Optional[str] = None, 
                filter: Optional[str] = None, 
                orderby: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[Invitation]: ...


    class azure.mgmt.datashare.operations.Operations:

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
            ) -> Iterable[OperationModel]: ...


    class azure.mgmt.datashare.operations.ProviderShareSubscriptionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def adjust(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_name: str, 
                provider_share_subscription_id: str, 
                provider_share_subscription: ProviderShareSubscription, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ProviderShareSubscription: ...

        @overload
        def adjust(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_name: str, 
                provider_share_subscription_id: str, 
                provider_share_subscription: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ProviderShareSubscription: ...

        @distributed_trace
        def begin_revoke(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_name: str, 
                provider_share_subscription_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[ProviderShareSubscription]: ...

        @distributed_trace
        def get_by_share(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_name: str, 
                provider_share_subscription_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ProviderShareSubscription: ...

        @distributed_trace
        def list_by_share(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_name: str, 
                skip_token: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[ProviderShareSubscription]: ...

        @overload
        def reinstate(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_name: str, 
                provider_share_subscription_id: str, 
                provider_share_subscription: ProviderShareSubscription, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ProviderShareSubscription: ...

        @overload
        def reinstate(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_name: str, 
                provider_share_subscription_id: str, 
                provider_share_subscription: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ProviderShareSubscription: ...


    class azure.mgmt.datashare.operations.ShareSubscriptionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_cancel_synchronization(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_subscription_name: str, 
                share_subscription_synchronization: ShareSubscriptionSynchronization, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ShareSubscriptionSynchronization]: ...

        @overload
        def begin_cancel_synchronization(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_subscription_name: str, 
                share_subscription_synchronization: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ShareSubscriptionSynchronization]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_subscription_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[OperationResponse]: ...

        @overload
        def begin_synchronize(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_subscription_name: str, 
                synchronize: Synchronize, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ShareSubscriptionSynchronization]: ...

        @overload
        def begin_synchronize(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_subscription_name: str, 
                synchronize: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ShareSubscriptionSynchronization]: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_subscription_name: str, 
                share_subscription: ShareSubscription, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ShareSubscription: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_subscription_name: str, 
                share_subscription: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ShareSubscription: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_subscription_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ShareSubscription: ...

        @distributed_trace
        def list_by_account(
                self, 
                resource_group_name: str, 
                account_name: str, 
                skip_token: Optional[str] = None, 
                filter: Optional[str] = None, 
                orderby: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[ShareSubscription]: ...

        @distributed_trace
        def list_source_share_synchronization_settings(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_subscription_name: str, 
                skip_token: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[SourceShareSynchronizationSetting]: ...

        @overload
        def list_synchronization_details(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_subscription_name: str, 
                share_subscription_synchronization: ShareSubscriptionSynchronization, 
                skip_token: Optional[str] = None, 
                filter: Optional[str] = None, 
                orderby: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Iterable[SynchronizationDetails]: ...

        @overload
        def list_synchronization_details(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_subscription_name: str, 
                share_subscription_synchronization: IO, 
                skip_token: Optional[str] = None, 
                filter: Optional[str] = None, 
                orderby: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Iterable[SynchronizationDetails]: ...

        @distributed_trace
        def list_synchronizations(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_subscription_name: str, 
                skip_token: Optional[str] = None, 
                filter: Optional[str] = None, 
                orderby: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[ShareSubscriptionSynchronization]: ...


    class azure.mgmt.datashare.operations.SharesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[OperationResponse]: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_name: str, 
                share: Share, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Share: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_name: str, 
                share: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Share: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Share: ...

        @distributed_trace
        def list_by_account(
                self, 
                resource_group_name: str, 
                account_name: str, 
                skip_token: Optional[str] = None, 
                filter: Optional[str] = None, 
                orderby: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[Share]: ...

        @overload
        def list_synchronization_details(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_name: str, 
                share_synchronization: ShareSynchronization, 
                skip_token: Optional[str] = None, 
                filter: Optional[str] = None, 
                orderby: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Iterable[SynchronizationDetails]: ...

        @overload
        def list_synchronization_details(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_name: str, 
                share_synchronization: IO, 
                skip_token: Optional[str] = None, 
                filter: Optional[str] = None, 
                orderby: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Iterable[SynchronizationDetails]: ...

        @distributed_trace
        def list_synchronizations(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_name: str, 
                skip_token: Optional[str] = None, 
                filter: Optional[str] = None, 
                orderby: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[ShareSynchronization]: ...


    class azure.mgmt.datashare.operations.SynchronizationSettingsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_name: str, 
                synchronization_setting_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[OperationResponse]: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_name: str, 
                synchronization_setting_name: str, 
                synchronization_setting: SynchronizationSetting, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SynchronizationSetting: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_name: str, 
                synchronization_setting_name: str, 
                synchronization_setting: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SynchronizationSetting: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_name: str, 
                synchronization_setting_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> SynchronizationSetting: ...

        @distributed_trace
        def list_by_share(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_name: str, 
                skip_token: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[SynchronizationSetting]: ...


    class azure.mgmt.datashare.operations.TriggersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_subscription_name: str, 
                trigger_name: str, 
                trigger: Trigger, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Trigger]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_subscription_name: str, 
                trigger_name: str, 
                trigger: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Trigger]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_subscription_name: str, 
                trigger_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[OperationResponse]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_subscription_name: str, 
                trigger_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Trigger: ...

        @distributed_trace
        def list_by_share_subscription(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_subscription_name: str, 
                skip_token: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[Trigger]: ...


```