```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.storageimportexport

    class azure.mgmt.storageimportexport.StorageImportExport: implements ContextManager 
        bit_locker_keys: BitLockerKeysOperations
        jobs: JobsOperations
        locations: LocationsOperations
        operations: Operations

        def __init__(
                self, 
                credential: TokenCredential, 
                subscription_id: str, 
                accept_language: Optional[str] = None, 
                base_url: str = "https://management.azure.com", 
                *, 
                api_version: str = ..., 
                **kwargs: Any
            ) -> None: ...

        def close(self) -> None: ...


namespace azure.mgmt.storageimportexport.aio

    class azure.mgmt.storageimportexport.aio.StorageImportExport: implements AsyncContextManager 
        bit_locker_keys: BitLockerKeysOperations
        jobs: JobsOperations
        locations: LocationsOperations
        operations: Operations

        def __init__(
                self, 
                credential: AsyncTokenCredential, 
                subscription_id: str, 
                accept_language: Optional[str] = None, 
                base_url: str = "https://management.azure.com", 
                *, 
                api_version: str = ..., 
                **kwargs: Any
            ) -> None: ...

        async def close(self) -> None: ...


namespace azure.mgmt.storageimportexport.aio.operations

    class azure.mgmt.storageimportexport.aio.operations.BitLockerKeysOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                job_name: str, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[DriveBitLockerKey]: ...


    class azure.mgmt.storageimportexport.aio.operations.JobsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create(
                self, 
                job_name: str, 
                resource_group_name: str, 
                body: PutJobParameters, 
                client_tenant_id: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JobResponse: ...

        @overload
        async def create(
                self, 
                job_name: str, 
                resource_group_name: str, 
                body: IO, 
                client_tenant_id: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JobResponse: ...

        @distributed_trace_async
        async def delete(
                self, 
                job_name: str, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                job_name: str, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> JobResponse: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                top: Optional[int] = None, 
                filter: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[JobResponse]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                top: Optional[int] = None, 
                filter: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[JobResponse]: ...

        @overload
        async def update(
                self, 
                job_name: str, 
                resource_group_name: str, 
                body: UpdateJobParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JobResponse: ...

        @overload
        async def update(
                self, 
                job_name: str, 
                resource_group_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JobResponse: ...


    class azure.mgmt.storageimportexport.aio.operations.LocationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                location_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Location: ...

        @distributed_trace
        def list(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[Location]: ...


    class azure.mgmt.storageimportexport.aio.operations.Operations:

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


namespace azure.mgmt.storageimportexport.models

    class azure.mgmt.storageimportexport.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.storageimportexport.models.DeliveryPackageInformation(Model):
        carrier_name: str
        drive_count: int
        ship_date: str
        tracking_number: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                carrier_name: str, 
                drive_count: Optional[int] = ..., 
                ship_date: Optional[str] = ..., 
                tracking_number: str, 
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


    class azure.mgmt.storageimportexport.models.DriveBitLockerKey(Model):
        bit_locker_key: str
        drive_id: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                bit_locker_key: Optional[str] = ..., 
                drive_id: Optional[str] = ..., 
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


    class azure.mgmt.storageimportexport.models.DriveState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPLETED = "Completed"
        COMPLETED_MORE_INFO = "CompletedMoreInfo"
        NEVER_RECEIVED = "NeverReceived"
        RECEIVED = "Received"
        SHIPPED_BACK = "ShippedBack"
        SPECIFIED = "Specified"
        TRANSFERRING = "Transferring"


    class azure.mgmt.storageimportexport.models.DriveStatus(Model):
        bit_locker_key: str
        bytes_succeeded: int
        copy_status: str
        drive_header_hash: str
        drive_id: str
        error_log_uri: str
        manifest_file: str
        manifest_hash: str
        manifest_uri: str
        percent_complete: int
        state: Union[str, DriveState]
        verbose_log_uri: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                bit_locker_key: Optional[str] = ..., 
                bytes_succeeded: Optional[int] = ..., 
                copy_status: Optional[str] = ..., 
                drive_header_hash: Optional[str] = ..., 
                drive_id: Optional[str] = ..., 
                error_log_uri: Optional[str] = ..., 
                manifest_file: Optional[str] = ..., 
                manifest_hash: Optional[str] = ..., 
                manifest_uri: Optional[str] = ..., 
                percent_complete: Optional[int] = ..., 
                state: Union[str, DriveState] = "Specified", 
                verbose_log_uri: Optional[str] = ..., 
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


    class azure.mgmt.storageimportexport.models.EncryptionKekType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CUSTOMER_MANAGED = "CustomerManaged"
        MICROSOFT_MANAGED = "MicrosoftManaged"


    class azure.mgmt.storageimportexport.models.EncryptionKeyDetails(Model):
        kek_type: Union[str, EncryptionKekType]
        kek_url: str
        kek_vault_resource_id: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                kek_type: Union[str, EncryptionKekType] = "MicrosoftManaged", 
                kek_url: Optional[str] = ..., 
                kek_vault_resource_id: Optional[str] = ..., 
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


    class azure.mgmt.storageimportexport.models.ErrorResponse(Model):
        code: str
        details: list[ErrorResponseErrorDetailsItem]
        innererror: JSON
        message: str
        target: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                details: Optional[List[ErrorResponseErrorDetailsItem]] = ..., 
                innererror: Optional[JSON] = ..., 
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


    class azure.mgmt.storageimportexport.models.ErrorResponseErrorDetailsItem(Model):
        code: str
        message: str
        target: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
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


    class azure.mgmt.storageimportexport.models.Export(Model):
        blob_list_blob_path: str
        blob_path: list[str]
        blob_path_prefix: list[str]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                blob_list_blob_path: Optional[str] = ..., 
                blob_path: Optional[List[str]] = ..., 
                blob_path_prefix: Optional[List[str]] = ..., 
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


    class azure.mgmt.storageimportexport.models.GetBitLockerKeysResponse(Model):
        value: list[DriveBitLockerKey]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                value: Optional[List[DriveBitLockerKey]] = ..., 
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


    class azure.mgmt.storageimportexport.models.IdentityDetails(Model):
        principal_id: str
        tenant_id: str
        type: Union[str, IdentityType]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                type: Union[str, IdentityType] = None, 
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


    class azure.mgmt.storageimportexport.models.IdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.storageimportexport.models.JobDetails(Model):
        backup_drive_manifest: bool
        cancel_requested: bool
        delivery_package: DeliveryPackageInformation
        diagnostics_path: str
        drive_list: list[DriveStatus]
        encryption_key: EncryptionKeyDetails
        export: Export
        incomplete_blob_list_uri: str
        job_type: str
        log_level: str
        percent_complete: int
        provisioning_state: str
        return_address: ReturnAddress
        return_package: PackageInformation
        return_shipping: ReturnShipping
        shipping_information: ShippingInformation
        state: str
        storage_account_id: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                backup_drive_manifest: bool = False, 
                cancel_requested: bool = False, 
                delivery_package: Optional[DeliveryPackageInformation] = ..., 
                diagnostics_path: Optional[str] = ..., 
                drive_list: Optional[List[DriveStatus]] = ..., 
                encryption_key: Optional[EncryptionKeyDetails] = ..., 
                export: Optional[Export] = ..., 
                incomplete_blob_list_uri: Optional[str] = ..., 
                job_type: Optional[str] = ..., 
                log_level: Optional[str] = ..., 
                percent_complete: Optional[int] = ..., 
                provisioning_state: Optional[str] = ..., 
                return_address: Optional[ReturnAddress] = ..., 
                return_package: Optional[PackageInformation] = ..., 
                return_shipping: Optional[ReturnShipping] = ..., 
                shipping_information: Optional[ShippingInformation] = ..., 
                state: str = "Creating", 
                storage_account_id: Optional[str] = ..., 
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


    class azure.mgmt.storageimportexport.models.JobResponse(Model):
        id: str
        identity: IdentityDetails
        location: str
        name: str
        properties: JobDetails
        system_data: SystemData
        tags: JSON
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                identity: Optional[IdentityDetails] = ..., 
                location: Optional[str] = ..., 
                properties: Optional[JobDetails] = ..., 
                tags: Optional[JSON] = ..., 
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


    class azure.mgmt.storageimportexport.models.ListJobsResponse(Model):
        next_link: str
        value: list[JobResponse]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[JobResponse]] = ..., 
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


    class azure.mgmt.storageimportexport.models.ListOperationsResponse(Model):
        value: list[Operation]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                value: Optional[List[Operation]] = ..., 
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


    class azure.mgmt.storageimportexport.models.Location(Model):
        additional_shipping_information: str
        alternate_locations: list[str]
        city: str
        country_or_region: str
        id: str
        name: str
        phone: str
        postal_code: str
        recipient_name: str
        state_or_province: str
        street_address1: str
        street_address2: str
        supported_carriers: list[str]
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                additional_shipping_information: Optional[str] = ..., 
                alternate_locations: Optional[List[str]] = ..., 
                city: Optional[str] = ..., 
                country_or_region: Optional[str] = ..., 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                phone: Optional[str] = ..., 
                postal_code: Optional[str] = ..., 
                recipient_name: Optional[str] = ..., 
                state_or_province: Optional[str] = ..., 
                street_address1: Optional[str] = ..., 
                street_address2: Optional[str] = ..., 
                supported_carriers: Optional[List[str]] = ..., 
                type: Optional[str] = ..., 
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


    class azure.mgmt.storageimportexport.models.LocationsResponse(Model):
        value: list[Location]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                value: Optional[List[Location]] = ..., 
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


    class azure.mgmt.storageimportexport.models.Operation(Model):
        description: str
        name: str
        operation: str
        provider: str
        resource: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                name: str, 
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


    class azure.mgmt.storageimportexport.models.PackageInformation(Model):
        carrier_name: str
        drive_count: int
        ship_date: str
        tracking_number: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                carrier_name: str, 
                drive_count: int, 
                ship_date: str, 
                tracking_number: str, 
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


    class azure.mgmt.storageimportexport.models.PutJobParameters(Model):
        location: str
        properties: JobDetails
        tags: JSON

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                properties: Optional[JobDetails] = ..., 
                tags: Optional[JSON] = ..., 
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


    class azure.mgmt.storageimportexport.models.ReturnAddress(Model):
        city: str
        country_or_region: str
        email: str
        phone: str
        postal_code: str
        recipient_name: str
        state_or_province: str
        street_address1: str
        street_address2: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                city: str, 
                country_or_region: str, 
                email: str, 
                phone: str, 
                postal_code: str, 
                recipient_name: str, 
                state_or_province: Optional[str] = ..., 
                street_address1: str, 
                street_address2: Optional[str] = ..., 
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


    class azure.mgmt.storageimportexport.models.ReturnShipping(Model):
        carrier_account_number: str
        carrier_name: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                carrier_account_number: str, 
                carrier_name: str, 
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


    class azure.mgmt.storageimportexport.models.ShippingInformation(Model):
        additional_information: str
        city: str
        country_or_region: str
        phone: str
        postal_code: str
        recipient_name: str
        state_or_province: str
        street_address1: str
        street_address2: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                city: Optional[str] = ..., 
                country_or_region: Optional[str] = ..., 
                phone: Optional[str] = ..., 
                postal_code: Optional[str] = ..., 
                recipient_name: Optional[str] = ..., 
                state_or_province: Optional[str] = ..., 
                street_address1: Optional[str] = ..., 
                street_address2: Optional[str] = ..., 
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


    class azure.mgmt.storageimportexport.models.SystemData(Model):
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


    class azure.mgmt.storageimportexport.models.UpdateJobParameters(Model):
        backup_drive_manifest: bool
        cancel_requested: bool
        delivery_package: DeliveryPackageInformation
        drive_list: list[DriveStatus]
        log_level: str
        return_address: ReturnAddress
        return_shipping: ReturnShipping
        state: str
        tags: JSON

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                backup_drive_manifest: bool = False, 
                cancel_requested: bool = False, 
                delivery_package: Optional[DeliveryPackageInformation] = ..., 
                drive_list: Optional[List[DriveStatus]] = ..., 
                log_level: Optional[str] = ..., 
                return_address: Optional[ReturnAddress] = ..., 
                return_shipping: Optional[ReturnShipping] = ..., 
                state: Optional[str] = ..., 
                tags: Optional[JSON] = ..., 
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


namespace azure.mgmt.storageimportexport.operations

    class azure.mgmt.storageimportexport.operations.BitLockerKeysOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def list(
                self, 
                job_name: str, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[DriveBitLockerKey]: ...


    class azure.mgmt.storageimportexport.operations.JobsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def create(
                self, 
                job_name: str, 
                resource_group_name: str, 
                body: PutJobParameters, 
                client_tenant_id: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JobResponse: ...

        @overload
        def create(
                self, 
                job_name: str, 
                resource_group_name: str, 
                body: IO, 
                client_tenant_id: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JobResponse: ...

        @distributed_trace
        def delete(
                self, 
                job_name: str, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                job_name: str, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> JobResponse: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                top: Optional[int] = None, 
                filter: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[JobResponse]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                top: Optional[int] = None, 
                filter: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[JobResponse]: ...

        @overload
        def update(
                self, 
                job_name: str, 
                resource_group_name: str, 
                body: UpdateJobParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JobResponse: ...

        @overload
        def update(
                self, 
                job_name: str, 
                resource_group_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JobResponse: ...


    class azure.mgmt.storageimportexport.operations.LocationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get(
                self, 
                location_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Location: ...

        @distributed_trace
        def list(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[Location]: ...


    class azure.mgmt.storageimportexport.operations.Operations:

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


```