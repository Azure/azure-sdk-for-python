```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.azurestack

    class azure.mgmt.azurestack.AzureStackManagementClient: implements ContextManager 
        cloud_manifest_file: CloudManifestFileOperations
        customer_subscriptions: CustomerSubscriptionsOperations
        deployment_license: DeploymentLicenseOperations
        operations: Operations
        products: ProductsOperations
        registrations: RegistrationsOperations

        def __init__(
                self, 
                credential: TokenCredential, 
                subscription_id: str, 
                base_url: str = "https://management.azure.com", 
                *, 
                api_version: str = ..., 
                **kwargs: Any
            ) -> None: ...

        def close(self) -> None: ...


namespace azure.mgmt.azurestack.aio

    class azure.mgmt.azurestack.aio.AzureStackManagementClient: implements AsyncContextManager 
        cloud_manifest_file: CloudManifestFileOperations
        customer_subscriptions: CustomerSubscriptionsOperations
        deployment_license: DeploymentLicenseOperations
        operations: Operations
        products: ProductsOperations
        registrations: RegistrationsOperations

        def __init__(
                self, 
                credential: AsyncTokenCredential, 
                subscription_id: str, 
                base_url: str = "https://management.azure.com", 
                *, 
                api_version: str = ..., 
                **kwargs: Any
            ) -> None: ...

        async def close(self) -> None: ...


namespace azure.mgmt.azurestack.aio.operations

    class azure.mgmt.azurestack.aio.operations.CloudManifestFileOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                verification_version: str, 
                version_creation_date: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> CloudManifestFileResponse: ...

        @distributed_trace_async
        async def list(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> CloudManifestFileResponse: ...


    class azure.mgmt.azurestack.aio.operations.CustomerSubscriptionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create(
                self, 
                resource_group: str, 
                registration_name: str, 
                customer_subscription_name: str, 
                customer_creation_parameters: CustomerSubscription, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CustomerSubscription: ...

        @overload
        async def create(
                self, 
                resource_group: str, 
                registration_name: str, 
                customer_subscription_name: str, 
                customer_creation_parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CustomerSubscription: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group: str, 
                registration_name: str, 
                customer_subscription_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group: str, 
                registration_name: str, 
                customer_subscription_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> CustomerSubscription: ...

        @distributed_trace
        def list(
                self, 
                resource_group: str, 
                registration_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[CustomerSubscription]: ...


    class azure.mgmt.azurestack.aio.operations.DeploymentLicenseOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create(
                self, 
                deployment_license_request: DeploymentLicenseRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DeploymentLicenseResponse: ...

        @overload
        async def create(
                self, 
                deployment_license_request: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DeploymentLicenseResponse: ...


    class azure.mgmt.azurestack.aio.operations.Operations:

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


    class azure.mgmt.azurestack.aio.operations.ProductsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group: str, 
                registration_name: str, 
                product_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Product: ...

        @overload
        async def get_product(
                self, 
                resource_group: str, 
                registration_name: str, 
                product_name: str, 
                device_configuration: Optional[DeviceConfiguration] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Product: ...

        @overload
        async def get_product(
                self, 
                resource_group: str, 
                registration_name: str, 
                product_name: str, 
                device_configuration: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Product: ...

        @overload
        async def get_products(
                self, 
                resource_group: str, 
                registration_name: str, 
                product_name: str, 
                device_configuration: Optional[DeviceConfiguration] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ProductList: ...

        @overload
        async def get_products(
                self, 
                resource_group: str, 
                registration_name: str, 
                product_name: str, 
                device_configuration: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ProductList: ...

        @distributed_trace
        def list(
                self, 
                resource_group: str, 
                registration_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[Product]: ...

        @distributed_trace_async
        async def list_details(
                self, 
                resource_group: str, 
                registration_name: str, 
                product_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ExtendedProduct: ...

        @overload
        async def list_products(
                self, 
                resource_group: str, 
                registration_name: str, 
                product_name: str, 
                device_configuration: Optional[DeviceConfiguration] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ProductList: ...

        @overload
        async def list_products(
                self, 
                resource_group: str, 
                registration_name: str, 
                product_name: str, 
                device_configuration: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ProductList: ...

        @overload
        async def upload_log(
                self, 
                resource_group: str, 
                registration_name: str, 
                product_name: str, 
                marketplace_product_log_update: Optional[MarketplaceProductLogUpdate] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ProductLog: ...

        @overload
        async def upload_log(
                self, 
                resource_group: str, 
                registration_name: str, 
                product_name: str, 
                marketplace_product_log_update: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ProductLog: ...


    class azure.mgmt.azurestack.aio.operations.RegistrationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group: str, 
                registration_name: str, 
                token: RegistrationParameter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Registration: ...

        @overload
        async def create_or_update(
                self, 
                resource_group: str, 
                registration_name: str, 
                token: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Registration: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group: str, 
                registration_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def enable_remote_management(
                self, 
                resource_group: str, 
                registration_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group: str, 
                registration_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Registration: ...

        @distributed_trace_async
        async def get_activation_key(
                self, 
                resource_group: str, 
                registration_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ActivationKeyResult: ...

        @distributed_trace
        def list(
                self, 
                resource_group: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[Registration]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[Registration]: ...

        @overload
        async def update(
                self, 
                resource_group: str, 
                registration_name: str, 
                token: RegistrationParameter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Registration: ...

        @overload
        async def update(
                self, 
                resource_group: str, 
                registration_name: str, 
                token: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Registration: ...


namespace azure.mgmt.azurestack.models

    class azure.mgmt.azurestack.models.ActivationKeyResult(Model):
        activation_key: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                activation_key: Optional[str] = ..., 
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


    class azure.mgmt.azurestack.models.Category(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ADFS = "ADFS"
        AZURE_AD = "AzureAD"


    class azure.mgmt.azurestack.models.CloudManifestFileDeploymentData(Model):
        custom_cloud_arm_endpoint: str
        custom_cloud_verification_key: str
        external_dsms_certificates: str
        external_dsms_endpoint: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                custom_cloud_arm_endpoint: Optional[str] = ..., 
                custom_cloud_verification_key: Optional[str] = ..., 
                external_dsms_certificates: Optional[str] = ..., 
                external_dsms_endpoint: Optional[str] = ..., 
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


    class azure.mgmt.azurestack.models.CloudManifestFileProperties(Model):
        deployment_data: CloudManifestFileDeploymentData
        signature: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                deployment_data: Optional[CloudManifestFileDeploymentData] = ..., 
                signature: Optional[str] = ..., 
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


    class azure.mgmt.azurestack.models.CloudManifestFileResponse(Resource):
        etag: str
        id: str
        name: str
        properties: CloudManifestFileProperties
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                properties: Optional[CloudManifestFileProperties] = ..., 
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


    class azure.mgmt.azurestack.models.Compatibility(Model):
        description: str
        is_compatible: bool
        issues: Union[list[str, CompatibilityIssue]]
        message: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                is_compatible: Optional[bool] = ..., 
                issues: Optional[List[Union[str, CompatibilityIssue]]] = ..., 
                message: Optional[str] = ..., 
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


    class azure.mgmt.azurestack.models.CompatibilityIssue(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ADFS_IDENTITY_SYSTEM_REQUIRED = "ADFSIdentitySystemRequired"
        AZURE_AD_IDENTITY_SYSTEM_REQUIRED = "AzureADIdentitySystemRequired"
        CAPACITY_BILLING_MODEL_REQUIRED = "CapacityBillingModelRequired"
        CONNECTION_TO_AZURE_REQUIRED = "ConnectionToAzureRequired"
        CONNECTION_TO_INTERNET_REQUIRED = "ConnectionToInternetRequired"
        DEVELOPMENT_BILLING_MODEL_REQUIRED = "DevelopmentBillingModelRequired"
        DISCONNECTED_ENVIRONMENT_REQUIRED = "DisconnectedEnvironmentRequired"
        HIGHER_DEVICE_VERSION_REQUIRED = "HigherDeviceVersionRequired"
        LOWER_DEVICE_VERSION_REQUIRED = "LowerDeviceVersionRequired"
        PAY_AS_YOU_GO_BILLING_MODEL_REQUIRED = "PayAsYouGoBillingModelRequired"


    class azure.mgmt.azurestack.models.ComputeRole(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        IAA_S = "IaaS"
        NONE = "None"
        PAA_S = "PaaS"


    class azure.mgmt.azurestack.models.CustomerSubscription(Resource):
        etag: str
        id: str
        name: str
        tenant_id: str
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
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


    class azure.mgmt.azurestack.models.CustomerSubscriptionList(Model):
        next_link: str
        value: list[CustomerSubscription]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[CustomerSubscription]] = ..., 
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


    class azure.mgmt.azurestack.models.DataDiskImage(Model):
        lun: int
        source_blob_sas_uri: str

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


    class azure.mgmt.azurestack.models.DeploymentLicenseRequest(Model):
        verification_version: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                verification_version: Optional[str] = ..., 
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


    class azure.mgmt.azurestack.models.DeploymentLicenseResponse(Model):
        signature: str
        temporary_license_chain: list[str]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                signature: Optional[str] = ..., 
                temporary_license_chain: Optional[List[str]] = ..., 
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


    class azure.mgmt.azurestack.models.DeviceConfiguration(Model):
        device_version: str
        identity_system: Union[str, Category]

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


    class azure.mgmt.azurestack.models.Display(Model):
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


    class azure.mgmt.azurestack.models.ErrorDetails(Model):
        code: str
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


    class azure.mgmt.azurestack.models.ErrorResponse(Model):
        error: ErrorDetails

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetails] = ..., 
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


    class azure.mgmt.azurestack.models.ExtendedProduct(Model):
        compute_role: Union[str, ComputeRole]
        data_disk_images: list[DataDiskImage]
        gallery_package_blob_sas_uri: str
        is_system_extension: bool
        os_disk_image: OsDiskImage
        product_kind: str
        support_multiple_extensions: bool
        uri: str
        version: str
        version_properties_version: str
        vm_os_type: Union[str, OperatingSystem]
        vm_scale_set_enabled: bool

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


    class azure.mgmt.azurestack.models.ExtendedProductProperties(VirtualMachineExtensionProductProperties, VirtualMachineProductProperties):
        compute_role: Union[str, ComputeRole]
        data_disk_images: list[DataDiskImage]
        is_system_extension: bool
        os_disk_image: OsDiskImage
        support_multiple_extensions: bool
        uri: str
        version: str
        vm_os_type: Union[str, OperatingSystem]
        vm_scale_set_enabled: bool

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


    class azure.mgmt.azurestack.models.IconUris(Model):
        hero: str
        large: str
        medium: str
        small: str
        wide: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                hero: Optional[str] = ..., 
                large: Optional[str] = ..., 
                medium: Optional[str] = ..., 
                small: Optional[str] = ..., 
                wide: Optional[str] = ..., 
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


    class azure.mgmt.azurestack.models.Location(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        GLOBAL = "global"


    class azure.mgmt.azurestack.models.MarketplaceProductLogUpdate(Model):
        details: str
        error: str
        operation: str
        status: str

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


    class azure.mgmt.azurestack.models.OperatingSystem(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LINUX = "Linux"
        NONE = "None"
        WINDOWS = "Windows"


    class azure.mgmt.azurestack.models.Operation(Model):
        display: Display
        name: str
        origin: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                display: Optional[Display] = ..., 
                name: Optional[str] = ..., 
                origin: Optional[str] = ..., 
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


    class azure.mgmt.azurestack.models.OperationList(Model):
        next_link: str
        value: list[Operation]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
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


    class azure.mgmt.azurestack.models.OsDiskImage(Model):
        operating_system: Union[str, OperatingSystem]
        source_blob_sas_uri: str

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


    class azure.mgmt.azurestack.models.Product(Resource):
        billing_part_number: str
        compatibility: Compatibility
        description: str
        display_name: str
        etag: str
        gallery_item_identity: str
        icon_uris: IconUris
        id: str
        legal_terms: str
        links: list[ProductLink]
        name: str
        offer: str
        offer_version: str
        payload_length: int
        privacy_policy: str
        product_kind: str
        product_properties: ProductProperties
        publisher_display_name: str
        publisher_identifier: str
        sku: str
        type: str
        vm_extension_type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                billing_part_number: Optional[str] = ..., 
                compatibility: Optional[Compatibility] = ..., 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                etag: Optional[str] = ..., 
                gallery_item_identity: Optional[str] = ..., 
                icon_uris: Optional[IconUris] = ..., 
                legal_terms: Optional[str] = ..., 
                links: Optional[List[ProductLink]] = ..., 
                offer: Optional[str] = ..., 
                offer_version: Optional[str] = ..., 
                payload_length: Optional[int] = ..., 
                privacy_policy: Optional[str] = ..., 
                product_kind: Optional[str] = ..., 
                product_properties: Optional[ProductProperties] = ..., 
                publisher_display_name: Optional[str] = ..., 
                publisher_identifier: Optional[str] = ..., 
                sku: Optional[str] = ..., 
                vm_extension_type: Optional[str] = ..., 
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


    class azure.mgmt.azurestack.models.ProductLink(Model):
        display_name: str
        uri: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                display_name: Optional[str] = ..., 
                uri: Optional[str] = ..., 
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


    class azure.mgmt.azurestack.models.ProductList(Model):
        next_link: str
        value: list[Product]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[Product]] = ..., 
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


    class azure.mgmt.azurestack.models.ProductLog(Model):
        details: str
        end_date: str
        error: str
        id: str
        operation: str
        product_id: str
        registration_name: str
        resource_group_name: str
        start_date: str
        status: str
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


    class azure.mgmt.azurestack.models.ProductProperties(Model):
        version: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                version: Optional[str] = ..., 
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


    class azure.mgmt.azurestack.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CREATING = "Creating"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.azurestack.models.Registration(TrackedResource):
        billing_model: str
        cloud_id: str
        etag: str
        id: str
        location: Union[str, Location]
        name: str
        object_id: str
        tags: dict[str, str]
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                billing_model: Optional[str] = ..., 
                cloud_id: Optional[str] = ..., 
                etag: Optional[str] = ..., 
                location: Union[str, Location], 
                object_id: Optional[str] = ..., 
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


    class azure.mgmt.azurestack.models.RegistrationList(Model):
        next_link: str
        value: list[Registration]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[Registration]] = ..., 
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


    class azure.mgmt.azurestack.models.RegistrationParameter(Model):
        location: Union[str, Location]
        registration_token: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                location: Union[str, Location], 
                registration_token: str, 
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


    class azure.mgmt.azurestack.models.Resource(Model):
        etag: str
        id: str
        name: str
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
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


    class azure.mgmt.azurestack.models.TrackedResource(Model):
        etag: str
        id: str
        location: Union[str, Location]
        name: str
        tags: dict[str, str]
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                location: Union[str, Location], 
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


    class azure.mgmt.azurestack.models.VirtualMachineExtensionProductProperties(Model):
        compute_role: Union[str, ComputeRole]
        is_system_extension: bool
        support_multiple_extensions: bool
        uri: str
        version: str
        vm_os_type: Union[str, OperatingSystem]
        vm_scale_set_enabled: bool

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


    class azure.mgmt.azurestack.models.VirtualMachineProductProperties(Model):
        data_disk_images: list[DataDiskImage]
        os_disk_image: OsDiskImage
        version: str

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


namespace azure.mgmt.azurestack.operations

    class azure.mgmt.azurestack.operations.CloudManifestFileOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get(
                self, 
                verification_version: str, 
                version_creation_date: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> CloudManifestFileResponse: ...

        @distributed_trace
        def list(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> CloudManifestFileResponse: ...


    class azure.mgmt.azurestack.operations.CustomerSubscriptionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def create(
                self, 
                resource_group: str, 
                registration_name: str, 
                customer_subscription_name: str, 
                customer_creation_parameters: CustomerSubscription, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CustomerSubscription: ...

        @overload
        def create(
                self, 
                resource_group: str, 
                registration_name: str, 
                customer_subscription_name: str, 
                customer_creation_parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CustomerSubscription: ...

        @distributed_trace
        def delete(
                self, 
                resource_group: str, 
                registration_name: str, 
                customer_subscription_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group: str, 
                registration_name: str, 
                customer_subscription_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> CustomerSubscription: ...

        @distributed_trace
        def list(
                self, 
                resource_group: str, 
                registration_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[CustomerSubscription]: ...


    class azure.mgmt.azurestack.operations.DeploymentLicenseOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def create(
                self, 
                deployment_license_request: DeploymentLicenseRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DeploymentLicenseResponse: ...

        @overload
        def create(
                self, 
                deployment_license_request: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DeploymentLicenseResponse: ...


    class azure.mgmt.azurestack.operations.Operations:

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


    class azure.mgmt.azurestack.operations.ProductsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get(
                self, 
                resource_group: str, 
                registration_name: str, 
                product_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Product: ...

        @overload
        def get_product(
                self, 
                resource_group: str, 
                registration_name: str, 
                product_name: str, 
                device_configuration: Optional[DeviceConfiguration] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Product: ...

        @overload
        def get_product(
                self, 
                resource_group: str, 
                registration_name: str, 
                product_name: str, 
                device_configuration: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Product: ...

        @overload
        def get_products(
                self, 
                resource_group: str, 
                registration_name: str, 
                product_name: str, 
                device_configuration: Optional[DeviceConfiguration] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ProductList: ...

        @overload
        def get_products(
                self, 
                resource_group: str, 
                registration_name: str, 
                product_name: str, 
                device_configuration: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ProductList: ...

        @distributed_trace
        def list(
                self, 
                resource_group: str, 
                registration_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[Product]: ...

        @distributed_trace
        def list_details(
                self, 
                resource_group: str, 
                registration_name: str, 
                product_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ExtendedProduct: ...

        @overload
        def list_products(
                self, 
                resource_group: str, 
                registration_name: str, 
                product_name: str, 
                device_configuration: Optional[DeviceConfiguration] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ProductList: ...

        @overload
        def list_products(
                self, 
                resource_group: str, 
                registration_name: str, 
                product_name: str, 
                device_configuration: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ProductList: ...

        @overload
        def upload_log(
                self, 
                resource_group: str, 
                registration_name: str, 
                product_name: str, 
                marketplace_product_log_update: Optional[MarketplaceProductLogUpdate] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ProductLog: ...

        @overload
        def upload_log(
                self, 
                resource_group: str, 
                registration_name: str, 
                product_name: str, 
                marketplace_product_log_update: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ProductLog: ...


    class azure.mgmt.azurestack.operations.RegistrationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def create_or_update(
                self, 
                resource_group: str, 
                registration_name: str, 
                token: RegistrationParameter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Registration: ...

        @overload
        def create_or_update(
                self, 
                resource_group: str, 
                registration_name: str, 
                token: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Registration: ...

        @distributed_trace
        def delete(
                self, 
                resource_group: str, 
                registration_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def enable_remote_management(
                self, 
                resource_group: str, 
                registration_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group: str, 
                registration_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Registration: ...

        @distributed_trace
        def get_activation_key(
                self, 
                resource_group: str, 
                registration_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ActivationKeyResult: ...

        @distributed_trace
        def list(
                self, 
                resource_group: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[Registration]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[Registration]: ...

        @overload
        def update(
                self, 
                resource_group: str, 
                registration_name: str, 
                token: RegistrationParameter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Registration: ...

        @overload
        def update(
                self, 
                resource_group: str, 
                registration_name: str, 
                token: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Registration: ...


```