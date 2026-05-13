```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.azurearcdata

    class azure.mgmt.azurearcdata.AzureArcDataManagementClient: implements ContextManager 
        active_directory_connectors: ActiveDirectoryConnectorsOperations
        data_controllers: DataControllersOperations
        operations: Operations
        postgres_instances: PostgresInstancesOperations
        sql_managed_instances: SqlManagedInstancesOperations
        sql_server_instances: SqlServerInstancesOperations

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


namespace azure.mgmt.azurearcdata.aio

    class azure.mgmt.azurearcdata.aio.AzureArcDataManagementClient: implements AsyncContextManager 
        active_directory_connectors: ActiveDirectoryConnectorsOperations
        data_controllers: DataControllersOperations
        operations: Operations
        postgres_instances: PostgresInstancesOperations
        sql_managed_instances: SqlManagedInstancesOperations
        sql_server_instances: SqlServerInstancesOperations

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


namespace azure.mgmt.azurearcdata.aio.operations

    class azure.mgmt.azurearcdata.aio.operations.ActiveDirectoryConnectorsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                data_controller_name: str, 
                active_directory_connector_name: str, 
                active_directory_connector_resource: ActiveDirectoryConnectorResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ActiveDirectoryConnectorResource]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                data_controller_name: str, 
                active_directory_connector_name: str, 
                active_directory_connector_resource: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ActiveDirectoryConnectorResource]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                data_controller_name: str, 
                active_directory_connector_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                data_controller_name: str, 
                active_directory_connector_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ActiveDirectoryConnectorResource: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                data_controller_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[ActiveDirectoryConnectorResource]: ...


    class azure.mgmt.azurearcdata.aio.operations.DataControllersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_delete_data_controller(
                self, 
                resource_group_name: str, 
                data_controller_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_patch_data_controller(
                self, 
                resource_group_name: str, 
                data_controller_name: str, 
                data_controller_resource: DataControllerUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DataControllerResource]: ...

        @overload
        async def begin_patch_data_controller(
                self, 
                resource_group_name: str, 
                data_controller_name: str, 
                data_controller_resource: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DataControllerResource]: ...

        @overload
        async def begin_put_data_controller(
                self, 
                resource_group_name: str, 
                data_controller_name: str, 
                data_controller_resource: DataControllerResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DataControllerResource]: ...

        @overload
        async def begin_put_data_controller(
                self, 
                resource_group_name: str, 
                data_controller_name: str, 
                data_controller_resource: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DataControllerResource]: ...

        @distributed_trace_async
        async def get_data_controller(
                self, 
                resource_group_name: str, 
                data_controller_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> DataControllerResource: ...

        @distributed_trace
        def list_in_group(
                self, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[DataControllerResource]: ...

        @distributed_trace
        def list_in_subscription(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[DataControllerResource]: ...


    class azure.mgmt.azurearcdata.aio.operations.Operations:

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
            ) -> AsyncIterable[Operation]: ...


    class azure.mgmt.azurearcdata.aio.operations.PostgresInstancesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                postgres_instance_name: str, 
                resource: PostgresInstance, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PostgresInstance]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                postgres_instance_name: str, 
                resource: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PostgresInstance]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                postgres_instance_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                postgres_instance_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> PostgresInstance: ...

        @distributed_trace
        def list(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[PostgresInstance]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[PostgresInstance]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                postgres_instance_name: str, 
                parameters: PostgresInstanceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PostgresInstance: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                postgres_instance_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PostgresInstance: ...


    class azure.mgmt.azurearcdata.aio.operations.SqlManagedInstancesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                sql_managed_instance_name: str, 
                sql_managed_instance: SqlManagedInstance, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SqlManagedInstance]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                sql_managed_instance_name: str, 
                sql_managed_instance: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SqlManagedInstance]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                sql_managed_instance_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                sql_managed_instance_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> SqlManagedInstance: ...

        @distributed_trace
        def list(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[SqlManagedInstance]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[SqlManagedInstance]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                sql_managed_instance_name: str, 
                parameters: SqlManagedInstanceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SqlManagedInstance: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                sql_managed_instance_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SqlManagedInstance: ...


    class azure.mgmt.azurearcdata.aio.operations.SqlServerInstancesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                sql_server_instance: SqlServerInstance, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SqlServerInstance]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                sql_server_instance: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SqlServerInstance]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> SqlServerInstance: ...

        @distributed_trace
        def list(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[SqlServerInstance]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[SqlServerInstance]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                parameters: SqlServerInstanceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SqlServerInstance: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SqlServerInstance: ...


namespace azure.mgmt.azurearcdata.models

    class azure.mgmt.azurearcdata.models.AccountProvisioningMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTOMATIC = "automatic"
        MANUAL = "manual"


    class azure.mgmt.azurearcdata.models.ActiveDirectoryConnectorDNSDetails(Model):
        domain_name: str
        nameserver_ip_addresses: list[str]
        prefer_k8_s_dns_for_ptr_lookups: bool
        replicas: int

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                domain_name: Optional[str] = ..., 
                nameserver_ip_addresses: List[str], 
                prefer_k8_s_dns_for_ptr_lookups: bool = True, 
                replicas: int = 1, 
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


    class azure.mgmt.azurearcdata.models.ActiveDirectoryConnectorDomainDetails(Model):
        domain_controllers: ActiveDirectoryDomainControllers
        netbios_domain_name: str
        ou_distinguished_name: str
        realm: str
        service_account_provisioning: Union[str, AccountProvisioningMode]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                domain_controllers: ActiveDirectoryDomainControllers, 
                netbios_domain_name: Optional[str] = ..., 
                ou_distinguished_name: Optional[str] = ..., 
                realm: str, 
                service_account_provisioning: Union[str, AccountProvisioningMode] = "manual", 
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


    class azure.mgmt.azurearcdata.models.ActiveDirectoryConnectorListResult(Model):
        next_link: str
        value: list[ActiveDirectoryConnectorResource]

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


    class azure.mgmt.azurearcdata.models.ActiveDirectoryConnectorProperties(Model):
        domain_service_account_login_information: BasicLoginInformation
        provisioning_state: str
        spec: ActiveDirectoryConnectorSpec
        status: ActiveDirectoryConnectorStatus

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                domain_service_account_login_information: Optional[BasicLoginInformation] = ..., 
                spec: ActiveDirectoryConnectorSpec, 
                status: Optional[ActiveDirectoryConnectorStatus] = ..., 
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


    class azure.mgmt.azurearcdata.models.ActiveDirectoryConnectorResource(ProxyResource):
        id: str
        name: str
        properties: ActiveDirectoryConnectorProperties
        system_data: SystemData
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                properties: ActiveDirectoryConnectorProperties, 
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


    class azure.mgmt.azurearcdata.models.ActiveDirectoryConnectorSpec(Model):
        active_directory: ActiveDirectoryConnectorDomainDetails
        dns: ActiveDirectoryConnectorDNSDetails

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                active_directory: ActiveDirectoryConnectorDomainDetails, 
                dns: ActiveDirectoryConnectorDNSDetails, 
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


    class azure.mgmt.azurearcdata.models.ActiveDirectoryConnectorStatus(Model):
        additional_properties: dict[str, JSON]
        last_update_time: str
        observed_generation: int
        state: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                additional_properties: Optional[Dict[str, JSON]] = ..., 
                last_update_time: Optional[str] = ..., 
                observed_generation: Optional[int] = ..., 
                state: Optional[str] = ..., 
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


    class azure.mgmt.azurearcdata.models.ActiveDirectoryDomainController(Model):
        hostname: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                hostname: str, 
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


    class azure.mgmt.azurearcdata.models.ActiveDirectoryDomainControllers(Model):
        primary_domain_controller: ActiveDirectoryDomainController
        secondary_domain_controllers: list[ActiveDirectoryDomainController]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                primary_domain_controller: Optional[ActiveDirectoryDomainController] = ..., 
                secondary_domain_controllers: Optional[List[ActiveDirectoryDomainController]] = ..., 
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


    class azure.mgmt.azurearcdata.models.ActiveDirectoryInformation(Model):
        keytab_information: KeytabInformation

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                keytab_information: Optional[KeytabInformation] = ..., 
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


    class azure.mgmt.azurearcdata.models.ArcSqlManagedInstanceLicenseType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BASE_PRICE = "BasePrice"
        DISASTER_RECOVERY = "DisasterRecovery"
        LICENSE_INCLUDED = "LicenseIncluded"


    class azure.mgmt.azurearcdata.models.ArcSqlServerLicenseType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FREE = "Free"
        HADR = "HADR"
        LICENSE_ONLY = "LicenseOnly"
        PAID = "Paid"
        PAYG = "PAYG"
        SERVER_CAL = "ServerCAL"
        UNDEFINED = "Undefined"


    class azure.mgmt.azurearcdata.models.BasicLoginInformation(Model):
        password: str
        username: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                password: Optional[str] = ..., 
                username: Optional[str] = ..., 
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


    class azure.mgmt.azurearcdata.models.CommonSku(Model):
        capacity: int
        dev: bool
        family: str
        name: str
        size: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                capacity: Optional[int] = ..., 
                dev: bool = True, 
                family: Optional[str] = ..., 
                name: str, 
                size: Optional[str] = ..., 
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


    class azure.mgmt.azurearcdata.models.ConnectionStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONNECTED = "Connected"
        DISCONNECTED = "Disconnected"
        REGISTERED = "Registered"
        UNKNOWN = "Unknown"


    class azure.mgmt.azurearcdata.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.azurearcdata.models.DataControllerProperties(Model):
        basic_login_information: BasicLoginInformation
        cluster_id: str
        extension_id: str
        infrastructure: Union[str, Infrastructure]
        k8_s_raw: JSON
        last_uploaded_date: datetime
        log_analytics_workspace_config: LogAnalyticsWorkspaceConfig
        logs_dashboard_credential: BasicLoginInformation
        metrics_dashboard_credential: BasicLoginInformation
        on_premise_property: OnPremiseProperty
        provisioning_state: str
        upload_service_principal: UploadServicePrincipal
        upload_watermark: UploadWatermark

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                basic_login_information: Optional[BasicLoginInformation] = ..., 
                cluster_id: Optional[str] = ..., 
                extension_id: Optional[str] = ..., 
                infrastructure: Union[str, Infrastructure] = "other", 
                k8_s_raw: Optional[JSON] = ..., 
                last_uploaded_date: Optional[datetime] = ..., 
                log_analytics_workspace_config: Optional[LogAnalyticsWorkspaceConfig] = ..., 
                logs_dashboard_credential: Optional[BasicLoginInformation] = ..., 
                metrics_dashboard_credential: Optional[BasicLoginInformation] = ..., 
                on_premise_property: Optional[OnPremiseProperty] = ..., 
                upload_service_principal: Optional[UploadServicePrincipal] = ..., 
                upload_watermark: Optional[UploadWatermark] = ..., 
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


    class azure.mgmt.azurearcdata.models.DataControllerResource(TrackedResource):
        extended_location: ExtendedLocation
        id: str
        location: str
        name: str
        properties: DataControllerProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                extended_location: Optional[ExtendedLocation] = ..., 
                location: str, 
                properties: DataControllerProperties, 
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


    class azure.mgmt.azurearcdata.models.DataControllerUpdate(Model):
        properties: DataControllerProperties
        tags: dict[str, str]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                properties: Optional[DataControllerProperties] = ..., 
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


    class azure.mgmt.azurearcdata.models.DefenderStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PROTECTED = "Protected"
        UNKNOWN = "Unknown"
        UNPROTECTED = "Unprotected"


    class azure.mgmt.azurearcdata.models.EditionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEVELOPER = "Developer"
        ENTERPRISE = "Enterprise"
        EVALUATION = "Evaluation"
        EXPRESS = "Express"
        STANDARD = "Standard"
        WEB = "Web"


    class azure.mgmt.azurearcdata.models.ErrorResponse(Model):
        error: ErrorResponseBody

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                error: Optional[ErrorResponseBody] = ..., 
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


    class azure.mgmt.azurearcdata.models.ErrorResponseBody(Model):
        code: str
        details: list[ErrorResponseBody]
        message: str
        target: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                details: Optional[List[ErrorResponseBody]] = ..., 
                message: Optional[str] = ..., 
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


    class azure.mgmt.azurearcdata.models.ExtendedLocation(Model):
        name: str
        type: Union[str, ExtendedLocationTypes]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                type: Optional[Union[str, ExtendedLocationTypes]] = ..., 
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


    class azure.mgmt.azurearcdata.models.ExtendedLocationTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CUSTOM_LOCATION = "CustomLocation"


    class azure.mgmt.azurearcdata.models.HostType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AWS_KUBERNETES_SERVICE = "AWS Kubernetes Service"
        AWS_VIRTUAL_MACHINE = "AWS Virtual Machine"
        AWS_VM_WARE_VIRTUAL_MACHINE = "AWS VMWare Virtual Machine"
        AZURE_KUBERNETES_SERVICE = "Azure Kubernetes Service"
        AZURE_VIRTUAL_MACHINE = "Azure Virtual Machine"
        AZURE_VM_WARE_VIRTUAL_MACHINE = "Azure VMWare Virtual Machine"
        CONTAINER = "Container"
        GCP_KUBERNETES_SERVICE = "GCP Kubernetes Service"
        GCP_VIRTUAL_MACHINE = "GCP Virtual Machine"
        GCP_VM_WARE_VIRTUAL_MACHINE = "GCP VMWare Virtual Machine"
        OTHER = "Other"
        PHYSICAL_SERVER = "Physical Server"
        VIRTUAL_MACHINE = "Virtual Machine"


    class azure.mgmt.azurearcdata.models.Infrastructure(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALIBABA = "alibaba"
        AWS = "aws"
        AZURE = "azure"
        GCP = "gcp"
        ONPREMISES = "onpremises"
        OTHER = "other"


    class azure.mgmt.azurearcdata.models.K8SResourceRequirements(Model):
        additional_properties: dict[str, JSON]
        limits: dict[str, str]
        requests: dict[str, str]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                additional_properties: Optional[Dict[str, JSON]] = ..., 
                limits: Optional[Dict[str, str]] = ..., 
                requests: Optional[Dict[str, str]] = ..., 
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


    class azure.mgmt.azurearcdata.models.K8SScheduling(Model):
        additional_properties: dict[str, JSON]
        default: K8SSchedulingOptions

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                additional_properties: Optional[Dict[str, JSON]] = ..., 
                default: Optional[K8SSchedulingOptions] = ..., 
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


    class azure.mgmt.azurearcdata.models.K8SSchedulingOptions(Model):
        additional_properties: dict[str, JSON]
        resources: K8SResourceRequirements

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                additional_properties: Optional[Dict[str, JSON]] = ..., 
                resources: Optional[K8SResourceRequirements] = ..., 
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


    class azure.mgmt.azurearcdata.models.KeytabInformation(Model):
        keytab: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                keytab: Optional[str] = ..., 
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


    class azure.mgmt.azurearcdata.models.LogAnalyticsWorkspaceConfig(Model):
        primary_key: str
        workspace_id: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                primary_key: Optional[str] = ..., 
                workspace_id: Optional[str] = ..., 
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


    class azure.mgmt.azurearcdata.models.OnPremiseProperty(Model):
        id: str
        public_signing_key: str
        signing_certificate_thumbprint: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                id: str, 
                public_signing_key: str, 
                signing_certificate_thumbprint: Optional[str] = ..., 
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


    class azure.mgmt.azurearcdata.models.Operation(Model):
        display: OperationDisplay
        is_data_action: bool
        name: str
        origin: Union[str, OperationOrigin]
        properties: dict[str, JSON]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                display: OperationDisplay, 
                is_data_action: bool, 
                name: str, 
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


    class azure.mgmt.azurearcdata.models.OperationDisplay(Model):
        description: str
        operation: str
        provider: str
        resource: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                description: str, 
                operation: str, 
                provider: str, 
                resource: str, 
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


    class azure.mgmt.azurearcdata.models.OperationListResult(Model):
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


    class azure.mgmt.azurearcdata.models.OperationOrigin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"


    class azure.mgmt.azurearcdata.models.PageOfDataControllerResource(Model):
        next_link: str
        value: list[DataControllerResource]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[DataControllerResource]] = ..., 
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


    class azure.mgmt.azurearcdata.models.PostgresInstance(TrackedResource):
        extended_location: ExtendedLocation
        id: str
        location: str
        name: str
        properties: PostgresInstanceProperties
        sku: PostgresInstanceSku
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                extended_location: Optional[ExtendedLocation] = ..., 
                location: str, 
                properties: PostgresInstanceProperties, 
                sku: Optional[PostgresInstanceSku] = ..., 
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


    class azure.mgmt.azurearcdata.models.PostgresInstanceListResult(Model):
        next_link: str
        value: list[PostgresInstance]

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


    class azure.mgmt.azurearcdata.models.PostgresInstanceProperties(Model):
        admin: str
        basic_login_information: BasicLoginInformation
        data_controller_id: str
        k8_s_raw: JSON
        last_uploaded_date: datetime
        provisioning_state: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                admin: Optional[str] = ..., 
                basic_login_information: Optional[BasicLoginInformation] = ..., 
                data_controller_id: Optional[str] = ..., 
                k8_s_raw: Optional[JSON] = ..., 
                last_uploaded_date: Optional[datetime] = ..., 
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


    class azure.mgmt.azurearcdata.models.PostgresInstanceSku(CommonSku):
        capacity: int
        dev: bool
        family: str
        name: str
        size: str
        tier: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                capacity: Optional[int] = ..., 
                dev: bool = True, 
                family: Optional[str] = ..., 
                name: str, 
                size: Optional[str] = ..., 
                tier: Literal["Hyperscale"] = "Hyperscale", 
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


    class azure.mgmt.azurearcdata.models.PostgresInstanceUpdate(Model):
        properties: PostgresInstanceProperties
        tags: dict[str, str]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                properties: Optional[PostgresInstanceProperties] = ..., 
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


    class azure.mgmt.azurearcdata.models.ProxyResource(Resource):
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


    class azure.mgmt.azurearcdata.models.Resource(Model):
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


    class azure.mgmt.azurearcdata.models.SqlManagedInstance(TrackedResource):
        extended_location: ExtendedLocation
        id: str
        location: str
        name: str
        properties: SqlManagedInstanceProperties
        sku: SqlManagedInstanceSku
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                extended_location: Optional[ExtendedLocation] = ..., 
                location: str, 
                properties: SqlManagedInstanceProperties, 
                sku: Optional[SqlManagedInstanceSku] = ..., 
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


    class azure.mgmt.azurearcdata.models.SqlManagedInstanceK8SRaw(Model):
        additional_properties: dict[str, JSON]
        spec: SqlManagedInstanceK8SSpec

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                additional_properties: Optional[Dict[str, JSON]] = ..., 
                spec: Optional[SqlManagedInstanceK8SSpec] = ..., 
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


    class azure.mgmt.azurearcdata.models.SqlManagedInstanceK8SSpec(Model):
        additional_properties: dict[str, JSON]
        replicas: int
        scheduling: K8SScheduling

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                additional_properties: Optional[Dict[str, JSON]] = ..., 
                replicas: Optional[int] = ..., 
                scheduling: Optional[K8SScheduling] = ..., 
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


    class azure.mgmt.azurearcdata.models.SqlManagedInstanceListResult(Model):
        next_link: str
        value: list[SqlManagedInstance]

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


    class azure.mgmt.azurearcdata.models.SqlManagedInstanceProperties(Model):
        active_directory_information: ActiveDirectoryInformation
        admin: str
        basic_login_information: BasicLoginInformation
        cluster_id: str
        data_controller_id: str
        end_time: str
        extension_id: str
        k8_s_raw: SqlManagedInstanceK8SRaw
        last_uploaded_date: datetime
        license_type: Union[str, ArcSqlManagedInstanceLicenseType]
        provisioning_state: str
        start_time: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                active_directory_information: Optional[ActiveDirectoryInformation] = ..., 
                admin: Optional[str] = ..., 
                basic_login_information: Optional[BasicLoginInformation] = ..., 
                cluster_id: Optional[str] = ..., 
                data_controller_id: Optional[str] = ..., 
                end_time: Optional[str] = ..., 
                extension_id: Optional[str] = ..., 
                k8_s_raw: Optional[SqlManagedInstanceK8SRaw] = ..., 
                last_uploaded_date: Optional[datetime] = ..., 
                license_type: Union[str, ArcSqlManagedInstanceLicenseType] = "BasePrice", 
                start_time: Optional[str] = ..., 
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


    class azure.mgmt.azurearcdata.models.SqlManagedInstanceSku(Model):
        capacity: int
        dev: bool
        family: str
        name: str = "vCore"
        size: str
        tier: Union[str, SqlManagedInstanceSkuTier]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                capacity: Optional[int] = ..., 
                dev: bool = True, 
                family: Optional[str] = ..., 
                size: Optional[str] = ..., 
                tier: Union[str, SqlManagedInstanceSkuTier] = "GeneralPurpose", 
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


    class azure.mgmt.azurearcdata.models.SqlManagedInstanceSkuTier(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BUSINESS_CRITICAL = "BusinessCritical"
        GENERAL_PURPOSE = "GeneralPurpose"


    class azure.mgmt.azurearcdata.models.SqlManagedInstanceUpdate(Model):
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


    class azure.mgmt.azurearcdata.models.SqlServerInstance(TrackedResource):
        id: str
        location: str
        name: str
        properties: SqlServerInstanceProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[SqlServerInstanceProperties] = ..., 
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


    class azure.mgmt.azurearcdata.models.SqlServerInstanceListResult(Model):
        next_link: str
        value: list[SqlServerInstance]

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


    class azure.mgmt.azurearcdata.models.SqlServerInstanceProperties(Model):
        azure_defender_status: Union[str, DefenderStatus]
        azure_defender_status_last_updated: datetime
        collation: str
        container_resource_id: str
        create_time: str
        current_version: str
        edition: Union[str, EditionType]
        host_type: Union[str, HostType]
        instance_name: str
        license_type: Union[str, ArcSqlServerLicenseType]
        patch_level: str
        product_id: str
        provisioning_state: str
        status: Union[str, ConnectionStatus]
        tcp_dynamic_ports: str
        tcp_static_ports: str
        v_core: str
        version: Union[str, SqlVersion]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                azure_defender_status: Optional[Union[str, DefenderStatus]] = ..., 
                azure_defender_status_last_updated: Optional[datetime] = ..., 
                collation: Optional[str] = ..., 
                container_resource_id: str, 
                current_version: Optional[str] = ..., 
                edition: Optional[Union[str, EditionType]] = ..., 
                host_type: Optional[Union[str, HostType]] = ..., 
                instance_name: Optional[str] = ..., 
                license_type: Optional[Union[str, ArcSqlServerLicenseType]] = ..., 
                patch_level: Optional[str] = ..., 
                product_id: Optional[str] = ..., 
                status: Union[str, ConnectionStatus], 
                tcp_dynamic_ports: Optional[str] = ..., 
                tcp_static_ports: Optional[str] = ..., 
                v_core: Optional[str] = ..., 
                version: Optional[Union[str, SqlVersion]] = ..., 
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


    class azure.mgmt.azurearcdata.models.SqlServerInstanceUpdate(Model):
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


    class azure.mgmt.azurearcdata.models.SqlVersion(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SQL_SERVER2012 = "SQL Server 2012"
        SQL_SERVER2014 = "SQL Server 2014"
        SQL_SERVER2016 = "SQL Server 2016"
        SQL_SERVER2017 = "SQL Server 2017"
        SQL_SERVER2019 = "SQL Server 2019"
        SQL_SERVER2022 = "SQL Server 2022"
        UNKNOWN = "Unknown"


    class azure.mgmt.azurearcdata.models.SystemData(Model):
        created_at: datetime
        created_by: str
        created_by_type: Union[str, CreatedByType]
        last_modified_at: datetime
        last_modified_by: str
        last_modified_by_type: Union[str, CreatedByType]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                created_at: Optional[datetime] = ..., 
                created_by: Optional[str] = ..., 
                created_by_type: Optional[Union[str, CreatedByType]] = ..., 
                last_modified_at: Optional[datetime] = ..., 
                last_modified_by: Optional[str] = ..., 
                last_modified_by_type: Optional[Union[str, CreatedByType]] = ..., 
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


    class azure.mgmt.azurearcdata.models.TrackedResource(Resource):
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
                location: str, 
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


    class azure.mgmt.azurearcdata.models.UploadServicePrincipal(Model):
        authority: str
        client_id: str
        client_secret: str
        tenant_id: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                authority: Optional[str] = ..., 
                client_id: Optional[str] = ..., 
                client_secret: Optional[str] = ..., 
                tenant_id: Optional[str] = ..., 
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


    class azure.mgmt.azurearcdata.models.UploadWatermark(Model):
        logs: datetime
        metrics: datetime
        usages: datetime

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                logs: Optional[datetime] = ..., 
                metrics: Optional[datetime] = ..., 
                usages: Optional[datetime] = ..., 
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


namespace azure.mgmt.azurearcdata.operations

    class azure.mgmt.azurearcdata.operations.ActiveDirectoryConnectorsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                data_controller_name: str, 
                active_directory_connector_name: str, 
                active_directory_connector_resource: ActiveDirectoryConnectorResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ActiveDirectoryConnectorResource]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                data_controller_name: str, 
                active_directory_connector_name: str, 
                active_directory_connector_resource: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ActiveDirectoryConnectorResource]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                data_controller_name: str, 
                active_directory_connector_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                data_controller_name: str, 
                active_directory_connector_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ActiveDirectoryConnectorResource: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                data_controller_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[ActiveDirectoryConnectorResource]: ...


    class azure.mgmt.azurearcdata.operations.DataControllersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def begin_delete_data_controller(
                self, 
                resource_group_name: str, 
                data_controller_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_patch_data_controller(
                self, 
                resource_group_name: str, 
                data_controller_name: str, 
                data_controller_resource: DataControllerUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DataControllerResource]: ...

        @overload
        def begin_patch_data_controller(
                self, 
                resource_group_name: str, 
                data_controller_name: str, 
                data_controller_resource: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DataControllerResource]: ...

        @overload
        def begin_put_data_controller(
                self, 
                resource_group_name: str, 
                data_controller_name: str, 
                data_controller_resource: DataControllerResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DataControllerResource]: ...

        @overload
        def begin_put_data_controller(
                self, 
                resource_group_name: str, 
                data_controller_name: str, 
                data_controller_resource: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DataControllerResource]: ...

        @distributed_trace
        def get_data_controller(
                self, 
                resource_group_name: str, 
                data_controller_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> DataControllerResource: ...

        @distributed_trace
        def list_in_group(
                self, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[DataControllerResource]: ...

        @distributed_trace
        def list_in_subscription(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[DataControllerResource]: ...


    class azure.mgmt.azurearcdata.operations.Operations:

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
            ) -> Iterable[Operation]: ...


    class azure.mgmt.azurearcdata.operations.PostgresInstancesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                postgres_instance_name: str, 
                resource: PostgresInstance, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PostgresInstance]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                postgres_instance_name: str, 
                resource: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PostgresInstance]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                postgres_instance_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                postgres_instance_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> PostgresInstance: ...

        @distributed_trace
        def list(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[PostgresInstance]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[PostgresInstance]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                postgres_instance_name: str, 
                parameters: PostgresInstanceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PostgresInstance: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                postgres_instance_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PostgresInstance: ...


    class azure.mgmt.azurearcdata.operations.SqlManagedInstancesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                sql_managed_instance_name: str, 
                sql_managed_instance: SqlManagedInstance, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SqlManagedInstance]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                sql_managed_instance_name: str, 
                sql_managed_instance: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SqlManagedInstance]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                sql_managed_instance_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                sql_managed_instance_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> SqlManagedInstance: ...

        @distributed_trace
        def list(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[SqlManagedInstance]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[SqlManagedInstance]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                sql_managed_instance_name: str, 
                parameters: SqlManagedInstanceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SqlManagedInstance: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                sql_managed_instance_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SqlManagedInstance: ...


    class azure.mgmt.azurearcdata.operations.SqlServerInstancesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                sql_server_instance: SqlServerInstance, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SqlServerInstance]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                sql_server_instance: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SqlServerInstance]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> SqlServerInstance: ...

        @distributed_trace
        def list(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[SqlServerInstance]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[SqlServerInstance]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                parameters: SqlServerInstanceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SqlServerInstance: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SqlServerInstance: ...


```