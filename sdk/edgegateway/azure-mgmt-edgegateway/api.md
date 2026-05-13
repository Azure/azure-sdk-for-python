```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.edgegateway

    class azure.mgmt.edgegateway.DataBoxEdgeManagementClient(SDKClient):
        alerts: AlertsOperations
        bandwidth_schedules: BandwidthSchedulesOperations
        config: DataBoxEdgeManagementClientConfiguration
        devices: DevicesOperations
        jobs: JobsOperations
        operations: Operations
        operations_status: OperationsStatusOperations
        orders: OrdersOperations
        roles: RolesOperations
        shares: SharesOperations
        storage_account_credentials: StorageAccountCredentialsOperations
        triggers: TriggersOperations
        users: UsersOperations

        def __init__(
                self, 
                credentials: :mod:A msrestazure Credentials, 
                subscription_id: str, 
                base_url: str = None
            ): ...


namespace azure.mgmt.edgegateway.data_box_edge_management_client

    class azure.mgmt.edgegateway.data_box_edge_management_client.AlertsOperations:
        api_version

        def __init__(
                self, 
                client, 
                config, 
                serializer, 
                deserializer
            ): ...

        def get(
                self, 
                device_name: str, 
                name: str, 
                resource_group_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[Alert, ClientRawResponse]: ...

        def list_by_data_box_edge_device(
                self, 
                device_name: str, 
                resource_group_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> AlertPaged[Alert]: ...


    class azure.mgmt.edgegateway.data_box_edge_management_client.BandwidthSchedulesOperations:
        api_version

        def __init__(
                self, 
                client, 
                config, 
                serializer, 
                deserializer
            ): ...

        def create_or_update(
                self, 
                device_name: str, 
                name: str, 
                parameters: BandwidthSchedule, 
                resource_group_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                polling = True, 
                **operation_config
            ) -> AzureOperationPoller[BandwidthSchedule]: ...

        def delete(
                self, 
                device_name: str, 
                name: str, 
                resource_group_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                polling = True, 
                **operation_config
            ) -> Union[AzureOperationPoller[None], AzureOperationPoller[ClientRawResponse[None]]]: ...

        def get(
                self, 
                device_name: str, 
                name: str, 
                resource_group_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[BandwidthSchedule, ClientRawResponse]: ...

        def list_by_data_box_edge_device(
                self, 
                device_name: str, 
                resource_group_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> BandwidthSchedulePaged[BandwidthSchedule]: ...


    class azure.mgmt.edgegateway.data_box_edge_management_client.DataBoxEdgeManagementClient(SDKClient):
        alerts: AlertsOperations
        bandwidth_schedules: BandwidthSchedulesOperations
        config: DataBoxEdgeManagementClientConfiguration
        devices: DevicesOperations
        jobs: JobsOperations
        operations: Operations
        operations_status: OperationsStatusOperations
        orders: OrdersOperations
        roles: RolesOperations
        shares: SharesOperations
        storage_account_credentials: StorageAccountCredentialsOperations
        triggers: TriggersOperations
        users: UsersOperations

        def __init__(
                self, 
                credentials: :mod:A msrestazure Credentials, 
                subscription_id: str, 
                base_url: str = None
            ): ...


    class azure.mgmt.edgegateway.data_box_edge_management_client.DataBoxEdgeManagementClientConfiguration(AzureConfiguration):
        property enable_http_logger: 
        property user_agent: str    # Read-only

        def __init__(
                self, 
                credentials: :mod:A msrestazure Credentials, 
                subscription_id: str, 
                base_url: str = None
            ): ...


    class azure.mgmt.edgegateway.data_box_edge_management_client.DevicesOperations:
        api_version

        def __init__(
                self, 
                client, 
                config, 
                serializer, 
                deserializer
            ): ...

        def create_or_update(
                self, 
                device_name: str, 
                data_box_edge_device: DataBoxEdgeDevice, 
                resource_group_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                polling = True, 
                **operation_config
            ) -> AzureOperationPoller[DataBoxEdgeDevice]: ...

        def create_or_update_security_settings(
                self, 
                device_name: str, 
                resource_group_name: str, 
                device_admin_password: AsymmetricEncryptedSecret, 
                custom_headers: dict = None, 
                raw: bool = False, 
                polling = True, 
                **operation_config
            ) -> Union[AzureOperationPoller[None], AzureOperationPoller[ClientRawResponse[None]]]: ...

        def delete(
                self, 
                device_name: str, 
                resource_group_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                polling = True, 
                **operation_config
            ) -> Union[AzureOperationPoller[None], AzureOperationPoller[ClientRawResponse[None]]]: ...

        def download_updates(
                self, 
                device_name: str, 
                resource_group_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                polling = True, 
                **operation_config
            ) -> Union[AzureOperationPoller[None], AzureOperationPoller[ClientRawResponse[None]]]: ...

        def get(
                self, 
                device_name: str, 
                resource_group_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[DataBoxEdgeDevice, ClientRawResponse]: ...

        def get_extended_information(
                self, 
                device_name: str, 
                resource_group_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> DataBoxEdgeDeviceExtendedInfo: ...

        def get_network_settings(
                self, 
                device_name: str, 
                resource_group_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[NetworkSettings, ClientRawResponse]: ...

        def get_update_summary(
                self, 
                device_name: str, 
                resource_group_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[UpdateSummary, ClientRawResponse]: ...

        def install_updates(
                self, 
                device_name: str, 
                resource_group_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                polling = True, 
                **operation_config
            ) -> Union[AzureOperationPoller[None], AzureOperationPoller[ClientRawResponse[None]]]: ...

        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                expand: str = None, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> DataBoxEdgeDevicePaged[DataBoxEdgeDevice]: ...

        def list_by_subscription(
                self, 
                expand: str = None, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> DataBoxEdgeDevicePaged[DataBoxEdgeDevice]: ...

        def scan_for_updates(
                self, 
                device_name: str, 
                resource_group_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                polling = True, 
                **operation_config
            ) -> Union[AzureOperationPoller[None], AzureOperationPoller[ClientRawResponse[None]]]: ...

        def update(
                self, 
                device_name: str, 
                resource_group_name: str, 
                tags: dict[str, str] = None, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[DataBoxEdgeDevice, ClientRawResponse]: ...

        def upload_certificate(
                self, 
                device_name: str, 
                resource_group_name: str, 
                certificate: str, 
                authentication_type: Union[str, AuthenticationType] = None, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[UploadCertificateResponse, ClientRawResponse]: ...


    class azure.mgmt.edgegateway.data_box_edge_management_client.JobsOperations:
        api_version

        def __init__(
                self, 
                client, 
                config, 
                serializer, 
                deserializer
            ): ...

        def get(
                self, 
                device_name: str, 
                name: str, 
                resource_group_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[Job, ClientRawResponse]: ...


    class azure.mgmt.edgegateway.data_box_edge_management_client.Operations:
        api_version

        def __init__(
                self, 
                client, 
                config, 
                serializer, 
                deserializer
            ): ...

        def list(
                self, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> OperationPaged[Operation]: ...


    class azure.mgmt.edgegateway.data_box_edge_management_client.OperationsStatusOperations:
        api_version

        def __init__(
                self, 
                client, 
                config, 
                serializer, 
                deserializer
            ): ...

        def get(
                self, 
                device_name: str, 
                name: str, 
                resource_group_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[Job, ClientRawResponse]: ...


    class azure.mgmt.edgegateway.data_box_edge_management_client.OrdersOperations:
        api_version

        def __init__(
                self, 
                client, 
                config, 
                serializer, 
                deserializer
            ): ...

        def create_or_update(
                self, 
                device_name: str, 
                order: Order, 
                resource_group_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                polling = True, 
                **operation_config
            ) -> AzureOperationPoller[Order]: ...

        def delete(
                self, 
                device_name: str, 
                resource_group_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                polling = True, 
                **operation_config
            ) -> Union[AzureOperationPoller[None], AzureOperationPoller[ClientRawResponse[None]]]: ...

        def get(
                self, 
                device_name: str, 
                resource_group_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[Order, ClientRawResponse]: ...

        def list_by_data_box_edge_device(
                self, 
                device_name: str, 
                resource_group_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> OrderPaged[Order]: ...


    class azure.mgmt.edgegateway.data_box_edge_management_client.RolesOperations:
        api_version

        def __init__(
                self, 
                client, 
                config, 
                serializer, 
                deserializer
            ): ...

        def create_or_update(
                self, 
                device_name: str, 
                name: str, 
                role: Role, 
                resource_group_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                polling = True, 
                **operation_config
            ) -> AzureOperationPoller[Role]: ...

        def delete(
                self, 
                device_name: str, 
                name: str, 
                resource_group_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                polling = True, 
                **operation_config
            ) -> Union[AzureOperationPoller[None], AzureOperationPoller[ClientRawResponse[None]]]: ...

        def get(
                self, 
                device_name: str, 
                name: str, 
                resource_group_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[Role, ClientRawResponse]: ...

        def list_by_data_box_edge_device(
                self, 
                device_name: str, 
                resource_group_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> RolePaged[Role]: ...


    class azure.mgmt.edgegateway.data_box_edge_management_client.SharesOperations:
        api_version

        def __init__(
                self, 
                client, 
                config, 
                serializer, 
                deserializer
            ): ...

        def create_or_update(
                self, 
                device_name: str, 
                name: str, 
                share: Share, 
                resource_group_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                polling = True, 
                **operation_config
            ) -> AzureOperationPoller[Share]: ...

        def delete(
                self, 
                device_name: str, 
                name: str, 
                resource_group_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                polling = True, 
                **operation_config
            ) -> Union[AzureOperationPoller[None], AzureOperationPoller[ClientRawResponse[None]]]: ...

        def get(
                self, 
                device_name: str, 
                name: str, 
                resource_group_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[Share, ClientRawResponse]: ...

        def list_by_data_box_edge_device(
                self, 
                device_name: str, 
                resource_group_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> SharePaged[Share]: ...

        def refresh(
                self, 
                device_name: str, 
                name: str, 
                resource_group_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                polling = True, 
                **operation_config
            ) -> Union[AzureOperationPoller[None], AzureOperationPoller[ClientRawResponse[None]]]: ...


    class azure.mgmt.edgegateway.data_box_edge_management_client.StorageAccountCredentialsOperations:
        api_version

        def __init__(
                self, 
                client, 
                config, 
                serializer, 
                deserializer
            ): ...

        def create_or_update(
                self, 
                device_name: str, 
                name: str, 
                storage_account_credential: StorageAccountCredential, 
                resource_group_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                polling = True, 
                **operation_config
            ) -> AzureOperationPoller[StorageAccountCredential]: ...

        def delete(
                self, 
                device_name: str, 
                name: str, 
                resource_group_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                polling = True, 
                **operation_config
            ) -> Union[AzureOperationPoller[None], AzureOperationPoller[ClientRawResponse[None]]]: ...

        def get(
                self, 
                device_name: str, 
                name: str, 
                resource_group_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[StorageAccountCredential, ClientRawResponse]: ...

        def list_by_data_box_edge_device(
                self, 
                device_name: str, 
                resource_group_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> StorageAccountCredentialPaged[StorageAccountCredential]: ...


    class azure.mgmt.edgegateway.data_box_edge_management_client.TriggersOperations:
        api_version

        def __init__(
                self, 
                client, 
                config, 
                serializer, 
                deserializer
            ): ...

        def create_or_update(
                self, 
                device_name: str, 
                name: str, 
                trigger: Trigger, 
                resource_group_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                polling = True, 
                **operation_config
            ) -> AzureOperationPoller[Trigger]: ...

        def delete(
                self, 
                device_name: str, 
                name: str, 
                resource_group_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                polling = True, 
                **operation_config
            ) -> Union[AzureOperationPoller[None], AzureOperationPoller[ClientRawResponse[None]]]: ...

        def get(
                self, 
                device_name: str, 
                name: str, 
                resource_group_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[Trigger, ClientRawResponse]: ...

        def list_by_data_box_edge_device(
                self, 
                device_name: str, 
                resource_group_name: str, 
                expand: str = None, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> TriggerPaged[Trigger]: ...


    class azure.mgmt.edgegateway.data_box_edge_management_client.UsersOperations:
        api_version

        def __init__(
                self, 
                client, 
                config, 
                serializer, 
                deserializer
            ): ...

        def create_or_update(
                self, 
                device_name: str, 
                name: str, 
                resource_group_name: str, 
                encrypted_password: AsymmetricEncryptedSecret = None, 
                share_access_rights: list[ShareAccessRight] = None, 
                custom_headers: dict = None, 
                raw: bool = False, 
                polling = True, 
                **operation_config
            ) -> AzureOperationPoller[User]: ...

        def delete(
                self, 
                device_name: str, 
                name: str, 
                resource_group_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                polling = True, 
                **operation_config
            ) -> Union[AzureOperationPoller[None], AzureOperationPoller[ClientRawResponse[None]]]: ...

        def get(
                self, 
                device_name: str, 
                name: str, 
                resource_group_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[User, ClientRawResponse]: ...

        def list_by_data_box_edge_device(
                self, 
                device_name: str, 
                resource_group_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> UserPaged[User]: ...


namespace azure.mgmt.edgegateway.models

    class azure.mgmt.edgegateway.models.ARMBaseModel(Model):
        id: str
        name: str
        type: str

        def __init__(self, **kwargs) -> None: ...


    class azure.mgmt.edgegateway.models.AccountType(str, Enum):
        blob_storage = "BlobStorage"
        general_purpose_storage = "GeneralPurposeStorage"


    class azure.mgmt.edgegateway.models.Address(Model):

        def __init__(
                self, 
                *, 
                address_line1: str, 
                address_line2: str = ..., 
                address_line3: str = ..., 
                city: str, 
                country: str, 
                postal_code: str, 
                state: str, 
                **kwargs
            ) -> None: ...


    class azure.mgmt.edgegateway.models.Alert(ARMBaseModel):
        alert_type: str
        appeared_at_date_time: datetime
        detailed_information: dict[str, str]
        error_details: AlertErrorDetails
        id: str
        name: str
        recommendation: str
        severity: Union[str, AlertSeverity]
        title: str
        type: str

        def __init__(self, **kwargs) -> None: ...


    class azure.mgmt.edgegateway.models.AlertErrorDetails(Model):
        error_code: str
        error_message: str
        occurrences: int

        def __init__(self, **kwargs) -> None: ...


    class azure.mgmt.edgegateway.models.AlertPaged(Paged):
        property raw: ClientRawResponse    # Read-only

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...


    class azure.mgmt.edgegateway.models.AlertSeverity(str, Enum):
        critical = "Critical"
        informational = "Informational"
        warning = "Warning"


    class azure.mgmt.edgegateway.models.AsymmetricEncryptedSecret(Model):

        def __init__(
                self, 
                *, 
                encryption_algorithm, 
                encryption_cert_thumbprint: str = ..., 
                value: str, 
                **kwargs
            ) -> None: ...


    class azure.mgmt.edgegateway.models.Authentication(Model):

        def __init__(
                self, 
                *, 
                symmetric_key = ..., 
                **kwargs
            ) -> None: ...


    class azure.mgmt.edgegateway.models.AuthenticationType(str, Enum):
        azure_active_directory = "AzureActiveDirectory"
        invalid = "Invalid"


    class azure.mgmt.edgegateway.models.AzureContainerDataFormat(str, Enum):
        azure_file = "AzureFile"
        block_blob = "BlockBlob"
        page_blob = "PageBlob"


    class azure.mgmt.edgegateway.models.AzureContainerInfo(Model):

        def __init__(
                self, 
                *, 
                container_name: str, 
                data_format, 
                storage_account_credential_id: str, 
                **kwargs
            ) -> None: ...


    class azure.mgmt.edgegateway.models.BandwidthSchedule(ARMBaseModel):
        id: str
        name: str
        type: str

        def __init__(
                self, 
                *, 
                days, 
                rate_in_mbps: int, 
                start: str, 
                stop: str, 
                **kwargs
            ) -> None: ...


    class azure.mgmt.edgegateway.models.BandwidthSchedulePaged(Paged):
        property raw: ClientRawResponse    # Read-only

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...


    class azure.mgmt.edgegateway.models.ClientAccessRight(Model):

        def __init__(
                self, 
                *, 
                access_permission, 
                client: str, 
                **kwargs
            ) -> None: ...


    class azure.mgmt.edgegateway.models.ClientPermissionType(str, Enum):
        no_access = "NoAccess"
        read_only = "ReadOnly"
        read_write = "ReadWrite"


    class azure.mgmt.edgegateway.models.ContactDetails(Model):

        def __init__(
                self, 
                *, 
                company_name: str, 
                contact_person: str, 
                email_list, 
                phone: str, 
                **kwargs
            ) -> None: ...


    class azure.mgmt.edgegateway.models.DataBoxEdgeDevice(ARMBaseModel):
        configured_role_types: Union[list[str, RoleTypes]]
        culture: str
        device_hcs_version: str
        device_local_capacity: long
        device_model: str
        device_software_version: str
        device_type: Union[str, DeviceType]
        id: str
        name: str
        serial_number: str
        time_zone: str
        type: str

        def __init__(
                self, 
                *, 
                data_box_edge_device_status = ..., 
                description: str = ..., 
                etag: str = ..., 
                friendly_name: str = ..., 
                location: str, 
                model_description: str = ..., 
                sku = ..., 
                tags = ..., 
                **kwargs
            ) -> None: ...


    class azure.mgmt.edgegateway.models.DataBoxEdgeDeviceExtendedInfo(ARMBaseModel):
        id: str
        name: str
        resource_key: str
        type: str

        def __init__(
                self, 
                *, 
                encryption_key: str = ..., 
                encryption_key_thumbprint: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.mgmt.edgegateway.models.DataBoxEdgeDevicePaged(Paged):
        property raw: ClientRawResponse    # Read-only

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...


    class azure.mgmt.edgegateway.models.DataBoxEdgeDevicePatch(Model):

        def __init__(
                self, 
                *, 
                tags = ..., 
                **kwargs
            ) -> None: ...


    class azure.mgmt.edgegateway.models.DataBoxEdgeDeviceStatus(str, Enum):
        disconnected = "Disconnected"
        needs_attention = "NeedsAttention"
        offline = "Offline"
        online = "Online"
        partially_disconnected = "PartiallyDisconnected"
        ready_to_setup = "ReadyToSetup"


    class azure.mgmt.edgegateway.models.DataPolicy(str, Enum):
        cloud = "Cloud"
        local = "Local"


    class azure.mgmt.edgegateway.models.DayOfWeek(str, Enum):
        friday = "Friday"
        monday = "Monday"
        saturday = "Saturday"
        sunday = "Sunday"
        thursday = "Thursday"
        tuesday = "Tuesday"
        wednesday = "Wednesday"


    class azure.mgmt.edgegateway.models.DeviceType(str, Enum):
        data_box_edge_device = "DataBoxEdgeDevice"


    class azure.mgmt.edgegateway.models.DownloadPhase(str, Enum):
        downloading = "Downloading"
        initializing = "Initializing"
        unknown = "Unknown"
        verifying = "Verifying"


    class azure.mgmt.edgegateway.models.EncryptionAlgorithm(str, Enum):
        aes256 = "AES256"
        none = "None"
        rsaes_pkcs1_v_1_5 = "RSAES_PKCS1_v_1_5"


    class azure.mgmt.edgegateway.models.FileEventTrigger(Trigger):
        id: str
        name: str
        type: str

        def __init__(
                self, 
                *, 
                custom_context_tag: str = ..., 
                sink_info, 
                source_info, 
                **kwargs
            ) -> None: ...


    class azure.mgmt.edgegateway.models.FileSourceInfo(Model):

        def __init__(
                self, 
                *, 
                share_id: str, 
                **kwargs
            ) -> None: ...


    class azure.mgmt.edgegateway.models.InstallRebootBehavior(str, Enum):
        never_reboots = "NeverReboots"
        request_reboot = "RequestReboot"
        requires_reboot = "RequiresReboot"


    class azure.mgmt.edgegateway.models.IoTDeviceInfo(Model):

        def __init__(
                self, 
                *, 
                authentication = ..., 
                device_id: str, 
                io_thost_hub: str, 
                **kwargs
            ) -> None: ...


    class azure.mgmt.edgegateway.models.IoTRole(Role):
        id: str
        name: str
        type: str

        def __init__(
                self, 
                *, 
                host_platform, 
                io_tdevice_details, 
                io_tedge_device_details, 
                role_status, 
                share_mappings = ..., 
                **kwargs
            ) -> None: ...


    class azure.mgmt.edgegateway.models.Ipv4Config(Model):
        gateway: str
        ip_address: str
        subnet: str

        def __init__(self, **kwargs) -> None: ...


    class azure.mgmt.edgegateway.models.Ipv6Config(Model):
        gateway: str
        ip_address: str
        prefix_length: int

        def __init__(self, **kwargs) -> None: ...


    class azure.mgmt.edgegateway.models.Job(Model):
        current_stage: Union[str, UpdateOperationStage]
        download_progress: UpdateDownloadProgress
        end_time: datetime
        error: JobErrorDetails
        error_manifest_file: str
        id: str
        install_progress: UpdateInstallProgress
        job_type: Union[str, JobType]
        name: str
        percent_complete: int
        share_id: str
        start_time: datetime
        status: Union[str, JobStatus]
        total_refresh_errors: int
        type: str

        def __init__(
                self, 
                *, 
                folder: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.mgmt.edgegateway.models.JobErrorDetails(Model):
        code: str
        error_details: list[JobErrorItem]
        message: str

        def __init__(self, **kwargs) -> None: ...


    class azure.mgmt.edgegateway.models.JobErrorItem(Model):
        code: str
        message: str
        recommendations: list[str]

        def __init__(self, **kwargs) -> None: ...


    class azure.mgmt.edgegateway.models.JobStatus(str, Enum):
        canceled = "Canceled"
        failed = "Failed"
        invalid = "Invalid"
        paused = "Paused"
        running = "Running"
        scheduled = "Scheduled"
        succeeded = "Succeeded"


    class azure.mgmt.edgegateway.models.JobType(str, Enum):
        download_updates = "DownloadUpdates"
        install_updates = "InstallUpdates"
        invalid = "Invalid"
        refresh_share = "RefreshShare"
        scan_for_updates = "ScanForUpdates"


    class azure.mgmt.edgegateway.models.MetricAggregationType(str, Enum):
        average = "Average"
        count = "Count"
        maximum = "Maximum"
        minimum = "Minimum"
        none = "None"
        not_specified = "NotSpecified"
        total = "Total"


    class azure.mgmt.edgegateway.models.MetricCategory(str, Enum):
        capacity = "Capacity"
        transaction = "Transaction"


    class azure.mgmt.edgegateway.models.MetricDimensionV1(Model):

        def __init__(
                self, 
                *, 
                display_name: str = ..., 
                name: str = ..., 
                to_be_exported_for_shoebox: bool = ..., 
                **kwargs
            ) -> None: ...


    class azure.mgmt.edgegateway.models.MetricSpecificationV1(Model):

        def __init__(
                self, 
                *, 
                aggregation_type = ..., 
                category = ..., 
                dimensions = ..., 
                display_description: str = ..., 
                display_name: str = ..., 
                fill_gap_with_zero: bool = ..., 
                name: str = ..., 
                resource_id_dimension_name_override: str = ..., 
                supported_aggregation_types = ..., 
                supported_time_grain_types = ..., 
                unit = ..., 
                **kwargs
            ) -> None: ...


    class azure.mgmt.edgegateway.models.MetricUnit(str, Enum):
        bytes = "Bytes"
        bytes_per_second = "BytesPerSecond"
        count = "Count"
        count_per_second = "CountPerSecond"
        milliseconds = "Milliseconds"
        not_specified = "NotSpecified"
        percent = "Percent"
        seconds = "Seconds"


    class azure.mgmt.edgegateway.models.MonitoringStatus(str, Enum):
        disabled = "Disabled"
        enabled = "Enabled"


    class azure.mgmt.edgegateway.models.MountPointMap(Model):
        mount_point: str
        role_id: str
        role_type: Union[str, RoleTypes]

        def __init__(
                self, 
                *, 
                share_id: str, 
                **kwargs
            ) -> None: ...


    class azure.mgmt.edgegateway.models.NetworkAdapter(Model):
        adapter_id: str
        adapter_position: NetworkAdapterPosition
        dns_servers: list[str]
        index: int
        ipv4_configuration: Ipv4Config
        ipv6_configuration: Ipv6Config
        ipv6_link_local_address: str
        label: str
        link_speed: long
        mac_address: str
        network_adapter_name: str
        node_id: str
        status: Union[str, NetworkAdapterStatus]

        def __init__(
                self, 
                *, 
                dhcp_status = ..., 
                rdma_status = ..., 
                **kwargs
            ) -> None: ...


    class azure.mgmt.edgegateway.models.NetworkAdapterDHCPStatus(str, Enum):
        disabled = "Disabled"
        enabled = "Enabled"


    class azure.mgmt.edgegateway.models.NetworkAdapterPosition(Model):
        network_group: Union[str, NetworkGroup]
        port: int

        def __init__(self, **kwargs) -> None: ...


    class azure.mgmt.edgegateway.models.NetworkAdapterRDMAStatus(str, Enum):
        capable = "Capable"
        incapable = "Incapable"


    class azure.mgmt.edgegateway.models.NetworkAdapterStatus(str, Enum):
        active = "Active"
        inactive = "Inactive"


    class azure.mgmt.edgegateway.models.NetworkGroup(str, Enum):
        non_rdma = "NonRDMA"
        none = "None"
        rdma = "RDMA"


    class azure.mgmt.edgegateway.models.NetworkSettings(ARMBaseModel):
        id: str
        name: str
        network_adapters: list[NetworkAdapter]
        type: str

        def __init__(self, **kwargs) -> None: ...


    class azure.mgmt.edgegateway.models.Operation(Model):

        def __init__(
                self, 
                *, 
                display = ..., 
                name: str = ..., 
                origin: str = ..., 
                service_specification = ..., 
                **kwargs
            ) -> None: ...


    class azure.mgmt.edgegateway.models.OperationDisplay(Model):

        def __init__(
                self, 
                *, 
                description: str = ..., 
                operation: str = ..., 
                provider: str = ..., 
                resource: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.mgmt.edgegateway.models.OperationPaged(Paged):
        property raw: ClientRawResponse    # Read-only

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...


    class azure.mgmt.edgegateway.models.Order(ARMBaseModel):
        delivery_tracking_info: list[TrackingInfo]
        id: str
        name: str
        order_history: list[OrderStatus]
        return_tracking_info: list[TrackingInfo]
        serial_number: str
        type: str

        def __init__(
                self, 
                *, 
                contact_information, 
                current_status = ..., 
                shipping_address, 
                **kwargs
            ) -> None: ...


    class azure.mgmt.edgegateway.models.OrderPaged(Paged):
        property raw: ClientRawResponse    # Read-only

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...


    class azure.mgmt.edgegateway.models.OrderState(str, Enum):
        arriving = "Arriving"
        awaiting_fulfilment = "AwaitingFulfilment"
        awaiting_preparation = "AwaitingPreparation"
        awaiting_return_shipment = "AwaitingReturnShipment"
        awaiting_shipment = "AwaitingShipment"
        collected_at_microsoft = "CollectedAtMicrosoft"
        declined = "Declined"
        delivered = "Delivered"
        lost_device = "LostDevice"
        replacement_requested = "ReplacementRequested"
        return_initiated = "ReturnInitiated"
        shipped = "Shipped"
        shipped_back = "ShippedBack"
        untracked = "Untracked"


    class azure.mgmt.edgegateway.models.OrderStatus(Model):
        update_date_time: datetime

        def __init__(
                self, 
                *, 
                comments: str = ..., 
                status, 
                **kwargs
            ) -> None: ...


    class azure.mgmt.edgegateway.models.PeriodicTimerEventTrigger(Trigger):
        id: str
        name: str
        type: str

        def __init__(
                self, 
                *, 
                custom_context_tag: str = ..., 
                sink_info, 
                source_info, 
                **kwargs
            ) -> None: ...


    class azure.mgmt.edgegateway.models.PeriodicTimerSourceInfo(Model):

        def __init__(
                self, 
                *, 
                schedule: str, 
                start_time, 
                topic: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.mgmt.edgegateway.models.PlatformType(str, Enum):
        linux = "Linux"
        windows = "Windows"


    class azure.mgmt.edgegateway.models.RefreshDetails(Model):

        def __init__(
                self, 
                *, 
                error_manifest_file: str = ..., 
                in_progress_refresh_job_id: str = ..., 
                last_completed_refresh_job_time_in_utc = ..., 
                last_job: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.mgmt.edgegateway.models.Role(ARMBaseModel):
        id: str
        name: str
        type: str

        def __init__(self, **kwargs) -> None: ...


    class azure.mgmt.edgegateway.models.RolePaged(Paged):
        property raw: ClientRawResponse    # Read-only

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...


    class azure.mgmt.edgegateway.models.RoleSinkInfo(Model):

        def __init__(
                self, 
                *, 
                role_id: str, 
                **kwargs
            ) -> None: ...


    class azure.mgmt.edgegateway.models.RoleStatus(str, Enum):
        disabled = "Disabled"
        enabled = "Enabled"


    class azure.mgmt.edgegateway.models.RoleTypes(str, Enum):
        asa = "ASA"
        cognitive = "Cognitive"
        functions = "Functions"
        iot = "IOT"


    class azure.mgmt.edgegateway.models.SSLStatus(str, Enum):
        disabled = "Disabled"
        enabled = "Enabled"


    class azure.mgmt.edgegateway.models.SecuritySettings(ARMBaseModel):
        id: str
        name: str
        type: str

        def __init__(
                self, 
                *, 
                device_admin_password, 
                **kwargs
            ) -> None: ...


    class azure.mgmt.edgegateway.models.ServiceSpecification(Model):

        def __init__(
                self, 
                *, 
                metric_specifications = ..., 
                **kwargs
            ) -> None: ...


    class azure.mgmt.edgegateway.models.Share(ARMBaseModel):
        id: str
        name: str
        share_mappings: list[MountPointMap]
        type: str

        def __init__(
                self, 
                *, 
                access_protocol, 
                azure_container_info = ..., 
                client_access_rights = ..., 
                data_policy = ..., 
                description: str = ..., 
                monitoring_status, 
                refresh_details = ..., 
                share_status, 
                user_access_rights = ..., 
                **kwargs
            ) -> None: ...


    class azure.mgmt.edgegateway.models.ShareAccessProtocol(str, Enum):
        nfs = "NFS"
        smb = "SMB"


    class azure.mgmt.edgegateway.models.ShareAccessRight(Model):

        def __init__(
                self, 
                *, 
                access_type, 
                share_id: str, 
                **kwargs
            ) -> None: ...


    class azure.mgmt.edgegateway.models.ShareAccessType(str, Enum):
        change = "Change"
        custom = "Custom"
        read = "Read"


    class azure.mgmt.edgegateway.models.SharePaged(Paged):
        property raw: ClientRawResponse    # Read-only

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...


    class azure.mgmt.edgegateway.models.ShareStatus(str, Enum):
        offline = "Offline"
        online = "Online"


    class azure.mgmt.edgegateway.models.Sku(Model):

        def __init__(
                self, 
                *, 
                name = ..., 
                tier = ..., 
                **kwargs
            ) -> None: ...


    class azure.mgmt.edgegateway.models.SkuName(str, Enum):
        edge = "Edge"
        gateway = "Gateway"


    class azure.mgmt.edgegateway.models.SkuTier(str, Enum):
        standard = "Standard"


    class azure.mgmt.edgegateway.models.StorageAccountCredential(ARMBaseModel):
        id: str
        name: str
        type: str

        def __init__(
                self, 
                *, 
                account_key = ..., 
                account_type, 
                alias: str, 
                blob_domain_name: str = ..., 
                connection_string: str = ..., 
                ssl_status, 
                user_name: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.mgmt.edgegateway.models.StorageAccountCredentialPaged(Paged):
        property raw: ClientRawResponse    # Read-only

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...


    class azure.mgmt.edgegateway.models.SymmetricKey(Model):

        def __init__(
                self, 
                *, 
                connection_string = ..., 
                **kwargs
            ) -> None: ...


    class azure.mgmt.edgegateway.models.TimeGrain(str, Enum):
        pt12_h = "PT12H"
        pt15_m = "PT15M"
        pt1_d = "PT1D"
        pt1_h = "PT1H"
        pt1_m = "PT1M"
        pt30_m = "PT30M"
        pt5_m = "PT5M"
        pt6_h = "PT6H"


    class azure.mgmt.edgegateway.models.TrackingInfo(Model):

        def __init__(
                self, 
                *, 
                carrier_name: str = ..., 
                serial_number: str = ..., 
                tracking_id: str = ..., 
                tracking_url: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.mgmt.edgegateway.models.Trigger(ARMBaseModel):
        id: str
        name: str
        type: str

        def __init__(self, **kwargs) -> None: ...


    class azure.mgmt.edgegateway.models.TriggerPaged(Paged):
        property raw: ClientRawResponse    # Read-only

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...


    class azure.mgmt.edgegateway.models.UpdateDownloadProgress(Model):
        download_phase: Union[str, DownloadPhase]
        number_of_updates_downloaded: int
        number_of_updates_to_download: int
        percent_complete: int
        total_bytes_downloaded: float
        total_bytes_to_download: float

        def __init__(self, **kwargs) -> None: ...


    class azure.mgmt.edgegateway.models.UpdateInstallProgress(Model):
        number_of_updates_installed: int
        number_of_updates_to_install: int
        percent_complete: int

        def __init__(self, **kwargs) -> None: ...


    class azure.mgmt.edgegateway.models.UpdateOperation(str, Enum):
        download = "Download"
        install = "Install"
        none = "None"
        scan = "Scan"


    class azure.mgmt.edgegateway.models.UpdateOperationStage(str, Enum):
        download_complete = "DownloadComplete"
        download_failed = "DownloadFailed"
        download_started = "DownloadStarted"
        failure = "Failure"
        initial = "Initial"
        install_complete = "InstallComplete"
        install_failed = "InstallFailed"
        install_started = "InstallStarted"
        reboot_initiated = "RebootInitiated"
        rescan_complete = "RescanComplete"
        rescan_failed = "RescanFailed"
        rescan_started = "RescanStarted"
        scan_complete = "ScanComplete"
        scan_failed = "ScanFailed"
        scan_started = "ScanStarted"
        success = "Success"
        unknown = "Unknown"


    class azure.mgmt.edgegateway.models.UpdateSummary(ARMBaseModel):
        id: str
        in_progress_download_job_id: str
        in_progress_download_job_started_date_time: datetime
        in_progress_install_job_id: str
        in_progress_install_job_started_date_time: datetime
        last_completed_download_job_date_time: datetime
        last_completed_install_job_date_time: datetime
        name: str
        ongoing_update_operation: Union[str, UpdateOperation]
        reboot_behavior: Union[str, InstallRebootBehavior]
        total_number_of_updates_available: int
        total_number_of_updates_pending_download: int
        total_number_of_updates_pending_install: int
        total_update_size_in_bytes: float
        type: str
        update_titles: list[str]

        def __init__(
                self, 
                *, 
                device_last_scanned_date_time = ..., 
                device_version_number: str = ..., 
                friendly_device_version_name: str = ..., 
                last_completed_scan_job_date_time = ..., 
                **kwargs
            ) -> None: ...


    class azure.mgmt.edgegateway.models.UploadCertificateRequest(Model):

        def __init__(
                self, 
                *, 
                authentication_type = ..., 
                certificate: str, 
                **kwargs
            ) -> None: ...


    class azure.mgmt.edgegateway.models.UploadCertificateResponse(Model):

        def __init__(
                self, 
                *, 
                aad_authority: str, 
                aad_tenant_id: str, 
                auth_type = ..., 
                azure_management_endpoint_audience: str, 
                resource_id: str, 
                service_principal_client_id: str, 
                service_principal_object_id: str, 
                **kwargs
            ) -> None: ...


    class azure.mgmt.edgegateway.models.User(ARMBaseModel):
        id: str
        name: str
        type: str

        def __init__(
                self, 
                *, 
                encrypted_password = ..., 
                share_access_rights = ..., 
                **kwargs
            ) -> None: ...


    class azure.mgmt.edgegateway.models.UserAccessRight(Model):

        def __init__(
                self, 
                *, 
                access_type, 
                user_id: str, 
                **kwargs
            ) -> None: ...


    class azure.mgmt.edgegateway.models.UserPaged(Paged):
        property raw: ClientRawResponse    # Read-only

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...


namespace azure.mgmt.edgegateway.models.address

    class azure.mgmt.edgegateway.models.address.Address(Model):

        def __init__(self, **kwargs): ...


namespace azure.mgmt.edgegateway.models.address_py3

    class azure.mgmt.edgegateway.models.address_py3.Address(Model):

        def __init__(
                self, 
                *, 
                address_line1: str, 
                address_line2: str = ..., 
                address_line3: str = ..., 
                city: str, 
                country: str, 
                postal_code: str, 
                state: str, 
                **kwargs
            ) -> None: ...


namespace azure.mgmt.edgegateway.models.alert

    class azure.mgmt.edgegateway.models.alert.ARMBaseModel(Model):
        id: str
        name: str
        type: str

        def __init__(self, **kwargs): ...


    class azure.mgmt.edgegateway.models.alert.Alert(ARMBaseModel):
        alert_type: str
        appeared_at_date_time: datetime
        detailed_information: dict[str, str]
        error_details: AlertErrorDetails
        id: str
        name: str
        recommendation: str
        severity: Union[str, AlertSeverity]
        title: str
        type: str

        def __init__(self, **kwargs): ...


namespace azure.mgmt.edgegateway.models.alert_error_details

    class azure.mgmt.edgegateway.models.alert_error_details.AlertErrorDetails(Model):
        error_code: str
        error_message: str
        occurrences: int

        def __init__(self, **kwargs): ...


namespace azure.mgmt.edgegateway.models.alert_error_details_py3

    class azure.mgmt.edgegateway.models.alert_error_details_py3.AlertErrorDetails(Model):
        error_code: str
        error_message: str
        occurrences: int

        def __init__(self, **kwargs) -> None: ...


namespace azure.mgmt.edgegateway.models.alert_paged

    class azure.mgmt.edgegateway.models.alert_paged.AlertPaged(Paged):
        property raw: ClientRawResponse    # Read-only

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...


namespace azure.mgmt.edgegateway.models.alert_py3

    class azure.mgmt.edgegateway.models.alert_py3.ARMBaseModel(Model):
        id: str
        name: str
        type: str

        def __init__(self, **kwargs) -> None: ...


    class azure.mgmt.edgegateway.models.alert_py3.Alert(ARMBaseModel):
        alert_type: str
        appeared_at_date_time: datetime
        detailed_information: dict[str, str]
        error_details: AlertErrorDetails
        id: str
        name: str
        recommendation: str
        severity: Union[str, AlertSeverity]
        title: str
        type: str

        def __init__(self, **kwargs) -> None: ...


namespace azure.mgmt.edgegateway.models.arm_base_model

    class azure.mgmt.edgegateway.models.arm_base_model.ARMBaseModel(Model):
        id: str
        name: str
        type: str

        def __init__(self, **kwargs): ...


namespace azure.mgmt.edgegateway.models.arm_base_model_py3

    class azure.mgmt.edgegateway.models.arm_base_model_py3.ARMBaseModel(Model):
        id: str
        name: str
        type: str

        def __init__(self, **kwargs) -> None: ...


namespace azure.mgmt.edgegateway.models.asymmetric_encrypted_secret

    class azure.mgmt.edgegateway.models.asymmetric_encrypted_secret.AsymmetricEncryptedSecret(Model):

        def __init__(self, **kwargs): ...


namespace azure.mgmt.edgegateway.models.asymmetric_encrypted_secret_py3

    class azure.mgmt.edgegateway.models.asymmetric_encrypted_secret_py3.AsymmetricEncryptedSecret(Model):

        def __init__(
                self, 
                *, 
                encryption_algorithm, 
                encryption_cert_thumbprint: str = ..., 
                value: str, 
                **kwargs
            ) -> None: ...


namespace azure.mgmt.edgegateway.models.authentication

    class azure.mgmt.edgegateway.models.authentication.Authentication(Model):

        def __init__(self, **kwargs): ...


namespace azure.mgmt.edgegateway.models.authentication_py3

    class azure.mgmt.edgegateway.models.authentication_py3.Authentication(Model):

        def __init__(
                self, 
                *, 
                symmetric_key = ..., 
                **kwargs
            ) -> None: ...


namespace azure.mgmt.edgegateway.models.azure_container_info

    class azure.mgmt.edgegateway.models.azure_container_info.AzureContainerInfo(Model):

        def __init__(self, **kwargs): ...


namespace azure.mgmt.edgegateway.models.azure_container_info_py3

    class azure.mgmt.edgegateway.models.azure_container_info_py3.AzureContainerInfo(Model):

        def __init__(
                self, 
                *, 
                container_name: str, 
                data_format, 
                storage_account_credential_id: str, 
                **kwargs
            ) -> None: ...


namespace azure.mgmt.edgegateway.models.bandwidth_schedule

    class azure.mgmt.edgegateway.models.bandwidth_schedule.ARMBaseModel(Model):
        id: str
        name: str
        type: str

        def __init__(self, **kwargs): ...


    class azure.mgmt.edgegateway.models.bandwidth_schedule.BandwidthSchedule(ARMBaseModel):
        id: str
        name: str
        type: str

        def __init__(self, **kwargs): ...


namespace azure.mgmt.edgegateway.models.bandwidth_schedule_paged

    class azure.mgmt.edgegateway.models.bandwidth_schedule_paged.BandwidthSchedulePaged(Paged):
        property raw: ClientRawResponse    # Read-only

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...


namespace azure.mgmt.edgegateway.models.bandwidth_schedule_py3

    class azure.mgmt.edgegateway.models.bandwidth_schedule_py3.ARMBaseModel(Model):
        id: str
        name: str
        type: str

        def __init__(self, **kwargs) -> None: ...


    class azure.mgmt.edgegateway.models.bandwidth_schedule_py3.BandwidthSchedule(ARMBaseModel):
        id: str
        name: str
        type: str

        def __init__(
                self, 
                *, 
                days, 
                rate_in_mbps: int, 
                start: str, 
                stop: str, 
                **kwargs
            ) -> None: ...


namespace azure.mgmt.edgegateway.models.client_access_right

    class azure.mgmt.edgegateway.models.client_access_right.ClientAccessRight(Model):

        def __init__(self, **kwargs): ...


namespace azure.mgmt.edgegateway.models.client_access_right_py3

    class azure.mgmt.edgegateway.models.client_access_right_py3.ClientAccessRight(Model):

        def __init__(
                self, 
                *, 
                access_permission, 
                client: str, 
                **kwargs
            ) -> None: ...


namespace azure.mgmt.edgegateway.models.contact_details

    class azure.mgmt.edgegateway.models.contact_details.ContactDetails(Model):

        def __init__(self, **kwargs): ...


namespace azure.mgmt.edgegateway.models.contact_details_py3

    class azure.mgmt.edgegateway.models.contact_details_py3.ContactDetails(Model):

        def __init__(
                self, 
                *, 
                company_name: str, 
                contact_person: str, 
                email_list, 
                phone: str, 
                **kwargs
            ) -> None: ...


namespace azure.mgmt.edgegateway.models.data_box_edge_device

    class azure.mgmt.edgegateway.models.data_box_edge_device.ARMBaseModel(Model):
        id: str
        name: str
        type: str

        def __init__(self, **kwargs): ...


    class azure.mgmt.edgegateway.models.data_box_edge_device.DataBoxEdgeDevice(ARMBaseModel):
        configured_role_types: Union[list[str, RoleTypes]]
        culture: str
        device_hcs_version: str
        device_local_capacity: long
        device_model: str
        device_software_version: str
        device_type: Union[str, DeviceType]
        id: str
        name: str
        serial_number: str
        time_zone: str
        type: str

        def __init__(self, **kwargs): ...


namespace azure.mgmt.edgegateway.models.data_box_edge_device_extended_info

    class azure.mgmt.edgegateway.models.data_box_edge_device_extended_info.ARMBaseModel(Model):
        id: str
        name: str
        type: str

        def __init__(self, **kwargs): ...


    class azure.mgmt.edgegateway.models.data_box_edge_device_extended_info.DataBoxEdgeDeviceExtendedInfo(ARMBaseModel):
        id: str
        name: str
        resource_key: str
        type: str

        def __init__(self, **kwargs): ...


namespace azure.mgmt.edgegateway.models.data_box_edge_device_extended_info_py3

    class azure.mgmt.edgegateway.models.data_box_edge_device_extended_info_py3.ARMBaseModel(Model):
        id: str
        name: str
        type: str

        def __init__(self, **kwargs) -> None: ...


    class azure.mgmt.edgegateway.models.data_box_edge_device_extended_info_py3.DataBoxEdgeDeviceExtendedInfo(ARMBaseModel):
        id: str
        name: str
        resource_key: str
        type: str

        def __init__(
                self, 
                *, 
                encryption_key: str = ..., 
                encryption_key_thumbprint: str = ..., 
                **kwargs
            ) -> None: ...


namespace azure.mgmt.edgegateway.models.data_box_edge_device_paged

    class azure.mgmt.edgegateway.models.data_box_edge_device_paged.DataBoxEdgeDevicePaged(Paged):
        property raw: ClientRawResponse    # Read-only

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...


namespace azure.mgmt.edgegateway.models.data_box_edge_device_patch

    class azure.mgmt.edgegateway.models.data_box_edge_device_patch.DataBoxEdgeDevicePatch(Model):

        def __init__(self, **kwargs): ...


namespace azure.mgmt.edgegateway.models.data_box_edge_device_patch_py3

    class azure.mgmt.edgegateway.models.data_box_edge_device_patch_py3.DataBoxEdgeDevicePatch(Model):

        def __init__(
                self, 
                *, 
                tags = ..., 
                **kwargs
            ) -> None: ...


namespace azure.mgmt.edgegateway.models.data_box_edge_device_py3

    class azure.mgmt.edgegateway.models.data_box_edge_device_py3.ARMBaseModel(Model):
        id: str
        name: str
        type: str

        def __init__(self, **kwargs) -> None: ...


    class azure.mgmt.edgegateway.models.data_box_edge_device_py3.DataBoxEdgeDevice(ARMBaseModel):
        configured_role_types: Union[list[str, RoleTypes]]
        culture: str
        device_hcs_version: str
        device_local_capacity: long
        device_model: str
        device_software_version: str
        device_type: Union[str, DeviceType]
        id: str
        name: str
        serial_number: str
        time_zone: str
        type: str

        def __init__(
                self, 
                *, 
                data_box_edge_device_status = ..., 
                description: str = ..., 
                etag: str = ..., 
                friendly_name: str = ..., 
                location: str, 
                model_description: str = ..., 
                sku = ..., 
                tags = ..., 
                **kwargs
            ) -> None: ...


namespace azure.mgmt.edgegateway.models.data_box_edge_management_client_enums

    class azure.mgmt.edgegateway.models.data_box_edge_management_client_enums.AccountType(str, Enum):
        blob_storage = "BlobStorage"
        general_purpose_storage = "GeneralPurposeStorage"


    class azure.mgmt.edgegateway.models.data_box_edge_management_client_enums.AlertSeverity(str, Enum):
        critical = "Critical"
        informational = "Informational"
        warning = "Warning"


    class azure.mgmt.edgegateway.models.data_box_edge_management_client_enums.AuthenticationType(str, Enum):
        azure_active_directory = "AzureActiveDirectory"
        invalid = "Invalid"


    class azure.mgmt.edgegateway.models.data_box_edge_management_client_enums.AzureContainerDataFormat(str, Enum):
        azure_file = "AzureFile"
        block_blob = "BlockBlob"
        page_blob = "PageBlob"


    class azure.mgmt.edgegateway.models.data_box_edge_management_client_enums.ClientPermissionType(str, Enum):
        no_access = "NoAccess"
        read_only = "ReadOnly"
        read_write = "ReadWrite"


    class azure.mgmt.edgegateway.models.data_box_edge_management_client_enums.DataBoxEdgeDeviceStatus(str, Enum):
        disconnected = "Disconnected"
        needs_attention = "NeedsAttention"
        offline = "Offline"
        online = "Online"
        partially_disconnected = "PartiallyDisconnected"
        ready_to_setup = "ReadyToSetup"


    class azure.mgmt.edgegateway.models.data_box_edge_management_client_enums.DataPolicy(str, Enum):
        cloud = "Cloud"
        local = "Local"


    class azure.mgmt.edgegateway.models.data_box_edge_management_client_enums.DayOfWeek(str, Enum):
        friday = "Friday"
        monday = "Monday"
        saturday = "Saturday"
        sunday = "Sunday"
        thursday = "Thursday"
        tuesday = "Tuesday"
        wednesday = "Wednesday"


    class azure.mgmt.edgegateway.models.data_box_edge_management_client_enums.DeviceType(str, Enum):
        data_box_edge_device = "DataBoxEdgeDevice"


    class azure.mgmt.edgegateway.models.data_box_edge_management_client_enums.DownloadPhase(str, Enum):
        downloading = "Downloading"
        initializing = "Initializing"
        unknown = "Unknown"
        verifying = "Verifying"


    class azure.mgmt.edgegateway.models.data_box_edge_management_client_enums.EncryptionAlgorithm(str, Enum):
        aes256 = "AES256"
        none = "None"
        rsaes_pkcs1_v_1_5 = "RSAES_PKCS1_v_1_5"


    class azure.mgmt.edgegateway.models.data_box_edge_management_client_enums.InstallRebootBehavior(str, Enum):
        never_reboots = "NeverReboots"
        request_reboot = "RequestReboot"
        requires_reboot = "RequiresReboot"


    class azure.mgmt.edgegateway.models.data_box_edge_management_client_enums.JobStatus(str, Enum):
        canceled = "Canceled"
        failed = "Failed"
        invalid = "Invalid"
        paused = "Paused"
        running = "Running"
        scheduled = "Scheduled"
        succeeded = "Succeeded"


    class azure.mgmt.edgegateway.models.data_box_edge_management_client_enums.JobType(str, Enum):
        download_updates = "DownloadUpdates"
        install_updates = "InstallUpdates"
        invalid = "Invalid"
        refresh_share = "RefreshShare"
        scan_for_updates = "ScanForUpdates"


    class azure.mgmt.edgegateway.models.data_box_edge_management_client_enums.MetricAggregationType(str, Enum):
        average = "Average"
        count = "Count"
        maximum = "Maximum"
        minimum = "Minimum"
        none = "None"
        not_specified = "NotSpecified"
        total = "Total"


    class azure.mgmt.edgegateway.models.data_box_edge_management_client_enums.MetricCategory(str, Enum):
        capacity = "Capacity"
        transaction = "Transaction"


    class azure.mgmt.edgegateway.models.data_box_edge_management_client_enums.MetricUnit(str, Enum):
        bytes = "Bytes"
        bytes_per_second = "BytesPerSecond"
        count = "Count"
        count_per_second = "CountPerSecond"
        milliseconds = "Milliseconds"
        not_specified = "NotSpecified"
        percent = "Percent"
        seconds = "Seconds"


    class azure.mgmt.edgegateway.models.data_box_edge_management_client_enums.MonitoringStatus(str, Enum):
        disabled = "Disabled"
        enabled = "Enabled"


    class azure.mgmt.edgegateway.models.data_box_edge_management_client_enums.NetworkAdapterDHCPStatus(str, Enum):
        disabled = "Disabled"
        enabled = "Enabled"


    class azure.mgmt.edgegateway.models.data_box_edge_management_client_enums.NetworkAdapterRDMAStatus(str, Enum):
        capable = "Capable"
        incapable = "Incapable"


    class azure.mgmt.edgegateway.models.data_box_edge_management_client_enums.NetworkAdapterStatus(str, Enum):
        active = "Active"
        inactive = "Inactive"


    class azure.mgmt.edgegateway.models.data_box_edge_management_client_enums.NetworkGroup(str, Enum):
        non_rdma = "NonRDMA"
        none = "None"
        rdma = "RDMA"


    class azure.mgmt.edgegateway.models.data_box_edge_management_client_enums.OrderState(str, Enum):
        arriving = "Arriving"
        awaiting_fulfilment = "AwaitingFulfilment"
        awaiting_preparation = "AwaitingPreparation"
        awaiting_return_shipment = "AwaitingReturnShipment"
        awaiting_shipment = "AwaitingShipment"
        collected_at_microsoft = "CollectedAtMicrosoft"
        declined = "Declined"
        delivered = "Delivered"
        lost_device = "LostDevice"
        replacement_requested = "ReplacementRequested"
        return_initiated = "ReturnInitiated"
        shipped = "Shipped"
        shipped_back = "ShippedBack"
        untracked = "Untracked"


    class azure.mgmt.edgegateway.models.data_box_edge_management_client_enums.PlatformType(str, Enum):
        linux = "Linux"
        windows = "Windows"


    class azure.mgmt.edgegateway.models.data_box_edge_management_client_enums.RoleStatus(str, Enum):
        disabled = "Disabled"
        enabled = "Enabled"


    class azure.mgmt.edgegateway.models.data_box_edge_management_client_enums.RoleTypes(str, Enum):
        asa = "ASA"
        cognitive = "Cognitive"
        functions = "Functions"
        iot = "IOT"


    class azure.mgmt.edgegateway.models.data_box_edge_management_client_enums.SSLStatus(str, Enum):
        disabled = "Disabled"
        enabled = "Enabled"


    class azure.mgmt.edgegateway.models.data_box_edge_management_client_enums.ShareAccessProtocol(str, Enum):
        nfs = "NFS"
        smb = "SMB"


    class azure.mgmt.edgegateway.models.data_box_edge_management_client_enums.ShareAccessType(str, Enum):
        change = "Change"
        custom = "Custom"
        read = "Read"


    class azure.mgmt.edgegateway.models.data_box_edge_management_client_enums.ShareStatus(str, Enum):
        offline = "Offline"
        online = "Online"


    class azure.mgmt.edgegateway.models.data_box_edge_management_client_enums.SkuName(str, Enum):
        edge = "Edge"
        gateway = "Gateway"


    class azure.mgmt.edgegateway.models.data_box_edge_management_client_enums.SkuTier(str, Enum):
        standard = "Standard"


    class azure.mgmt.edgegateway.models.data_box_edge_management_client_enums.TimeGrain(str, Enum):
        pt12_h = "PT12H"
        pt15_m = "PT15M"
        pt1_d = "PT1D"
        pt1_h = "PT1H"
        pt1_m = "PT1M"
        pt30_m = "PT30M"
        pt5_m = "PT5M"
        pt6_h = "PT6H"


    class azure.mgmt.edgegateway.models.data_box_edge_management_client_enums.UpdateOperation(str, Enum):
        download = "Download"
        install = "Install"
        none = "None"
        scan = "Scan"


    class azure.mgmt.edgegateway.models.data_box_edge_management_client_enums.UpdateOperationStage(str, Enum):
        download_complete = "DownloadComplete"
        download_failed = "DownloadFailed"
        download_started = "DownloadStarted"
        failure = "Failure"
        initial = "Initial"
        install_complete = "InstallComplete"
        install_failed = "InstallFailed"
        install_started = "InstallStarted"
        reboot_initiated = "RebootInitiated"
        rescan_complete = "RescanComplete"
        rescan_failed = "RescanFailed"
        rescan_started = "RescanStarted"
        scan_complete = "ScanComplete"
        scan_failed = "ScanFailed"
        scan_started = "ScanStarted"
        success = "Success"
        unknown = "Unknown"


namespace azure.mgmt.edgegateway.models.file_event_trigger

    class azure.mgmt.edgegateway.models.file_event_trigger.FileEventTrigger(Trigger):
        id: str
        name: str
        type: str

        def __init__(self, **kwargs): ...


    class azure.mgmt.edgegateway.models.file_event_trigger.Trigger(ARMBaseModel):
        id: str
        name: str
        type: str

        def __init__(self, **kwargs): ...


namespace azure.mgmt.edgegateway.models.file_event_trigger_py3

    class azure.mgmt.edgegateway.models.file_event_trigger_py3.FileEventTrigger(Trigger):
        id: str
        name: str
        type: str

        def __init__(
                self, 
                *, 
                custom_context_tag: str = ..., 
                sink_info, 
                source_info, 
                **kwargs
            ) -> None: ...


    class azure.mgmt.edgegateway.models.file_event_trigger_py3.Trigger(ARMBaseModel):
        id: str
        name: str
        type: str

        def __init__(self, **kwargs) -> None: ...


namespace azure.mgmt.edgegateway.models.file_source_info

    class azure.mgmt.edgegateway.models.file_source_info.FileSourceInfo(Model):

        def __init__(self, **kwargs): ...


namespace azure.mgmt.edgegateway.models.file_source_info_py3

    class azure.mgmt.edgegateway.models.file_source_info_py3.FileSourceInfo(Model):

        def __init__(
                self, 
                *, 
                share_id: str, 
                **kwargs
            ) -> None: ...


namespace azure.mgmt.edgegateway.models.io_tdevice_info

    class azure.mgmt.edgegateway.models.io_tdevice_info.IoTDeviceInfo(Model):

        def __init__(self, **kwargs): ...


namespace azure.mgmt.edgegateway.models.io_tdevice_info_py3

    class azure.mgmt.edgegateway.models.io_tdevice_info_py3.IoTDeviceInfo(Model):

        def __init__(
                self, 
                *, 
                authentication = ..., 
                device_id: str, 
                io_thost_hub: str, 
                **kwargs
            ) -> None: ...


namespace azure.mgmt.edgegateway.models.io_trole

    class azure.mgmt.edgegateway.models.io_trole.IoTRole(Role):
        id: str
        name: str
        type: str

        def __init__(self, **kwargs): ...


    class azure.mgmt.edgegateway.models.io_trole.Role(ARMBaseModel):
        id: str
        name: str
        type: str

        def __init__(self, **kwargs): ...


namespace azure.mgmt.edgegateway.models.io_trole_py3

    class azure.mgmt.edgegateway.models.io_trole_py3.IoTRole(Role):
        id: str
        name: str
        type: str

        def __init__(
                self, 
                *, 
                host_platform, 
                io_tdevice_details, 
                io_tedge_device_details, 
                role_status, 
                share_mappings = ..., 
                **kwargs
            ) -> None: ...


    class azure.mgmt.edgegateway.models.io_trole_py3.Role(ARMBaseModel):
        id: str
        name: str
        type: str

        def __init__(self, **kwargs) -> None: ...


namespace azure.mgmt.edgegateway.models.ipv4_config

    class azure.mgmt.edgegateway.models.ipv4_config.Ipv4Config(Model):
        gateway: str
        ip_address: str
        subnet: str

        def __init__(self, **kwargs): ...


namespace azure.mgmt.edgegateway.models.ipv4_config_py3

    class azure.mgmt.edgegateway.models.ipv4_config_py3.Ipv4Config(Model):
        gateway: str
        ip_address: str
        subnet: str

        def __init__(self, **kwargs) -> None: ...


namespace azure.mgmt.edgegateway.models.ipv6_config

    class azure.mgmt.edgegateway.models.ipv6_config.Ipv6Config(Model):
        gateway: str
        ip_address: str
        prefix_length: int

        def __init__(self, **kwargs): ...


namespace azure.mgmt.edgegateway.models.ipv6_config_py3

    class azure.mgmt.edgegateway.models.ipv6_config_py3.Ipv6Config(Model):
        gateway: str
        ip_address: str
        prefix_length: int

        def __init__(self, **kwargs) -> None: ...


namespace azure.mgmt.edgegateway.models.job

    class azure.mgmt.edgegateway.models.job.Job(Model):
        current_stage: Union[str, UpdateOperationStage]
        download_progress: UpdateDownloadProgress
        end_time: datetime
        error: JobErrorDetails
        error_manifest_file: str
        id: str
        install_progress: UpdateInstallProgress
        job_type: Union[str, JobType]
        name: str
        percent_complete: int
        share_id: str
        start_time: datetime
        status: Union[str, JobStatus]
        total_refresh_errors: int
        type: str

        def __init__(self, **kwargs): ...


namespace azure.mgmt.edgegateway.models.job_error_details

    class azure.mgmt.edgegateway.models.job_error_details.JobErrorDetails(Model):
        code: str
        error_details: list[JobErrorItem]
        message: str

        def __init__(self, **kwargs): ...


namespace azure.mgmt.edgegateway.models.job_error_details_py3

    class azure.mgmt.edgegateway.models.job_error_details_py3.JobErrorDetails(Model):
        code: str
        error_details: list[JobErrorItem]
        message: str

        def __init__(self, **kwargs) -> None: ...


namespace azure.mgmt.edgegateway.models.job_error_item

    class azure.mgmt.edgegateway.models.job_error_item.JobErrorItem(Model):
        code: str
        message: str
        recommendations: list[str]

        def __init__(self, **kwargs): ...


namespace azure.mgmt.edgegateway.models.job_error_item_py3

    class azure.mgmt.edgegateway.models.job_error_item_py3.JobErrorItem(Model):
        code: str
        message: str
        recommendations: list[str]

        def __init__(self, **kwargs) -> None: ...


namespace azure.mgmt.edgegateway.models.job_py3

    class azure.mgmt.edgegateway.models.job_py3.Job(Model):
        current_stage: Union[str, UpdateOperationStage]
        download_progress: UpdateDownloadProgress
        end_time: datetime
        error: JobErrorDetails
        error_manifest_file: str
        id: str
        install_progress: UpdateInstallProgress
        job_type: Union[str, JobType]
        name: str
        percent_complete: int
        share_id: str
        start_time: datetime
        status: Union[str, JobStatus]
        total_refresh_errors: int
        type: str

        def __init__(
                self, 
                *, 
                folder: str = ..., 
                **kwargs
            ) -> None: ...


namespace azure.mgmt.edgegateway.models.metric_dimension_v1

    class azure.mgmt.edgegateway.models.metric_dimension_v1.MetricDimensionV1(Model):

        def __init__(self, **kwargs): ...


namespace azure.mgmt.edgegateway.models.metric_dimension_v1_py3

    class azure.mgmt.edgegateway.models.metric_dimension_v1_py3.MetricDimensionV1(Model):

        def __init__(
                self, 
                *, 
                display_name: str = ..., 
                name: str = ..., 
                to_be_exported_for_shoebox: bool = ..., 
                **kwargs
            ) -> None: ...


namespace azure.mgmt.edgegateway.models.metric_specification_v1

    class azure.mgmt.edgegateway.models.metric_specification_v1.MetricSpecificationV1(Model):

        def __init__(self, **kwargs): ...


namespace azure.mgmt.edgegateway.models.metric_specification_v1_py3

    class azure.mgmt.edgegateway.models.metric_specification_v1_py3.MetricSpecificationV1(Model):

        def __init__(
                self, 
                *, 
                aggregation_type = ..., 
                category = ..., 
                dimensions = ..., 
                display_description: str = ..., 
                display_name: str = ..., 
                fill_gap_with_zero: bool = ..., 
                name: str = ..., 
                resource_id_dimension_name_override: str = ..., 
                supported_aggregation_types = ..., 
                supported_time_grain_types = ..., 
                unit = ..., 
                **kwargs
            ) -> None: ...


namespace azure.mgmt.edgegateway.models.mount_point_map

    class azure.mgmt.edgegateway.models.mount_point_map.MountPointMap(Model):
        mount_point: str
        role_id: str
        role_type: Union[str, RoleTypes]

        def __init__(self, **kwargs): ...


namespace azure.mgmt.edgegateway.models.mount_point_map_py3

    class azure.mgmt.edgegateway.models.mount_point_map_py3.MountPointMap(Model):
        mount_point: str
        role_id: str
        role_type: Union[str, RoleTypes]

        def __init__(
                self, 
                *, 
                share_id: str, 
                **kwargs
            ) -> None: ...


namespace azure.mgmt.edgegateway.models.network_adapter

    class azure.mgmt.edgegateway.models.network_adapter.NetworkAdapter(Model):
        adapter_id: str
        adapter_position: NetworkAdapterPosition
        dns_servers: list[str]
        index: int
        ipv4_configuration: Ipv4Config
        ipv6_configuration: Ipv6Config
        ipv6_link_local_address: str
        label: str
        link_speed: long
        mac_address: str
        network_adapter_name: str
        node_id: str
        status: Union[str, NetworkAdapterStatus]

        def __init__(self, **kwargs): ...


namespace azure.mgmt.edgegateway.models.network_adapter_position

    class azure.mgmt.edgegateway.models.network_adapter_position.NetworkAdapterPosition(Model):
        network_group: Union[str, NetworkGroup]
        port: int

        def __init__(self, **kwargs): ...


namespace azure.mgmt.edgegateway.models.network_adapter_position_py3

    class azure.mgmt.edgegateway.models.network_adapter_position_py3.NetworkAdapterPosition(Model):
        network_group: Union[str, NetworkGroup]
        port: int

        def __init__(self, **kwargs) -> None: ...


namespace azure.mgmt.edgegateway.models.network_adapter_py3

    class azure.mgmt.edgegateway.models.network_adapter_py3.NetworkAdapter(Model):
        adapter_id: str
        adapter_position: NetworkAdapterPosition
        dns_servers: list[str]
        index: int
        ipv4_configuration: Ipv4Config
        ipv6_configuration: Ipv6Config
        ipv6_link_local_address: str
        label: str
        link_speed: long
        mac_address: str
        network_adapter_name: str
        node_id: str
        status: Union[str, NetworkAdapterStatus]

        def __init__(
                self, 
                *, 
                dhcp_status = ..., 
                rdma_status = ..., 
                **kwargs
            ) -> None: ...


namespace azure.mgmt.edgegateway.models.network_settings

    class azure.mgmt.edgegateway.models.network_settings.ARMBaseModel(Model):
        id: str
        name: str
        type: str

        def __init__(self, **kwargs): ...


    class azure.mgmt.edgegateway.models.network_settings.NetworkSettings(ARMBaseModel):
        id: str
        name: str
        network_adapters: list[NetworkAdapter]
        type: str

        def __init__(self, **kwargs): ...


namespace azure.mgmt.edgegateway.models.network_settings_py3

    class azure.mgmt.edgegateway.models.network_settings_py3.ARMBaseModel(Model):
        id: str
        name: str
        type: str

        def __init__(self, **kwargs) -> None: ...


    class azure.mgmt.edgegateway.models.network_settings_py3.NetworkSettings(ARMBaseModel):
        id: str
        name: str
        network_adapters: list[NetworkAdapter]
        type: str

        def __init__(self, **kwargs) -> None: ...


namespace azure.mgmt.edgegateway.models.operation

    class azure.mgmt.edgegateway.models.operation.Operation(Model):

        def __init__(self, **kwargs): ...


namespace azure.mgmt.edgegateway.models.operation_display

    class azure.mgmt.edgegateway.models.operation_display.OperationDisplay(Model):

        def __init__(self, **kwargs): ...


namespace azure.mgmt.edgegateway.models.operation_display_py3

    class azure.mgmt.edgegateway.models.operation_display_py3.OperationDisplay(Model):

        def __init__(
                self, 
                *, 
                description: str = ..., 
                operation: str = ..., 
                provider: str = ..., 
                resource: str = ..., 
                **kwargs
            ) -> None: ...


namespace azure.mgmt.edgegateway.models.operation_paged

    class azure.mgmt.edgegateway.models.operation_paged.OperationPaged(Paged):
        property raw: ClientRawResponse    # Read-only

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...


namespace azure.mgmt.edgegateway.models.operation_py3

    class azure.mgmt.edgegateway.models.operation_py3.Operation(Model):

        def __init__(
                self, 
                *, 
                display = ..., 
                name: str = ..., 
                origin: str = ..., 
                service_specification = ..., 
                **kwargs
            ) -> None: ...


namespace azure.mgmt.edgegateway.models.order

    class azure.mgmt.edgegateway.models.order.ARMBaseModel(Model):
        id: str
        name: str
        type: str

        def __init__(self, **kwargs): ...


    class azure.mgmt.edgegateway.models.order.Order(ARMBaseModel):
        delivery_tracking_info: list[TrackingInfo]
        id: str
        name: str
        order_history: list[OrderStatus]
        return_tracking_info: list[TrackingInfo]
        serial_number: str
        type: str

        def __init__(self, **kwargs): ...


namespace azure.mgmt.edgegateway.models.order_paged

    class azure.mgmt.edgegateway.models.order_paged.OrderPaged(Paged):
        property raw: ClientRawResponse    # Read-only

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...


namespace azure.mgmt.edgegateway.models.order_py3

    class azure.mgmt.edgegateway.models.order_py3.ARMBaseModel(Model):
        id: str
        name: str
        type: str

        def __init__(self, **kwargs) -> None: ...


    class azure.mgmt.edgegateway.models.order_py3.Order(ARMBaseModel):
        delivery_tracking_info: list[TrackingInfo]
        id: str
        name: str
        order_history: list[OrderStatus]
        return_tracking_info: list[TrackingInfo]
        serial_number: str
        type: str

        def __init__(
                self, 
                *, 
                contact_information, 
                current_status = ..., 
                shipping_address, 
                **kwargs
            ) -> None: ...


namespace azure.mgmt.edgegateway.models.order_status

    class azure.mgmt.edgegateway.models.order_status.OrderStatus(Model):
        update_date_time: datetime

        def __init__(self, **kwargs): ...


namespace azure.mgmt.edgegateway.models.order_status_py3

    class azure.mgmt.edgegateway.models.order_status_py3.OrderStatus(Model):
        update_date_time: datetime

        def __init__(
                self, 
                *, 
                comments: str = ..., 
                status, 
                **kwargs
            ) -> None: ...


namespace azure.mgmt.edgegateway.models.periodic_timer_event_trigger

    class azure.mgmt.edgegateway.models.periodic_timer_event_trigger.PeriodicTimerEventTrigger(Trigger):
        id: str
        name: str
        type: str

        def __init__(self, **kwargs): ...


    class azure.mgmt.edgegateway.models.periodic_timer_event_trigger.Trigger(ARMBaseModel):
        id: str
        name: str
        type: str

        def __init__(self, **kwargs): ...


namespace azure.mgmt.edgegateway.models.periodic_timer_event_trigger_py3

    class azure.mgmt.edgegateway.models.periodic_timer_event_trigger_py3.PeriodicTimerEventTrigger(Trigger):
        id: str
        name: str
        type: str

        def __init__(
                self, 
                *, 
                custom_context_tag: str = ..., 
                sink_info, 
                source_info, 
                **kwargs
            ) -> None: ...


    class azure.mgmt.edgegateway.models.periodic_timer_event_trigger_py3.Trigger(ARMBaseModel):
        id: str
        name: str
        type: str

        def __init__(self, **kwargs) -> None: ...


namespace azure.mgmt.edgegateway.models.periodic_timer_source_info

    class azure.mgmt.edgegateway.models.periodic_timer_source_info.PeriodicTimerSourceInfo(Model):

        def __init__(self, **kwargs): ...


namespace azure.mgmt.edgegateway.models.periodic_timer_source_info_py3

    class azure.mgmt.edgegateway.models.periodic_timer_source_info_py3.PeriodicTimerSourceInfo(Model):

        def __init__(
                self, 
                *, 
                schedule: str, 
                start_time, 
                topic: str = ..., 
                **kwargs
            ) -> None: ...


namespace azure.mgmt.edgegateway.models.refresh_details

    class azure.mgmt.edgegateway.models.refresh_details.RefreshDetails(Model):

        def __init__(self, **kwargs): ...


namespace azure.mgmt.edgegateway.models.refresh_details_py3

    class azure.mgmt.edgegateway.models.refresh_details_py3.RefreshDetails(Model):

        def __init__(
                self, 
                *, 
                error_manifest_file: str = ..., 
                in_progress_refresh_job_id: str = ..., 
                last_completed_refresh_job_time_in_utc = ..., 
                last_job: str = ..., 
                **kwargs
            ) -> None: ...


namespace azure.mgmt.edgegateway.models.role

    class azure.mgmt.edgegateway.models.role.ARMBaseModel(Model):
        id: str
        name: str
        type: str

        def __init__(self, **kwargs): ...


    class azure.mgmt.edgegateway.models.role.Role(ARMBaseModel):
        id: str
        name: str
        type: str

        def __init__(self, **kwargs): ...


namespace azure.mgmt.edgegateway.models.role_paged

    class azure.mgmt.edgegateway.models.role_paged.RolePaged(Paged):
        property raw: ClientRawResponse    # Read-only

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...


namespace azure.mgmt.edgegateway.models.role_py3

    class azure.mgmt.edgegateway.models.role_py3.ARMBaseModel(Model):
        id: str
        name: str
        type: str

        def __init__(self, **kwargs) -> None: ...


    class azure.mgmt.edgegateway.models.role_py3.Role(ARMBaseModel):
        id: str
        name: str
        type: str

        def __init__(self, **kwargs) -> None: ...


namespace azure.mgmt.edgegateway.models.role_sink_info

    class azure.mgmt.edgegateway.models.role_sink_info.RoleSinkInfo(Model):

        def __init__(self, **kwargs): ...


namespace azure.mgmt.edgegateway.models.role_sink_info_py3

    class azure.mgmt.edgegateway.models.role_sink_info_py3.RoleSinkInfo(Model):

        def __init__(
                self, 
                *, 
                role_id: str, 
                **kwargs
            ) -> None: ...


namespace azure.mgmt.edgegateway.models.security_settings

    class azure.mgmt.edgegateway.models.security_settings.ARMBaseModel(Model):
        id: str
        name: str
        type: str

        def __init__(self, **kwargs): ...


    class azure.mgmt.edgegateway.models.security_settings.SecuritySettings(ARMBaseModel):
        id: str
        name: str
        type: str

        def __init__(self, **kwargs): ...


namespace azure.mgmt.edgegateway.models.security_settings_py3

    class azure.mgmt.edgegateway.models.security_settings_py3.ARMBaseModel(Model):
        id: str
        name: str
        type: str

        def __init__(self, **kwargs) -> None: ...


    class azure.mgmt.edgegateway.models.security_settings_py3.SecuritySettings(ARMBaseModel):
        id: str
        name: str
        type: str

        def __init__(
                self, 
                *, 
                device_admin_password, 
                **kwargs
            ) -> None: ...


namespace azure.mgmt.edgegateway.models.service_specification

    class azure.mgmt.edgegateway.models.service_specification.ServiceSpecification(Model):

        def __init__(self, **kwargs): ...


namespace azure.mgmt.edgegateway.models.service_specification_py3

    class azure.mgmt.edgegateway.models.service_specification_py3.ServiceSpecification(Model):

        def __init__(
                self, 
                *, 
                metric_specifications = ..., 
                **kwargs
            ) -> None: ...


namespace azure.mgmt.edgegateway.models.share

    class azure.mgmt.edgegateway.models.share.ARMBaseModel(Model):
        id: str
        name: str
        type: str

        def __init__(self, **kwargs): ...


    class azure.mgmt.edgegateway.models.share.Share(ARMBaseModel):
        id: str
        name: str
        share_mappings: list[MountPointMap]
        type: str

        def __init__(self, **kwargs): ...


namespace azure.mgmt.edgegateway.models.share_access_right

    class azure.mgmt.edgegateway.models.share_access_right.ShareAccessRight(Model):

        def __init__(self, **kwargs): ...


namespace azure.mgmt.edgegateway.models.share_access_right_py3

    class azure.mgmt.edgegateway.models.share_access_right_py3.ShareAccessRight(Model):

        def __init__(
                self, 
                *, 
                access_type, 
                share_id: str, 
                **kwargs
            ) -> None: ...


namespace azure.mgmt.edgegateway.models.share_paged

    class azure.mgmt.edgegateway.models.share_paged.SharePaged(Paged):
        property raw: ClientRawResponse    # Read-only

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...


namespace azure.mgmt.edgegateway.models.share_py3

    class azure.mgmt.edgegateway.models.share_py3.ARMBaseModel(Model):
        id: str
        name: str
        type: str

        def __init__(self, **kwargs) -> None: ...


    class azure.mgmt.edgegateway.models.share_py3.Share(ARMBaseModel):
        id: str
        name: str
        share_mappings: list[MountPointMap]
        type: str

        def __init__(
                self, 
                *, 
                access_protocol, 
                azure_container_info = ..., 
                client_access_rights = ..., 
                data_policy = ..., 
                description: str = ..., 
                monitoring_status, 
                refresh_details = ..., 
                share_status, 
                user_access_rights = ..., 
                **kwargs
            ) -> None: ...


namespace azure.mgmt.edgegateway.models.sku

    class azure.mgmt.edgegateway.models.sku.Sku(Model):

        def __init__(self, **kwargs): ...


namespace azure.mgmt.edgegateway.models.sku_py3

    class azure.mgmt.edgegateway.models.sku_py3.Sku(Model):

        def __init__(
                self, 
                *, 
                name = ..., 
                tier = ..., 
                **kwargs
            ) -> None: ...


namespace azure.mgmt.edgegateway.models.storage_account_credential

    class azure.mgmt.edgegateway.models.storage_account_credential.ARMBaseModel(Model):
        id: str
        name: str
        type: str

        def __init__(self, **kwargs): ...


    class azure.mgmt.edgegateway.models.storage_account_credential.StorageAccountCredential(ARMBaseModel):
        id: str
        name: str
        type: str

        def __init__(self, **kwargs): ...


namespace azure.mgmt.edgegateway.models.storage_account_credential_paged

    class azure.mgmt.edgegateway.models.storage_account_credential_paged.StorageAccountCredentialPaged(Paged):
        property raw: ClientRawResponse    # Read-only

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...


namespace azure.mgmt.edgegateway.models.storage_account_credential_py3

    class azure.mgmt.edgegateway.models.storage_account_credential_py3.ARMBaseModel(Model):
        id: str
        name: str
        type: str

        def __init__(self, **kwargs) -> None: ...


    class azure.mgmt.edgegateway.models.storage_account_credential_py3.StorageAccountCredential(ARMBaseModel):
        id: str
        name: str
        type: str

        def __init__(
                self, 
                *, 
                account_key = ..., 
                account_type, 
                alias: str, 
                blob_domain_name: str = ..., 
                connection_string: str = ..., 
                ssl_status, 
                user_name: str = ..., 
                **kwargs
            ) -> None: ...


namespace azure.mgmt.edgegateway.models.symmetric_key

    class azure.mgmt.edgegateway.models.symmetric_key.SymmetricKey(Model):

        def __init__(self, **kwargs): ...


namespace azure.mgmt.edgegateway.models.symmetric_key_py3

    class azure.mgmt.edgegateway.models.symmetric_key_py3.SymmetricKey(Model):

        def __init__(
                self, 
                *, 
                connection_string = ..., 
                **kwargs
            ) -> None: ...


namespace azure.mgmt.edgegateway.models.tracking_info

    class azure.mgmt.edgegateway.models.tracking_info.TrackingInfo(Model):

        def __init__(self, **kwargs): ...


namespace azure.mgmt.edgegateway.models.tracking_info_py3

    class azure.mgmt.edgegateway.models.tracking_info_py3.TrackingInfo(Model):

        def __init__(
                self, 
                *, 
                carrier_name: str = ..., 
                serial_number: str = ..., 
                tracking_id: str = ..., 
                tracking_url: str = ..., 
                **kwargs
            ) -> None: ...


namespace azure.mgmt.edgegateway.models.trigger

    class azure.mgmt.edgegateway.models.trigger.ARMBaseModel(Model):
        id: str
        name: str
        type: str

        def __init__(self, **kwargs): ...


    class azure.mgmt.edgegateway.models.trigger.Trigger(ARMBaseModel):
        id: str
        name: str
        type: str

        def __init__(self, **kwargs): ...


namespace azure.mgmt.edgegateway.models.trigger_paged

    class azure.mgmt.edgegateway.models.trigger_paged.TriggerPaged(Paged):
        property raw: ClientRawResponse    # Read-only

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...


namespace azure.mgmt.edgegateway.models.trigger_py3

    class azure.mgmt.edgegateway.models.trigger_py3.ARMBaseModel(Model):
        id: str
        name: str
        type: str

        def __init__(self, **kwargs) -> None: ...


    class azure.mgmt.edgegateway.models.trigger_py3.Trigger(ARMBaseModel):
        id: str
        name: str
        type: str

        def __init__(self, **kwargs) -> None: ...


namespace azure.mgmt.edgegateway.models.update_download_progress

    class azure.mgmt.edgegateway.models.update_download_progress.UpdateDownloadProgress(Model):
        download_phase: Union[str, DownloadPhase]
        number_of_updates_downloaded: int
        number_of_updates_to_download: int
        percent_complete: int
        total_bytes_downloaded: float
        total_bytes_to_download: float

        def __init__(self, **kwargs): ...


namespace azure.mgmt.edgegateway.models.update_download_progress_py3

    class azure.mgmt.edgegateway.models.update_download_progress_py3.UpdateDownloadProgress(Model):
        download_phase: Union[str, DownloadPhase]
        number_of_updates_downloaded: int
        number_of_updates_to_download: int
        percent_complete: int
        total_bytes_downloaded: float
        total_bytes_to_download: float

        def __init__(self, **kwargs) -> None: ...


namespace azure.mgmt.edgegateway.models.update_install_progress

    class azure.mgmt.edgegateway.models.update_install_progress.UpdateInstallProgress(Model):
        number_of_updates_installed: int
        number_of_updates_to_install: int
        percent_complete: int

        def __init__(self, **kwargs): ...


namespace azure.mgmt.edgegateway.models.update_install_progress_py3

    class azure.mgmt.edgegateway.models.update_install_progress_py3.UpdateInstallProgress(Model):
        number_of_updates_installed: int
        number_of_updates_to_install: int
        percent_complete: int

        def __init__(self, **kwargs) -> None: ...


namespace azure.mgmt.edgegateway.models.update_summary

    class azure.mgmt.edgegateway.models.update_summary.ARMBaseModel(Model):
        id: str
        name: str
        type: str

        def __init__(self, **kwargs): ...


    class azure.mgmt.edgegateway.models.update_summary.UpdateSummary(ARMBaseModel):
        id: str
        in_progress_download_job_id: str
        in_progress_download_job_started_date_time: datetime
        in_progress_install_job_id: str
        in_progress_install_job_started_date_time: datetime
        last_completed_download_job_date_time: datetime
        last_completed_install_job_date_time: datetime
        name: str
        ongoing_update_operation: Union[str, UpdateOperation]
        reboot_behavior: Union[str, InstallRebootBehavior]
        total_number_of_updates_available: int
        total_number_of_updates_pending_download: int
        total_number_of_updates_pending_install: int
        total_update_size_in_bytes: float
        type: str
        update_titles: list[str]

        def __init__(self, **kwargs): ...


namespace azure.mgmt.edgegateway.models.update_summary_py3

    class azure.mgmt.edgegateway.models.update_summary_py3.ARMBaseModel(Model):
        id: str
        name: str
        type: str

        def __init__(self, **kwargs) -> None: ...


    class azure.mgmt.edgegateway.models.update_summary_py3.UpdateSummary(ARMBaseModel):
        id: str
        in_progress_download_job_id: str
        in_progress_download_job_started_date_time: datetime
        in_progress_install_job_id: str
        in_progress_install_job_started_date_time: datetime
        last_completed_download_job_date_time: datetime
        last_completed_install_job_date_time: datetime
        name: str
        ongoing_update_operation: Union[str, UpdateOperation]
        reboot_behavior: Union[str, InstallRebootBehavior]
        total_number_of_updates_available: int
        total_number_of_updates_pending_download: int
        total_number_of_updates_pending_install: int
        total_update_size_in_bytes: float
        type: str
        update_titles: list[str]

        def __init__(
                self, 
                *, 
                device_last_scanned_date_time = ..., 
                device_version_number: str = ..., 
                friendly_device_version_name: str = ..., 
                last_completed_scan_job_date_time = ..., 
                **kwargs
            ) -> None: ...


namespace azure.mgmt.edgegateway.models.upload_certificate_request

    class azure.mgmt.edgegateway.models.upload_certificate_request.UploadCertificateRequest(Model):

        def __init__(self, **kwargs): ...


namespace azure.mgmt.edgegateway.models.upload_certificate_request_py3

    class azure.mgmt.edgegateway.models.upload_certificate_request_py3.UploadCertificateRequest(Model):

        def __init__(
                self, 
                *, 
                authentication_type = ..., 
                certificate: str, 
                **kwargs
            ) -> None: ...


namespace azure.mgmt.edgegateway.models.upload_certificate_response

    class azure.mgmt.edgegateway.models.upload_certificate_response.UploadCertificateResponse(Model):

        def __init__(self, **kwargs): ...


namespace azure.mgmt.edgegateway.models.upload_certificate_response_py3

    class azure.mgmt.edgegateway.models.upload_certificate_response_py3.UploadCertificateResponse(Model):

        def __init__(
                self, 
                *, 
                aad_authority: str, 
                aad_tenant_id: str, 
                auth_type = ..., 
                azure_management_endpoint_audience: str, 
                resource_id: str, 
                service_principal_client_id: str, 
                service_principal_object_id: str, 
                **kwargs
            ) -> None: ...


namespace azure.mgmt.edgegateway.models.user

    class azure.mgmt.edgegateway.models.user.ARMBaseModel(Model):
        id: str
        name: str
        type: str

        def __init__(self, **kwargs): ...


    class azure.mgmt.edgegateway.models.user.User(ARMBaseModel):
        id: str
        name: str
        type: str

        def __init__(self, **kwargs): ...


namespace azure.mgmt.edgegateway.models.user_access_right

    class azure.mgmt.edgegateway.models.user_access_right.UserAccessRight(Model):

        def __init__(self, **kwargs): ...


namespace azure.mgmt.edgegateway.models.user_access_right_py3

    class azure.mgmt.edgegateway.models.user_access_right_py3.UserAccessRight(Model):

        def __init__(
                self, 
                *, 
                access_type, 
                user_id: str, 
                **kwargs
            ) -> None: ...


namespace azure.mgmt.edgegateway.models.user_paged

    class azure.mgmt.edgegateway.models.user_paged.UserPaged(Paged):
        property raw: ClientRawResponse    # Read-only

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...


namespace azure.mgmt.edgegateway.models.user_py3

    class azure.mgmt.edgegateway.models.user_py3.ARMBaseModel(Model):
        id: str
        name: str
        type: str

        def __init__(self, **kwargs) -> None: ...


    class azure.mgmt.edgegateway.models.user_py3.User(ARMBaseModel):
        id: str
        name: str
        type: str

        def __init__(
                self, 
                *, 
                encrypted_password = ..., 
                share_access_rights = ..., 
                **kwargs
            ) -> None: ...


namespace azure.mgmt.edgegateway.operations

    class azure.mgmt.edgegateway.operations.AlertsOperations:
        api_version

        def __init__(
                self, 
                client, 
                config, 
                serializer, 
                deserializer
            ): ...

        def get(
                self, 
                device_name: str, 
                name: str, 
                resource_group_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[Alert, ClientRawResponse]: ...

        def list_by_data_box_edge_device(
                self, 
                device_name: str, 
                resource_group_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> AlertPaged[Alert]: ...


    class azure.mgmt.edgegateway.operations.BandwidthSchedulesOperations:
        api_version

        def __init__(
                self, 
                client, 
                config, 
                serializer, 
                deserializer
            ): ...

        def create_or_update(
                self, 
                device_name: str, 
                name: str, 
                parameters: BandwidthSchedule, 
                resource_group_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                polling = True, 
                **operation_config
            ) -> AzureOperationPoller[BandwidthSchedule]: ...

        def delete(
                self, 
                device_name: str, 
                name: str, 
                resource_group_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                polling = True, 
                **operation_config
            ) -> Union[AzureOperationPoller[None], AzureOperationPoller[ClientRawResponse[None]]]: ...

        def get(
                self, 
                device_name: str, 
                name: str, 
                resource_group_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[BandwidthSchedule, ClientRawResponse]: ...

        def list_by_data_box_edge_device(
                self, 
                device_name: str, 
                resource_group_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> BandwidthSchedulePaged[BandwidthSchedule]: ...


    class azure.mgmt.edgegateway.operations.DevicesOperations:
        api_version

        def __init__(
                self, 
                client, 
                config, 
                serializer, 
                deserializer
            ): ...

        def create_or_update(
                self, 
                device_name: str, 
                data_box_edge_device: DataBoxEdgeDevice, 
                resource_group_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                polling = True, 
                **operation_config
            ) -> AzureOperationPoller[DataBoxEdgeDevice]: ...

        def create_or_update_security_settings(
                self, 
                device_name: str, 
                resource_group_name: str, 
                device_admin_password: AsymmetricEncryptedSecret, 
                custom_headers: dict = None, 
                raw: bool = False, 
                polling = True, 
                **operation_config
            ) -> Union[AzureOperationPoller[None], AzureOperationPoller[ClientRawResponse[None]]]: ...

        def delete(
                self, 
                device_name: str, 
                resource_group_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                polling = True, 
                **operation_config
            ) -> Union[AzureOperationPoller[None], AzureOperationPoller[ClientRawResponse[None]]]: ...

        def download_updates(
                self, 
                device_name: str, 
                resource_group_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                polling = True, 
                **operation_config
            ) -> Union[AzureOperationPoller[None], AzureOperationPoller[ClientRawResponse[None]]]: ...

        def get(
                self, 
                device_name: str, 
                resource_group_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[DataBoxEdgeDevice, ClientRawResponse]: ...

        def get_extended_information(
                self, 
                device_name: str, 
                resource_group_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> DataBoxEdgeDeviceExtendedInfo: ...

        def get_network_settings(
                self, 
                device_name: str, 
                resource_group_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[NetworkSettings, ClientRawResponse]: ...

        def get_update_summary(
                self, 
                device_name: str, 
                resource_group_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[UpdateSummary, ClientRawResponse]: ...

        def install_updates(
                self, 
                device_name: str, 
                resource_group_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                polling = True, 
                **operation_config
            ) -> Union[AzureOperationPoller[None], AzureOperationPoller[ClientRawResponse[None]]]: ...

        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                expand: str = None, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> DataBoxEdgeDevicePaged[DataBoxEdgeDevice]: ...

        def list_by_subscription(
                self, 
                expand: str = None, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> DataBoxEdgeDevicePaged[DataBoxEdgeDevice]: ...

        def scan_for_updates(
                self, 
                device_name: str, 
                resource_group_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                polling = True, 
                **operation_config
            ) -> Union[AzureOperationPoller[None], AzureOperationPoller[ClientRawResponse[None]]]: ...

        def update(
                self, 
                device_name: str, 
                resource_group_name: str, 
                tags: dict[str, str] = None, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[DataBoxEdgeDevice, ClientRawResponse]: ...

        def upload_certificate(
                self, 
                device_name: str, 
                resource_group_name: str, 
                certificate: str, 
                authentication_type: Union[str, AuthenticationType] = None, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[UploadCertificateResponse, ClientRawResponse]: ...


    class azure.mgmt.edgegateway.operations.JobsOperations:
        api_version

        def __init__(
                self, 
                client, 
                config, 
                serializer, 
                deserializer
            ): ...

        def get(
                self, 
                device_name: str, 
                name: str, 
                resource_group_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[Job, ClientRawResponse]: ...


    class azure.mgmt.edgegateway.operations.Operations:
        api_version

        def __init__(
                self, 
                client, 
                config, 
                serializer, 
                deserializer
            ): ...

        def list(
                self, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> OperationPaged[Operation]: ...


    class azure.mgmt.edgegateway.operations.OperationsStatusOperations:
        api_version

        def __init__(
                self, 
                client, 
                config, 
                serializer, 
                deserializer
            ): ...

        def get(
                self, 
                device_name: str, 
                name: str, 
                resource_group_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[Job, ClientRawResponse]: ...


    class azure.mgmt.edgegateway.operations.OrdersOperations:
        api_version

        def __init__(
                self, 
                client, 
                config, 
                serializer, 
                deserializer
            ): ...

        def create_or_update(
                self, 
                device_name: str, 
                order: Order, 
                resource_group_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                polling = True, 
                **operation_config
            ) -> AzureOperationPoller[Order]: ...

        def delete(
                self, 
                device_name: str, 
                resource_group_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                polling = True, 
                **operation_config
            ) -> Union[AzureOperationPoller[None], AzureOperationPoller[ClientRawResponse[None]]]: ...

        def get(
                self, 
                device_name: str, 
                resource_group_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[Order, ClientRawResponse]: ...

        def list_by_data_box_edge_device(
                self, 
                device_name: str, 
                resource_group_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> OrderPaged[Order]: ...


    class azure.mgmt.edgegateway.operations.RolesOperations:
        api_version

        def __init__(
                self, 
                client, 
                config, 
                serializer, 
                deserializer
            ): ...

        def create_or_update(
                self, 
                device_name: str, 
                name: str, 
                role: Role, 
                resource_group_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                polling = True, 
                **operation_config
            ) -> AzureOperationPoller[Role]: ...

        def delete(
                self, 
                device_name: str, 
                name: str, 
                resource_group_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                polling = True, 
                **operation_config
            ) -> Union[AzureOperationPoller[None], AzureOperationPoller[ClientRawResponse[None]]]: ...

        def get(
                self, 
                device_name: str, 
                name: str, 
                resource_group_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[Role, ClientRawResponse]: ...

        def list_by_data_box_edge_device(
                self, 
                device_name: str, 
                resource_group_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> RolePaged[Role]: ...


    class azure.mgmt.edgegateway.operations.SharesOperations:
        api_version

        def __init__(
                self, 
                client, 
                config, 
                serializer, 
                deserializer
            ): ...

        def create_or_update(
                self, 
                device_name: str, 
                name: str, 
                share: Share, 
                resource_group_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                polling = True, 
                **operation_config
            ) -> AzureOperationPoller[Share]: ...

        def delete(
                self, 
                device_name: str, 
                name: str, 
                resource_group_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                polling = True, 
                **operation_config
            ) -> Union[AzureOperationPoller[None], AzureOperationPoller[ClientRawResponse[None]]]: ...

        def get(
                self, 
                device_name: str, 
                name: str, 
                resource_group_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[Share, ClientRawResponse]: ...

        def list_by_data_box_edge_device(
                self, 
                device_name: str, 
                resource_group_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> SharePaged[Share]: ...

        def refresh(
                self, 
                device_name: str, 
                name: str, 
                resource_group_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                polling = True, 
                **operation_config
            ) -> Union[AzureOperationPoller[None], AzureOperationPoller[ClientRawResponse[None]]]: ...


    class azure.mgmt.edgegateway.operations.StorageAccountCredentialsOperations:
        api_version

        def __init__(
                self, 
                client, 
                config, 
                serializer, 
                deserializer
            ): ...

        def create_or_update(
                self, 
                device_name: str, 
                name: str, 
                storage_account_credential: StorageAccountCredential, 
                resource_group_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                polling = True, 
                **operation_config
            ) -> AzureOperationPoller[StorageAccountCredential]: ...

        def delete(
                self, 
                device_name: str, 
                name: str, 
                resource_group_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                polling = True, 
                **operation_config
            ) -> Union[AzureOperationPoller[None], AzureOperationPoller[ClientRawResponse[None]]]: ...

        def get(
                self, 
                device_name: str, 
                name: str, 
                resource_group_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[StorageAccountCredential, ClientRawResponse]: ...

        def list_by_data_box_edge_device(
                self, 
                device_name: str, 
                resource_group_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> StorageAccountCredentialPaged[StorageAccountCredential]: ...


    class azure.mgmt.edgegateway.operations.TriggersOperations:
        api_version

        def __init__(
                self, 
                client, 
                config, 
                serializer, 
                deserializer
            ): ...

        def create_or_update(
                self, 
                device_name: str, 
                name: str, 
                trigger: Trigger, 
                resource_group_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                polling = True, 
                **operation_config
            ) -> AzureOperationPoller[Trigger]: ...

        def delete(
                self, 
                device_name: str, 
                name: str, 
                resource_group_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                polling = True, 
                **operation_config
            ) -> Union[AzureOperationPoller[None], AzureOperationPoller[ClientRawResponse[None]]]: ...

        def get(
                self, 
                device_name: str, 
                name: str, 
                resource_group_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[Trigger, ClientRawResponse]: ...

        def list_by_data_box_edge_device(
                self, 
                device_name: str, 
                resource_group_name: str, 
                expand: str = None, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> TriggerPaged[Trigger]: ...


    class azure.mgmt.edgegateway.operations.UsersOperations:
        api_version

        def __init__(
                self, 
                client, 
                config, 
                serializer, 
                deserializer
            ): ...

        def create_or_update(
                self, 
                device_name: str, 
                name: str, 
                resource_group_name: str, 
                encrypted_password: AsymmetricEncryptedSecret = None, 
                share_access_rights: list[ShareAccessRight] = None, 
                custom_headers: dict = None, 
                raw: bool = False, 
                polling = True, 
                **operation_config
            ) -> AzureOperationPoller[User]: ...

        def delete(
                self, 
                device_name: str, 
                name: str, 
                resource_group_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                polling = True, 
                **operation_config
            ) -> Union[AzureOperationPoller[None], AzureOperationPoller[ClientRawResponse[None]]]: ...

        def get(
                self, 
                device_name: str, 
                name: str, 
                resource_group_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[User, ClientRawResponse]: ...

        def list_by_data_box_edge_device(
                self, 
                device_name: str, 
                resource_group_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> UserPaged[User]: ...


namespace azure.mgmt.edgegateway.operations.alerts_operations

    class azure.mgmt.edgegateway.operations.alerts_operations.AlertsOperations:
        api_version

        def __init__(
                self, 
                client, 
                config, 
                serializer, 
                deserializer
            ): ...

        def get(
                self, 
                device_name: str, 
                name: str, 
                resource_group_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[Alert, ClientRawResponse]: ...

        def list_by_data_box_edge_device(
                self, 
                device_name: str, 
                resource_group_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> AlertPaged[Alert]: ...


namespace azure.mgmt.edgegateway.operations.bandwidth_schedules_operations

    class azure.mgmt.edgegateway.operations.bandwidth_schedules_operations.BandwidthSchedulesOperations:
        api_version

        def __init__(
                self, 
                client, 
                config, 
                serializer, 
                deserializer
            ): ...

        def create_or_update(
                self, 
                device_name: str, 
                name: str, 
                parameters: BandwidthSchedule, 
                resource_group_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                polling = True, 
                **operation_config
            ) -> AzureOperationPoller[BandwidthSchedule]: ...

        def delete(
                self, 
                device_name: str, 
                name: str, 
                resource_group_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                polling = True, 
                **operation_config
            ) -> Union[AzureOperationPoller[None], AzureOperationPoller[ClientRawResponse[None]]]: ...

        def get(
                self, 
                device_name: str, 
                name: str, 
                resource_group_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[BandwidthSchedule, ClientRawResponse]: ...

        def list_by_data_box_edge_device(
                self, 
                device_name: str, 
                resource_group_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> BandwidthSchedulePaged[BandwidthSchedule]: ...


namespace azure.mgmt.edgegateway.operations.devices_operations

    class azure.mgmt.edgegateway.operations.devices_operations.DevicesOperations:
        api_version

        def __init__(
                self, 
                client, 
                config, 
                serializer, 
                deserializer
            ): ...

        def create_or_update(
                self, 
                device_name: str, 
                data_box_edge_device: DataBoxEdgeDevice, 
                resource_group_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                polling = True, 
                **operation_config
            ) -> AzureOperationPoller[DataBoxEdgeDevice]: ...

        def create_or_update_security_settings(
                self, 
                device_name: str, 
                resource_group_name: str, 
                device_admin_password: AsymmetricEncryptedSecret, 
                custom_headers: dict = None, 
                raw: bool = False, 
                polling = True, 
                **operation_config
            ) -> Union[AzureOperationPoller[None], AzureOperationPoller[ClientRawResponse[None]]]: ...

        def delete(
                self, 
                device_name: str, 
                resource_group_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                polling = True, 
                **operation_config
            ) -> Union[AzureOperationPoller[None], AzureOperationPoller[ClientRawResponse[None]]]: ...

        def download_updates(
                self, 
                device_name: str, 
                resource_group_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                polling = True, 
                **operation_config
            ) -> Union[AzureOperationPoller[None], AzureOperationPoller[ClientRawResponse[None]]]: ...

        def get(
                self, 
                device_name: str, 
                resource_group_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[DataBoxEdgeDevice, ClientRawResponse]: ...

        def get_extended_information(
                self, 
                device_name: str, 
                resource_group_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> DataBoxEdgeDeviceExtendedInfo: ...

        def get_network_settings(
                self, 
                device_name: str, 
                resource_group_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[NetworkSettings, ClientRawResponse]: ...

        def get_update_summary(
                self, 
                device_name: str, 
                resource_group_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[UpdateSummary, ClientRawResponse]: ...

        def install_updates(
                self, 
                device_name: str, 
                resource_group_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                polling = True, 
                **operation_config
            ) -> Union[AzureOperationPoller[None], AzureOperationPoller[ClientRawResponse[None]]]: ...

        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                expand: str = None, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> DataBoxEdgeDevicePaged[DataBoxEdgeDevice]: ...

        def list_by_subscription(
                self, 
                expand: str = None, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> DataBoxEdgeDevicePaged[DataBoxEdgeDevice]: ...

        def scan_for_updates(
                self, 
                device_name: str, 
                resource_group_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                polling = True, 
                **operation_config
            ) -> Union[AzureOperationPoller[None], AzureOperationPoller[ClientRawResponse[None]]]: ...

        def update(
                self, 
                device_name: str, 
                resource_group_name: str, 
                tags: dict[str, str] = None, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[DataBoxEdgeDevice, ClientRawResponse]: ...

        def upload_certificate(
                self, 
                device_name: str, 
                resource_group_name: str, 
                certificate: str, 
                authentication_type: Union[str, AuthenticationType] = None, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[UploadCertificateResponse, ClientRawResponse]: ...


namespace azure.mgmt.edgegateway.operations.jobs_operations

    class azure.mgmt.edgegateway.operations.jobs_operations.JobsOperations:
        api_version

        def __init__(
                self, 
                client, 
                config, 
                serializer, 
                deserializer
            ): ...

        def get(
                self, 
                device_name: str, 
                name: str, 
                resource_group_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[Job, ClientRawResponse]: ...


namespace azure.mgmt.edgegateway.operations.operations

    class azure.mgmt.edgegateway.operations.operations.Operations:
        api_version

        def __init__(
                self, 
                client, 
                config, 
                serializer, 
                deserializer
            ): ...

        def list(
                self, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> OperationPaged[Operation]: ...


namespace azure.mgmt.edgegateway.operations.operations_status_operations

    class azure.mgmt.edgegateway.operations.operations_status_operations.OperationsStatusOperations:
        api_version

        def __init__(
                self, 
                client, 
                config, 
                serializer, 
                deserializer
            ): ...

        def get(
                self, 
                device_name: str, 
                name: str, 
                resource_group_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[Job, ClientRawResponse]: ...


namespace azure.mgmt.edgegateway.operations.orders_operations

    class azure.mgmt.edgegateway.operations.orders_operations.OrdersOperations:
        api_version

        def __init__(
                self, 
                client, 
                config, 
                serializer, 
                deserializer
            ): ...

        def create_or_update(
                self, 
                device_name: str, 
                order: Order, 
                resource_group_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                polling = True, 
                **operation_config
            ) -> AzureOperationPoller[Order]: ...

        def delete(
                self, 
                device_name: str, 
                resource_group_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                polling = True, 
                **operation_config
            ) -> Union[AzureOperationPoller[None], AzureOperationPoller[ClientRawResponse[None]]]: ...

        def get(
                self, 
                device_name: str, 
                resource_group_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[Order, ClientRawResponse]: ...

        def list_by_data_box_edge_device(
                self, 
                device_name: str, 
                resource_group_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> OrderPaged[Order]: ...


namespace azure.mgmt.edgegateway.operations.roles_operations

    class azure.mgmt.edgegateway.operations.roles_operations.RolesOperations:
        api_version

        def __init__(
                self, 
                client, 
                config, 
                serializer, 
                deserializer
            ): ...

        def create_or_update(
                self, 
                device_name: str, 
                name: str, 
                role: Role, 
                resource_group_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                polling = True, 
                **operation_config
            ) -> AzureOperationPoller[Role]: ...

        def delete(
                self, 
                device_name: str, 
                name: str, 
                resource_group_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                polling = True, 
                **operation_config
            ) -> Union[AzureOperationPoller[None], AzureOperationPoller[ClientRawResponse[None]]]: ...

        def get(
                self, 
                device_name: str, 
                name: str, 
                resource_group_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[Role, ClientRawResponse]: ...

        def list_by_data_box_edge_device(
                self, 
                device_name: str, 
                resource_group_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> RolePaged[Role]: ...


namespace azure.mgmt.edgegateway.operations.shares_operations

    class azure.mgmt.edgegateway.operations.shares_operations.SharesOperations:
        api_version

        def __init__(
                self, 
                client, 
                config, 
                serializer, 
                deserializer
            ): ...

        def create_or_update(
                self, 
                device_name: str, 
                name: str, 
                share: Share, 
                resource_group_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                polling = True, 
                **operation_config
            ) -> AzureOperationPoller[Share]: ...

        def delete(
                self, 
                device_name: str, 
                name: str, 
                resource_group_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                polling = True, 
                **operation_config
            ) -> Union[AzureOperationPoller[None], AzureOperationPoller[ClientRawResponse[None]]]: ...

        def get(
                self, 
                device_name: str, 
                name: str, 
                resource_group_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[Share, ClientRawResponse]: ...

        def list_by_data_box_edge_device(
                self, 
                device_name: str, 
                resource_group_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> SharePaged[Share]: ...

        def refresh(
                self, 
                device_name: str, 
                name: str, 
                resource_group_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                polling = True, 
                **operation_config
            ) -> Union[AzureOperationPoller[None], AzureOperationPoller[ClientRawResponse[None]]]: ...


namespace azure.mgmt.edgegateway.operations.storage_account_credentials_operations

    class azure.mgmt.edgegateway.operations.storage_account_credentials_operations.StorageAccountCredentialsOperations:
        api_version

        def __init__(
                self, 
                client, 
                config, 
                serializer, 
                deserializer
            ): ...

        def create_or_update(
                self, 
                device_name: str, 
                name: str, 
                storage_account_credential: StorageAccountCredential, 
                resource_group_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                polling = True, 
                **operation_config
            ) -> AzureOperationPoller[StorageAccountCredential]: ...

        def delete(
                self, 
                device_name: str, 
                name: str, 
                resource_group_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                polling = True, 
                **operation_config
            ) -> Union[AzureOperationPoller[None], AzureOperationPoller[ClientRawResponse[None]]]: ...

        def get(
                self, 
                device_name: str, 
                name: str, 
                resource_group_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[StorageAccountCredential, ClientRawResponse]: ...

        def list_by_data_box_edge_device(
                self, 
                device_name: str, 
                resource_group_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> StorageAccountCredentialPaged[StorageAccountCredential]: ...


namespace azure.mgmt.edgegateway.operations.triggers_operations

    class azure.mgmt.edgegateway.operations.triggers_operations.TriggersOperations:
        api_version

        def __init__(
                self, 
                client, 
                config, 
                serializer, 
                deserializer
            ): ...

        def create_or_update(
                self, 
                device_name: str, 
                name: str, 
                trigger: Trigger, 
                resource_group_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                polling = True, 
                **operation_config
            ) -> AzureOperationPoller[Trigger]: ...

        def delete(
                self, 
                device_name: str, 
                name: str, 
                resource_group_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                polling = True, 
                **operation_config
            ) -> Union[AzureOperationPoller[None], AzureOperationPoller[ClientRawResponse[None]]]: ...

        def get(
                self, 
                device_name: str, 
                name: str, 
                resource_group_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[Trigger, ClientRawResponse]: ...

        def list_by_data_box_edge_device(
                self, 
                device_name: str, 
                resource_group_name: str, 
                expand: str = None, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> TriggerPaged[Trigger]: ...


namespace azure.mgmt.edgegateway.operations.users_operations

    class azure.mgmt.edgegateway.operations.users_operations.UsersOperations:
        api_version

        def __init__(
                self, 
                client, 
                config, 
                serializer, 
                deserializer
            ): ...

        def create_or_update(
                self, 
                device_name: str, 
                name: str, 
                resource_group_name: str, 
                encrypted_password: AsymmetricEncryptedSecret = None, 
                share_access_rights: list[ShareAccessRight] = None, 
                custom_headers: dict = None, 
                raw: bool = False, 
                polling = True, 
                **operation_config
            ) -> AzureOperationPoller[User]: ...

        def delete(
                self, 
                device_name: str, 
                name: str, 
                resource_group_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                polling = True, 
                **operation_config
            ) -> Union[AzureOperationPoller[None], AzureOperationPoller[ClientRawResponse[None]]]: ...

        def get(
                self, 
                device_name: str, 
                name: str, 
                resource_group_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[User, ClientRawResponse]: ...

        def list_by_data_box_edge_device(
                self, 
                device_name: str, 
                resource_group_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> UserPaged[User]: ...


```