```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.managementpartner

    class azure.mgmt.managementpartner.ACEProvisioningManagementPartnerAPI: implements ContextManager 
        operation: OperationOperations
        partner: PartnerOperations
        partners: PartnersOperations

        def __init__(
                self, 
                credential: TokenCredential, 
                base_url: str = "https://management.azure.com", 
                *, 
                api_version: str = ..., 
                **kwargs: Any
            ) -> None: ...

        def close(self) -> None: ...


namespace azure.mgmt.managementpartner.aio

    class azure.mgmt.managementpartner.aio.ACEProvisioningManagementPartnerAPI: implements AsyncContextManager 
        operation: OperationOperations
        partner: PartnerOperations
        partners: PartnersOperations

        def __init__(
                self, 
                credential: AsyncTokenCredential, 
                base_url: str = "https://management.azure.com", 
                *, 
                api_version: str = ..., 
                **kwargs: Any
            ) -> None: ...

        async def close(self) -> None: ...


namespace azure.mgmt.managementpartner.aio.operations

    class azure.mgmt.managementpartner.aio.operations.OperationOperations:

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
            ) -> AsyncIterable[OperationResponse]: ...


    class azure.mgmt.managementpartner.aio.operations.PartnerOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def create(
                self, 
                partner_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> PartnerResponse: ...

        @distributed_trace_async
        async def delete(
                self, 
                partner_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                partner_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> PartnerResponse: ...

        @distributed_trace_async
        async def update(
                self, 
                partner_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> PartnerResponse: ...


    class azure.mgmt.managementpartner.aio.operations.PartnersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> PartnerResponse: ...


namespace azure.mgmt.managementpartner.models

    class azure.mgmt.managementpartner.models.Error(Model):
        code: str
        error: ExtendedErrorInfo
        message: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                error: Optional[ExtendedErrorInfo] = ..., 
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


    class azure.mgmt.managementpartner.models.ExtendedErrorInfo(Model):
        code: str
        message: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
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


    class azure.mgmt.managementpartner.models.ManagementPartnerState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        DELETED = "Deleted"


    class azure.mgmt.managementpartner.models.OperationDisplay(Model):
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


    class azure.mgmt.managementpartner.models.OperationList(Model):
        next_link: str
        value: list[OperationResponse]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[OperationResponse]] = ..., 
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


    class azure.mgmt.managementpartner.models.OperationResponse(Model):
        display: OperationDisplay
        name: str
        origin: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                display: Optional[OperationDisplay] = ..., 
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


    class azure.mgmt.managementpartner.models.PartnerResponse(Model):
        created_time: datetime
        etag: int
        id: str
        name: str
        object_id: str
        partner_id: str
        partner_name: str
        state: Union[str, ManagementPartnerState]
        tenant_id: str
        type: str
        updated_time: datetime
        version: int

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                created_time: Optional[datetime] = ..., 
                etag: Optional[int] = ..., 
                object_id: Optional[str] = ..., 
                partner_id: Optional[str] = ..., 
                partner_name: Optional[str] = ..., 
                state: Optional[Union[str, ManagementPartnerState]] = ..., 
                tenant_id: Optional[str] = ..., 
                updated_time: Optional[datetime] = ..., 
                version: Optional[int] = ..., 
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


namespace azure.mgmt.managementpartner.operations

    class azure.mgmt.managementpartner.operations.OperationOperations:

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
            ) -> Iterable[OperationResponse]: ...


    class azure.mgmt.managementpartner.operations.PartnerOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def create(
                self, 
                partner_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> PartnerResponse: ...

        @distributed_trace
        def delete(
                self, 
                partner_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                partner_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> PartnerResponse: ...

        @distributed_trace
        def update(
                self, 
                partner_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> PartnerResponse: ...


    class azure.mgmt.managementpartner.operations.PartnersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> PartnerResponse: ...


```