```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.datalake.analytics.account

    class azure.mgmt.datalake.analytics.account.DataLakeAnalyticsAccountManagementClient: implements ContextManager 
        accounts: AccountsOperations
        compute_policies: ComputePoliciesOperations
        data_lake_store_accounts: DataLakeStoreAccountsOperations
        firewall_rules: FirewallRulesOperations
        locations: LocationsOperations
        operations: Operations
        storage_accounts: StorageAccountsOperations

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


namespace azure.mgmt.datalake.analytics.account.aio

    class azure.mgmt.datalake.analytics.account.aio.DataLakeAnalyticsAccountManagementClient: implements AsyncContextManager 
        accounts: AccountsOperations
        compute_policies: ComputePoliciesOperations
        data_lake_store_accounts: DataLakeStoreAccountsOperations
        firewall_rules: FirewallRulesOperations
        locations: LocationsOperations
        operations: Operations
        storage_accounts: StorageAccountsOperations

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


namespace azure.mgmt.datalake.analytics.account.aio.operations

    class azure.mgmt.datalake.analytics.account.aio.operations.AccountsOperations:

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
                parameters: CreateDataLakeAnalyticsAccountParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DataLakeAnalyticsAccount]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DataLakeAnalyticsAccount]: ...

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
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                parameters: Optional[UpdateDataLakeAnalyticsAccountParameters] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DataLakeAnalyticsAccount]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                parameters: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DataLakeAnalyticsAccount]: ...

        @overload
        async def check_name_availability(
                self, 
                location: str, 
                parameters: CheckNameAvailabilityParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> NameAvailabilityInformation: ...

        @overload
        async def check_name_availability(
                self, 
                location: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> NameAvailabilityInformation: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> DataLakeAnalyticsAccount: ...

        @distributed_trace
        def list(
                self, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                skip: Optional[int] = None, 
                select: Optional[str] = None, 
                orderby: Optional[str] = None, 
                count: Optional[bool] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[DataLakeAnalyticsAccountBasic]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                skip: Optional[int] = None, 
                select: Optional[str] = None, 
                orderby: Optional[str] = None, 
                count: Optional[bool] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[DataLakeAnalyticsAccountBasic]: ...


    class azure.mgmt.datalake.analytics.account.aio.operations.ComputePoliciesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                compute_policy_name: str, 
                parameters: CreateOrUpdateComputePolicyParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ComputePolicy: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                compute_policy_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ComputePolicy: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                compute_policy_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                compute_policy_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ComputePolicy: ...

        @distributed_trace
        def list_by_account(
                self, 
                resource_group_name: str, 
                account_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[ComputePolicy]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                compute_policy_name: str, 
                parameters: Optional[UpdateComputePolicyParameters] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ComputePolicy: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                compute_policy_name: str, 
                parameters: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ComputePolicy: ...


    class azure.mgmt.datalake.analytics.account.aio.operations.DataLakeStoreAccountsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def add(
                self, 
                resource_group_name: str, 
                account_name: str, 
                data_lake_store_account_name: str, 
                parameters: Optional[AddDataLakeStoreParameters] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def add(
                self, 
                resource_group_name: str, 
                account_name: str, 
                data_lake_store_account_name: str, 
                parameters: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                data_lake_store_account_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                data_lake_store_account_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> DataLakeStoreAccountInformation: ...

        @distributed_trace
        def list_by_account(
                self, 
                resource_group_name: str, 
                account_name: str, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                skip: Optional[int] = None, 
                select: Optional[str] = None, 
                orderby: Optional[str] = None, 
                count: Optional[bool] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[DataLakeStoreAccountInformation]: ...


    class azure.mgmt.datalake.analytics.account.aio.operations.FirewallRulesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                firewall_rule_name: str, 
                parameters: CreateOrUpdateFirewallRuleParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FirewallRule: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                firewall_rule_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FirewallRule: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                firewall_rule_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                firewall_rule_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> FirewallRule: ...

        @distributed_trace
        def list_by_account(
                self, 
                resource_group_name: str, 
                account_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[FirewallRule]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                firewall_rule_name: str, 
                parameters: Optional[UpdateFirewallRuleParameters] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FirewallRule: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                firewall_rule_name: str, 
                parameters: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FirewallRule: ...


    class azure.mgmt.datalake.analytics.account.aio.operations.LocationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get_capability(
                self, 
                location: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Optional[CapabilityInformation]: ...


    class azure.mgmt.datalake.analytics.account.aio.operations.Operations:

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


    class azure.mgmt.datalake.analytics.account.aio.operations.StorageAccountsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def add(
                self, 
                resource_group_name: str, 
                account_name: str, 
                storage_account_name: str, 
                parameters: AddStorageAccountParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def add(
                self, 
                resource_group_name: str, 
                account_name: str, 
                storage_account_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                storage_account_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                storage_account_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> StorageAccountInformation: ...

        @distributed_trace_async
        async def get_storage_container(
                self, 
                resource_group_name: str, 
                account_name: str, 
                storage_account_name: str, 
                container_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> StorageContainer: ...

        @distributed_trace
        def list_by_account(
                self, 
                resource_group_name: str, 
                account_name: str, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                skip: Optional[int] = None, 
                select: Optional[str] = None, 
                orderby: Optional[str] = None, 
                count: Optional[bool] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[StorageAccountInformation]: ...

        @distributed_trace
        def list_sas_tokens(
                self, 
                resource_group_name: str, 
                account_name: str, 
                storage_account_name: str, 
                container_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[SasTokenInformation]: ...

        @distributed_trace
        def list_storage_containers(
                self, 
                resource_group_name: str, 
                account_name: str, 
                storage_account_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[StorageContainer]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                storage_account_name: str, 
                parameters: Optional[UpdateStorageAccountParameters] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                storage_account_name: str, 
                parameters: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...


namespace azure.mgmt.datalake.analytics.account.models

    class azure.mgmt.datalake.analytics.account.models.AADObjectType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        GROUP = "Group"
        SERVICE_PRINCIPAL = "ServicePrincipal"
        USER = "User"


    class azure.mgmt.datalake.analytics.account.models.AddDataLakeStoreParameters(Model):
        suffix: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                suffix: Optional[str] = ..., 
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


    class azure.mgmt.datalake.analytics.account.models.AddDataLakeStoreWithAccountParameters(Model):
        name: str
        suffix: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                name: str, 
                suffix: Optional[str] = ..., 
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


    class azure.mgmt.datalake.analytics.account.models.AddStorageAccountParameters(Model):
        access_key: str
        suffix: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                access_key: str, 
                suffix: str = "azuredatalakestore.net", 
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


    class azure.mgmt.datalake.analytics.account.models.AddStorageAccountWithAccountParameters(Model):
        access_key: str
        name: str
        suffix: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                access_key: str, 
                name: str, 
                suffix: str = "azuredatalakestore.net", 
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


    class azure.mgmt.datalake.analytics.account.models.CapabilityInformation(Model):
        account_count: int
        max_account_count: int
        migration_state: bool
        state: Union[str, SubscriptionState]
        subscription_id: str

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


    class azure.mgmt.datalake.analytics.account.models.CheckNameAvailabilityParameters(Model):
        name: str
        type: Union[str, CheckNameAvailabilityParametersType]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                name: str, 
                type: Union[str, CheckNameAvailabilityParametersType], 
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


    class azure.mgmt.datalake.analytics.account.models.CheckNameAvailabilityParametersType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MICROSOFT_DATA_LAKE_ANALYTICS_ACCOUNTS = "Microsoft.DataLakeAnalytics/accounts"


    class azure.mgmt.datalake.analytics.account.models.ComputePolicy(SubResource):
        id: str
        max_degree_of_parallelism_per_job: int
        min_priority_per_job: int
        name: str
        object_id: str
        object_type: Union[str, AADObjectType]
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


    class azure.mgmt.datalake.analytics.account.models.ComputePolicyListResult(Model):
        next_link: str
        value: list[ComputePolicy]

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


    class azure.mgmt.datalake.analytics.account.models.CreateComputePolicyWithAccountParameters(Model):
        max_degree_of_parallelism_per_job: int
        min_priority_per_job: int
        name: str
        object_id: str
        object_type: Union[str, AADObjectType]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                max_degree_of_parallelism_per_job: Optional[int] = ..., 
                min_priority_per_job: Optional[int] = ..., 
                name: str, 
                object_id: str, 
                object_type: Union[str, AADObjectType], 
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


    class azure.mgmt.datalake.analytics.account.models.CreateDataLakeAnalyticsAccountParameters(Model):
        compute_policies: list[CreateComputePolicyWithAccountParameters]
        data_lake_store_accounts: list[AddDataLakeStoreWithAccountParameters]
        default_data_lake_store_account: str
        firewall_allow_azure_ips: Union[str, FirewallAllowAzureIpsState]
        firewall_rules: list[CreateFirewallRuleWithAccountParameters]
        firewall_state: Union[str, FirewallState]
        location: str
        max_degree_of_parallelism: int
        max_degree_of_parallelism_per_job: int
        max_job_count: int
        min_priority_per_job: int
        new_tier: Union[str, TierType]
        query_store_retention: int
        storage_accounts: list[AddStorageAccountWithAccountParameters]
        tags: dict[str, str]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                compute_policies: Optional[List[CreateComputePolicyWithAccountParameters]] = ..., 
                data_lake_store_accounts: List[AddDataLakeStoreWithAccountParameters], 
                default_data_lake_store_account: str, 
                firewall_allow_azure_ips: Optional[Union[str, FirewallAllowAzureIpsState]] = ..., 
                firewall_rules: Optional[List[CreateFirewallRuleWithAccountParameters]] = ..., 
                firewall_state: Optional[Union[str, FirewallState]] = ..., 
                location: str, 
                max_degree_of_parallelism: int = 30, 
                max_degree_of_parallelism_per_job: int = 32, 
                max_job_count: int = 3, 
                min_priority_per_job: Optional[int] = ..., 
                new_tier: Optional[Union[str, TierType]] = ..., 
                query_store_retention: int = 30, 
                storage_accounts: Optional[List[AddStorageAccountWithAccountParameters]] = ..., 
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


    class azure.mgmt.datalake.analytics.account.models.CreateFirewallRuleWithAccountParameters(Model):
        end_ip_address: str
        name: str
        start_ip_address: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                end_ip_address: str, 
                name: str, 
                start_ip_address: str, 
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


    class azure.mgmt.datalake.analytics.account.models.CreateOrUpdateComputePolicyParameters(Model):
        max_degree_of_parallelism_per_job: int
        min_priority_per_job: int
        object_id: str
        object_type: Union[str, AADObjectType]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                max_degree_of_parallelism_per_job: Optional[int] = ..., 
                min_priority_per_job: Optional[int] = ..., 
                object_id: str, 
                object_type: Union[str, AADObjectType], 
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


    class azure.mgmt.datalake.analytics.account.models.CreateOrUpdateFirewallRuleParameters(Model):
        end_ip_address: str
        start_ip_address: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                end_ip_address: str, 
                start_ip_address: str, 
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


    class azure.mgmt.datalake.analytics.account.models.DataLakeAnalyticsAccount(Resource):
        account_id: str
        compute_policies: list[ComputePolicy]
        creation_time: datetime
        current_tier: Union[str, TierType]
        data_lake_store_accounts: list[DataLakeStoreAccountInformation]
        debug_data_access_level: Union[str, DebugDataAccessLevel]
        default_data_lake_store_account: str
        default_data_lake_store_account_type: str
        endpoint: str
        firewall_allow_azure_ips: Union[str, FirewallAllowAzureIpsState]
        firewall_rules: list[FirewallRule]
        firewall_state: Union[str, FirewallState]
        hive_metastores: list[HiveMetastore]
        id: str
        last_modified_time: datetime
        location: str
        max_active_job_count_per_user: int
        max_degree_of_parallelism: int
        max_degree_of_parallelism_per_job: int
        max_job_count: int
        max_job_running_time_in_min: int
        max_queued_job_count_per_user: int
        min_priority_per_job: int
        name: str
        new_tier: Union[str, TierType]
        provisioning_state: Union[str, DataLakeAnalyticsAccountStatus]
        public_data_lake_store_accounts: list[DataLakeStoreAccountInformation]
        query_store_retention: int
        state: Union[str, DataLakeAnalyticsAccountState]
        storage_accounts: list[StorageAccountInformation]
        system_max_degree_of_parallelism: int
        system_max_job_count: int
        tags: dict[str, str]
        type: str
        virtual_network_rules: list[VirtualNetworkRule]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                firewall_allow_azure_ips: Optional[Union[str, FirewallAllowAzureIpsState]] = ..., 
                firewall_state: Optional[Union[str, FirewallState]] = ..., 
                max_degree_of_parallelism: int = 30, 
                max_degree_of_parallelism_per_job: Optional[int] = ..., 
                max_job_count: int = 3, 
                new_tier: Optional[Union[str, TierType]] = ..., 
                public_data_lake_store_accounts: Optional[List[DataLakeStoreAccountInformation]] = ..., 
                query_store_retention: int = 30, 
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


    class azure.mgmt.datalake.analytics.account.models.DataLakeAnalyticsAccountBasic(Resource):
        account_id: str
        creation_time: datetime
        endpoint: str
        id: str
        last_modified_time: datetime
        location: str
        name: str
        provisioning_state: Union[str, DataLakeAnalyticsAccountStatus]
        state: Union[str, DataLakeAnalyticsAccountState]
        tags: dict[str, str]
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


    class azure.mgmt.datalake.analytics.account.models.DataLakeAnalyticsAccountListResult(Model):
        count: int
        next_link: str
        value: list[DataLakeAnalyticsAccountBasic]

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


    class azure.mgmt.datalake.analytics.account.models.DataLakeAnalyticsAccountProperties(DataLakeAnalyticsAccountPropertiesBasic):
        account_id: str
        compute_policies: list[ComputePolicy]
        creation_time: datetime
        current_tier: Union[str, TierType]
        data_lake_store_accounts: list[DataLakeStoreAccountInformation]
        debug_data_access_level: Union[str, DebugDataAccessLevel]
        default_data_lake_store_account: str
        default_data_lake_store_account_type: str
        endpoint: str
        firewall_allow_azure_ips: Union[str, FirewallAllowAzureIpsState]
        firewall_rules: list[FirewallRule]
        firewall_state: Union[str, FirewallState]
        hive_metastores: list[HiveMetastore]
        last_modified_time: datetime
        max_active_job_count_per_user: int
        max_degree_of_parallelism: int
        max_degree_of_parallelism_per_job: int
        max_job_count: int
        max_job_running_time_in_min: int
        max_queued_job_count_per_user: int
        min_priority_per_job: int
        new_tier: Union[str, TierType]
        provisioning_state: Union[str, DataLakeAnalyticsAccountStatus]
        public_data_lake_store_accounts: list[DataLakeStoreAccountInformation]
        query_store_retention: int
        state: Union[str, DataLakeAnalyticsAccountState]
        storage_accounts: list[StorageAccountInformation]
        system_max_degree_of_parallelism: int
        system_max_job_count: int
        virtual_network_rules: list[VirtualNetworkRule]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                firewall_allow_azure_ips: Optional[Union[str, FirewallAllowAzureIpsState]] = ..., 
                firewall_state: Optional[Union[str, FirewallState]] = ..., 
                max_degree_of_parallelism: int = 30, 
                max_degree_of_parallelism_per_job: Optional[int] = ..., 
                max_job_count: int = 3, 
                new_tier: Optional[Union[str, TierType]] = ..., 
                public_data_lake_store_accounts: Optional[List[DataLakeStoreAccountInformation]] = ..., 
                query_store_retention: int = 30, 
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


    class azure.mgmt.datalake.analytics.account.models.DataLakeAnalyticsAccountPropertiesBasic(Model):
        account_id: str
        creation_time: datetime
        endpoint: str
        last_modified_time: datetime
        provisioning_state: Union[str, DataLakeAnalyticsAccountStatus]
        state: Union[str, DataLakeAnalyticsAccountState]

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


    class azure.mgmt.datalake.analytics.account.models.DataLakeAnalyticsAccountState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        SUSPENDED = "Suspended"


    class azure.mgmt.datalake.analytics.account.models.DataLakeAnalyticsAccountStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETED = "Deleted"
        DELETING = "Deleting"
        FAILED = "Failed"
        PATCHING = "Patching"
        RESUMING = "Resuming"
        RUNNING = "Running"
        SUCCEEDED = "Succeeded"
        SUSPENDING = "Suspending"
        UNDELETING = "Undeleting"


    class azure.mgmt.datalake.analytics.account.models.DataLakeStoreAccountInformation(SubResource):
        id: str
        name: str
        suffix: str
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


    class azure.mgmt.datalake.analytics.account.models.DataLakeStoreAccountInformationListResult(Model):
        next_link: str
        value: list[DataLakeStoreAccountInformation]

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


    class azure.mgmt.datalake.analytics.account.models.DebugDataAccessLevel(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALL = "All"
        CUSTOMER = "Customer"
        NONE = "None"


    class azure.mgmt.datalake.analytics.account.models.ErrorAdditionalInfo(Model):
        info: JSON
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


    class azure.mgmt.datalake.analytics.account.models.ErrorDetail(Model):
        additional_info: list[ErrorAdditionalInfo]
        code: str
        details: list[ErrorDetail]
        message: str
        target: str

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


    class azure.mgmt.datalake.analytics.account.models.ErrorResponse(Model):
        error: ErrorDetail

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ..., 
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


    class azure.mgmt.datalake.analytics.account.models.FirewallAllowAzureIpsState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.datalake.analytics.account.models.FirewallRule(SubResource):
        end_ip_address: str
        id: str
        name: str
        start_ip_address: str
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


    class azure.mgmt.datalake.analytics.account.models.FirewallRuleListResult(Model):
        next_link: str
        value: list[FirewallRule]

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


    class azure.mgmt.datalake.analytics.account.models.FirewallState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.datalake.analytics.account.models.HiveMetastore(SubResource):
        database_name: str
        id: str
        name: str
        nested_resource_provisioning_state: Union[str, NestedResourceProvisioningState]
        password: str
        runtime_version: str
        server_uri: str
        type: str
        user_name: str

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


    class azure.mgmt.datalake.analytics.account.models.HiveMetastoreListResult(Model):
        next_link: str
        value: list[HiveMetastore]

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


    class azure.mgmt.datalake.analytics.account.models.NameAvailabilityInformation(Model):
        message: str
        name_available: bool
        reason: str

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


    class azure.mgmt.datalake.analytics.account.models.NestedResourceProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.datalake.analytics.account.models.Operation(Model):
        display: OperationDisplay
        name: str
        origin: Union[str, OperationOrigin]
        properties: OperationMetaPropertyInfo

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


    class azure.mgmt.datalake.analytics.account.models.OperationDisplay(Model):
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


    class azure.mgmt.datalake.analytics.account.models.OperationListResult(Model):
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


    class azure.mgmt.datalake.analytics.account.models.OperationMetaLogSpecification(Model):
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


    class azure.mgmt.datalake.analytics.account.models.OperationMetaMetricAvailabilitiesSpecification(Model):
        blob_duration: str
        time_grain: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                blob_duration: Optional[str] = ..., 
                time_grain: Optional[str] = ..., 
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


    class azure.mgmt.datalake.analytics.account.models.OperationMetaMetricSpecification(Model):
        aggregation_type: str
        availabilities: list[OperationMetaMetricAvailabilitiesSpecification]
        display_description: str
        display_name: str
        name: str
        unit: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                aggregation_type: Optional[str] = ..., 
                availabilities: Optional[List[OperationMetaMetricAvailabilitiesSpecification]] = ..., 
                display_description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                name: Optional[str] = ..., 
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


    class azure.mgmt.datalake.analytics.account.models.OperationMetaPropertyInfo(Model):
        service_specification: OperationMetaServiceSpecification

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
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


    class azure.mgmt.datalake.analytics.account.models.OperationMetaServiceSpecification(Model):
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


    class azure.mgmt.datalake.analytics.account.models.OperationOrigin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.datalake.analytics.account.models.Resource(Model):
        id: str
        location: str
        name: str
        tags: dict[str, str]
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


    class azure.mgmt.datalake.analytics.account.models.SasTokenInformation(Model):
        access_token: str

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


    class azure.mgmt.datalake.analytics.account.models.SasTokenInformationListResult(Model):
        next_link: str
        value: list[SasTokenInformation]

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


    class azure.mgmt.datalake.analytics.account.models.StorageAccountInformation(SubResource):
        id: str
        name: str
        suffix: str
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


    class azure.mgmt.datalake.analytics.account.models.StorageAccountInformationListResult(Model):
        next_link: str
        value: list[StorageAccountInformation]

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


    class azure.mgmt.datalake.analytics.account.models.StorageContainer(SubResource):
        id: str
        last_modified_time: datetime
        name: str
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


    class azure.mgmt.datalake.analytics.account.models.StorageContainerListResult(Model):
        next_link: str
        value: list[StorageContainer]

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


    class azure.mgmt.datalake.analytics.account.models.SubResource(Model):
        id: str
        name: str
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


    class azure.mgmt.datalake.analytics.account.models.SubscriptionState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DELETED = "Deleted"
        REGISTERED = "Registered"
        SUSPENDED = "Suspended"
        UNREGISTERED = "Unregistered"
        WARNED = "Warned"


    class azure.mgmt.datalake.analytics.account.models.TierType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMMITMENT100000_AU_HOURS = "Commitment_100000AUHours"
        COMMITMENT10000_AU_HOURS = "Commitment_10000AUHours"
        COMMITMENT1000_AU_HOURS = "Commitment_1000AUHours"
        COMMITMENT100_AU_HOURS = "Commitment_100AUHours"
        COMMITMENT500000_AU_HOURS = "Commitment_500000AUHours"
        COMMITMENT50000_AU_HOURS = "Commitment_50000AUHours"
        COMMITMENT5000_AU_HOURS = "Commitment_5000AUHours"
        COMMITMENT500_AU_HOURS = "Commitment_500AUHours"
        CONSUMPTION = "Consumption"


    class azure.mgmt.datalake.analytics.account.models.UpdateComputePolicyParameters(Model):
        max_degree_of_parallelism_per_job: int
        min_priority_per_job: int
        object_id: str
        object_type: Union[str, AADObjectType]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                max_degree_of_parallelism_per_job: Optional[int] = ..., 
                min_priority_per_job: Optional[int] = ..., 
                object_id: Optional[str] = ..., 
                object_type: Optional[Union[str, AADObjectType]] = ..., 
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


    class azure.mgmt.datalake.analytics.account.models.UpdateComputePolicyWithAccountParameters(Model):
        max_degree_of_parallelism_per_job: int
        min_priority_per_job: int
        name: str
        object_id: str
        object_type: Union[str, AADObjectType]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                max_degree_of_parallelism_per_job: Optional[int] = ..., 
                min_priority_per_job: Optional[int] = ..., 
                name: str, 
                object_id: Optional[str] = ..., 
                object_type: Optional[Union[str, AADObjectType]] = ..., 
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


    class azure.mgmt.datalake.analytics.account.models.UpdateDataLakeAnalyticsAccountParameters(Model):
        compute_policies: list[UpdateComputePolicyWithAccountParameters]
        data_lake_store_accounts: list[UpdateDataLakeStoreWithAccountParameters]
        firewall_allow_azure_ips: Union[str, FirewallAllowAzureIpsState]
        firewall_rules: list[UpdateFirewallRuleWithAccountParameters]
        firewall_state: Union[str, FirewallState]
        max_degree_of_parallelism: int
        max_degree_of_parallelism_per_job: int
        max_job_count: int
        min_priority_per_job: int
        new_tier: Union[str, TierType]
        query_store_retention: int
        storage_accounts: list[UpdateStorageAccountWithAccountParameters]
        tags: dict[str, str]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                compute_policies: Optional[List[UpdateComputePolicyWithAccountParameters]] = ..., 
                data_lake_store_accounts: Optional[List[UpdateDataLakeStoreWithAccountParameters]] = ..., 
                firewall_allow_azure_ips: Optional[Union[str, FirewallAllowAzureIpsState]] = ..., 
                firewall_rules: Optional[List[UpdateFirewallRuleWithAccountParameters]] = ..., 
                firewall_state: Optional[Union[str, FirewallState]] = ..., 
                max_degree_of_parallelism: Optional[int] = ..., 
                max_degree_of_parallelism_per_job: Optional[int] = ..., 
                max_job_count: Optional[int] = ..., 
                min_priority_per_job: Optional[int] = ..., 
                new_tier: Optional[Union[str, TierType]] = ..., 
                query_store_retention: Optional[int] = ..., 
                storage_accounts: Optional[List[UpdateStorageAccountWithAccountParameters]] = ..., 
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


    class azure.mgmt.datalake.analytics.account.models.UpdateDataLakeStoreWithAccountParameters(Model):
        name: str
        suffix: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                name: str, 
                suffix: Optional[str] = ..., 
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


    class azure.mgmt.datalake.analytics.account.models.UpdateFirewallRuleParameters(Model):
        end_ip_address: str
        start_ip_address: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                end_ip_address: Optional[str] = ..., 
                start_ip_address: Optional[str] = ..., 
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


    class azure.mgmt.datalake.analytics.account.models.UpdateFirewallRuleWithAccountParameters(Model):
        end_ip_address: str
        name: str
        start_ip_address: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                end_ip_address: Optional[str] = ..., 
                name: str, 
                start_ip_address: Optional[str] = ..., 
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


    class azure.mgmt.datalake.analytics.account.models.UpdateStorageAccountParameters(Model):
        access_key: str
        suffix: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                access_key: Optional[str] = ..., 
                suffix: Optional[str] = ..., 
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


    class azure.mgmt.datalake.analytics.account.models.UpdateStorageAccountWithAccountParameters(Model):
        access_key: str
        name: str
        suffix: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                access_key: Optional[str] = ..., 
                name: str, 
                suffix: Optional[str] = ..., 
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


    class azure.mgmt.datalake.analytics.account.models.VirtualNetworkRule(SubResource):
        id: str
        name: str
        subnet_id: str
        type: str
        virtual_network_rule_state: Union[str, VirtualNetworkRuleState]

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


    class azure.mgmt.datalake.analytics.account.models.VirtualNetworkRuleListResult(Model):
        next_link: str
        value: list[VirtualNetworkRule]

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


    class azure.mgmt.datalake.analytics.account.models.VirtualNetworkRuleState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        FAILED = "Failed"
        NETWORK_SOURCE_DELETED = "NetworkSourceDeleted"


namespace azure.mgmt.datalake.analytics.account.operations

    class azure.mgmt.datalake.analytics.account.operations.AccountsOperations:

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
                parameters: CreateDataLakeAnalyticsAccountParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DataLakeAnalyticsAccount]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DataLakeAnalyticsAccount]: ...

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
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                parameters: Optional[UpdateDataLakeAnalyticsAccountParameters] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DataLakeAnalyticsAccount]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                parameters: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DataLakeAnalyticsAccount]: ...

        @overload
        def check_name_availability(
                self, 
                location: str, 
                parameters: CheckNameAvailabilityParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> NameAvailabilityInformation: ...

        @overload
        def check_name_availability(
                self, 
                location: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> NameAvailabilityInformation: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> DataLakeAnalyticsAccount: ...

        @distributed_trace
        def list(
                self, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                skip: Optional[int] = None, 
                select: Optional[str] = None, 
                orderby: Optional[str] = None, 
                count: Optional[bool] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[DataLakeAnalyticsAccountBasic]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                skip: Optional[int] = None, 
                select: Optional[str] = None, 
                orderby: Optional[str] = None, 
                count: Optional[bool] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[DataLakeAnalyticsAccountBasic]: ...


    class azure.mgmt.datalake.analytics.account.operations.ComputePoliciesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                compute_policy_name: str, 
                parameters: CreateOrUpdateComputePolicyParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ComputePolicy: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                compute_policy_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ComputePolicy: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                compute_policy_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                compute_policy_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ComputePolicy: ...

        @distributed_trace
        def list_by_account(
                self, 
                resource_group_name: str, 
                account_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[ComputePolicy]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                compute_policy_name: str, 
                parameters: Optional[UpdateComputePolicyParameters] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ComputePolicy: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                compute_policy_name: str, 
                parameters: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ComputePolicy: ...


    class azure.mgmt.datalake.analytics.account.operations.DataLakeStoreAccountsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def add(
                self, 
                resource_group_name: str, 
                account_name: str, 
                data_lake_store_account_name: str, 
                parameters: Optional[AddDataLakeStoreParameters] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def add(
                self, 
                resource_group_name: str, 
                account_name: str, 
                data_lake_store_account_name: str, 
                parameters: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                data_lake_store_account_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                data_lake_store_account_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> DataLakeStoreAccountInformation: ...

        @distributed_trace
        def list_by_account(
                self, 
                resource_group_name: str, 
                account_name: str, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                skip: Optional[int] = None, 
                select: Optional[str] = None, 
                orderby: Optional[str] = None, 
                count: Optional[bool] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[DataLakeStoreAccountInformation]: ...


    class azure.mgmt.datalake.analytics.account.operations.FirewallRulesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                firewall_rule_name: str, 
                parameters: CreateOrUpdateFirewallRuleParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FirewallRule: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                firewall_rule_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FirewallRule: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                firewall_rule_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                firewall_rule_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> FirewallRule: ...

        @distributed_trace
        def list_by_account(
                self, 
                resource_group_name: str, 
                account_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[FirewallRule]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                firewall_rule_name: str, 
                parameters: Optional[UpdateFirewallRuleParameters] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FirewallRule: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                firewall_rule_name: str, 
                parameters: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FirewallRule: ...


    class azure.mgmt.datalake.analytics.account.operations.LocationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get_capability(
                self, 
                location: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Optional[CapabilityInformation]: ...


    class azure.mgmt.datalake.analytics.account.operations.Operations:

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


    class azure.mgmt.datalake.analytics.account.operations.StorageAccountsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def add(
                self, 
                resource_group_name: str, 
                account_name: str, 
                storage_account_name: str, 
                parameters: AddStorageAccountParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def add(
                self, 
                resource_group_name: str, 
                account_name: str, 
                storage_account_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                storage_account_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                storage_account_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> StorageAccountInformation: ...

        @distributed_trace
        def get_storage_container(
                self, 
                resource_group_name: str, 
                account_name: str, 
                storage_account_name: str, 
                container_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> StorageContainer: ...

        @distributed_trace
        def list_by_account(
                self, 
                resource_group_name: str, 
                account_name: str, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                skip: Optional[int] = None, 
                select: Optional[str] = None, 
                orderby: Optional[str] = None, 
                count: Optional[bool] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[StorageAccountInformation]: ...

        @distributed_trace
        def list_sas_tokens(
                self, 
                resource_group_name: str, 
                account_name: str, 
                storage_account_name: str, 
                container_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[SasTokenInformation]: ...

        @distributed_trace
        def list_storage_containers(
                self, 
                resource_group_name: str, 
                account_name: str, 
                storage_account_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[StorageContainer]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                storage_account_name: str, 
                parameters: Optional[UpdateStorageAccountParameters] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                storage_account_name: str, 
                parameters: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...


```