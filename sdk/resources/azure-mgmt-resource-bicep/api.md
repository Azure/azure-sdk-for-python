```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.resource.bicep

    class azure.mgmt.resource.bicep.BicepMgmtClient: implements ContextManager 
        decompile_operation_group: DecompileOperationGroupOperations

        def __init__(
                self, 
                credential: TokenCredential, 
                subscription_id: str, 
                base_url: Optional[str] = None, 
                *, 
                api_version: str = ..., 
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


namespace azure.mgmt.resource.bicep.aio

    class azure.mgmt.resource.bicep.aio.BicepMgmtClient: implements AsyncContextManager 
        decompile_operation_group: DecompileOperationGroupOperations

        def __init__(
                self, 
                credential: AsyncTokenCredential, 
                subscription_id: str, 
                base_url: Optional[str] = None, 
                *, 
                api_version: str = ..., 
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


namespace azure.mgmt.resource.bicep.aio.operations

    class azure.mgmt.resource.bicep.aio.operations.DecompileOperationGroupOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def bicep(
                self, 
                decompile_operation_request: DecompileOperationRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DecompileOperationSuccessResponse: ...

        @overload
        async def bicep(
                self, 
                decompile_operation_request: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DecompileOperationSuccessResponse: ...

        @overload
        async def bicep(
                self, 
                decompile_operation_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DecompileOperationSuccessResponse: ...


namespace azure.mgmt.resource.bicep.models

    class azure.mgmt.resource.bicep.models.DecompileOperationRequest(_Model):
        template: str

        @overload
        def __init__(
                self, 
                *, 
                template: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.bicep.models.DecompileOperationSuccessResponse(_Model):
        entry_point: str
        files: List[FileDefinition]

        @overload
        def __init__(
                self, 
                *, 
                entry_point: str, 
                files: List[FileDefinition]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.bicep.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.resource.bicep.models.ErrorDetail(_Model):
        additional_info: Optional[List[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[List[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.resource.bicep.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.bicep.models.FileDefinition(_Model):
        contents: Optional[str]
        path: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                contents: Optional[str] = ..., 
                path: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


namespace azure.mgmt.resource.bicep.operations

    class azure.mgmt.resource.bicep.operations.DecompileOperationGroupOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def bicep(
                self, 
                decompile_operation_request: DecompileOperationRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DecompileOperationSuccessResponse: ...

        @overload
        def bicep(
                self, 
                decompile_operation_request: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DecompileOperationSuccessResponse: ...

        @overload
        def bicep(
                self, 
                decompile_operation_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DecompileOperationSuccessResponse: ...


```