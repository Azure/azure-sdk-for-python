```py
namespace azure.iot.deviceregistrysoftwareupdate

    class azure.iot.deviceregistrysoftwareupdate.DeviceRegistrySoftwareUpdateClient: implements ContextManager 
        device_classes: DeviceClassesOperations
        software_update: SoftwareUpdateOperations

        def __init__(
                self, 
                endpoint: str, 
                credential: TokenCredential, 
                *, 
                api_version: str = ..., 
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


namespace azure.iot.deviceregistrysoftwareupdate.aio

    class azure.iot.deviceregistrysoftwareupdate.aio.DeviceRegistrySoftwareUpdateClient: implements AsyncContextManager 
        device_classes: DeviceClassesOperations
        software_update: SoftwareUpdateOperations

        def __init__(
                self, 
                endpoint: str, 
                credential: AsyncTokenCredential, 
                *, 
                api_version: str = ..., 
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


namespace azure.iot.deviceregistrysoftwareupdate.aio.operations

    class azure.iot.deviceregistrysoftwareupdate.aio.operations.DeviceClassesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def delete(
                self, 
                device_class_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get_device_class(
                self, 
                device_class_id: str, 
                **kwargs: Any
            ) -> DeviceClass: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[DeviceClass]: ...


    class azure.iot.deviceregistrysoftwareupdate.aio.operations.SoftwareUpdateOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_delete_update(
                self, 
                provider: str, 
                name: str, 
                version: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_import_update(
                self, 
                import_update_request: ImportUpdateRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_import_update(
                self, 
                import_update_request: ImportUpdateRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_import_update(
                self, 
                import_update_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get_file(
                self, 
                provider: str, 
                name: str, 
                version: str, 
                file_id: str, 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> UpdateFile: ...

        @distributed_trace_async
        async def get_operation_status(
                self, 
                operation_id: str, 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> UpdateOperation: ...

        @distributed_trace_async
        async def get_update(
                self, 
                provider: str, 
                name: str, 
                version: str, 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> Update: ...

        @distributed_trace
        def list_files(
                self, 
                provider: str, 
                name: str, 
                version: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[str]: ...

        @distributed_trace
        def list_names(
                self, 
                provider: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[str]: ...

        @distributed_trace
        def list_operation_statuses(
                self, 
                *, 
                filter: Optional[str] = ..., 
                max_page_size: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[UpdateOperation]: ...

        @distributed_trace
        def list_providers(self, **kwargs: Any) -> AsyncItemPaged[str]: ...

        @distributed_trace
        def list_updates(
                self, 
                *, 
                filter: Optional[str] = ..., 
                search: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Update]: ...

        @distributed_trace
        def list_versions(
                self, 
                provider: str, 
                name: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[str]: ...


namespace azure.iot.deviceregistrysoftwareupdate.models

    class azure.iot.deviceregistrysoftwareupdate.models.BestCompatibleUpdate(_Model):
        update_id: UpdateId

        @overload
        def __init__(
                self, 
                *, 
                update_id: UpdateId
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.iot.deviceregistrysoftwareupdate.models.Compatibility(_Model):


    class azure.iot.deviceregistrysoftwareupdate.models.DeviceClass(_Model):
        best_compatible_update: Optional[BestCompatibleUpdate]
        device_class_id: str
        device_class_properties: DeviceClassProperties


    class azure.iot.deviceregistrysoftwareupdate.models.DeviceClassProperties(_Model):
        agent_profile: int
        compat_properties: dict[str, str]

        @overload
        def __init__(
                self, 
                *, 
                agent_profile: int, 
                compat_properties: dict[str, str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.iot.deviceregistrysoftwareupdate.models.FileImportMetadata(_Model):
        file_name: str
        url: str

        @overload
        def __init__(
                self, 
                *, 
                file_name: str, 
                url: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.iot.deviceregistrysoftwareupdate.models.ImportManifestMetadata(_Model):
        hashes: dict[str, str]
        size_in_bytes: int
        url: str

        @overload
        def __init__(
                self, 
                *, 
                hashes: dict[str, str], 
                size_in_bytes: int, 
                url: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.iot.deviceregistrysoftwareupdate.models.ImportUpdateInputItem(_Model):
        files: Optional[list[FileImportMetadata]]
        friendly_name: Optional[str]
        import_manifest: ImportManifestMetadata

        @overload
        def __init__(
                self, 
                *, 
                files: Optional[list[FileImportMetadata]] = ..., 
                friendly_name: Optional[str] = ..., 
                import_manifest: ImportManifestMetadata
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.iot.deviceregistrysoftwareupdate.models.ImportUpdateRequest(_Model):
        enable_scan: Optional[bool]
        import_update_input: list[ImportUpdateInputItem]

        @overload
        def __init__(
                self, 
                *, 
                enable_scan: Optional[bool] = ..., 
                import_update_input: list[ImportUpdateInputItem]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.iot.deviceregistrysoftwareupdate.models.Instructions(_Model):
        steps: list[Step]

        @overload
        def __init__(
                self, 
                *, 
                steps: list[Step]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.iot.deviceregistrysoftwareupdate.models.OperationState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        FAILED = "Failed"
        NOT_STARTED = "NotStarted"
        RUNNING = "Running"
        SUCCEEDED = "Succeeded"


    class azure.iot.deviceregistrysoftwareupdate.models.Step(_Model):
        description: Optional[str]
        file_names: Optional[list[str]]
        handler: Optional[str]
        handler_properties: Optional[dict[str, Any]]
        type: Optional[Union[str, StepType]]
        update_id: Optional[UpdateId]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                file_names: Optional[list[str]] = ..., 
                handler: Optional[str] = ..., 
                handler_properties: Optional[dict[str, Any]] = ..., 
                type: Optional[Union[str, StepType]] = ..., 
                update_id: Optional[UpdateId] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.iot.deviceregistrysoftwareupdate.models.StepType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INLINE = "inline"
        REFERENCE = "reference"


    class azure.iot.deviceregistrysoftwareupdate.models.Update(_Model):
        compatibility: list[Compatibility]
        created_date_time: datetime
        description: Optional[str]
        etag: Optional[str]
        friendly_name: Optional[str]
        imported_date_time: datetime
        installed_criteria: Optional[str]
        instructions: Optional[Instructions]
        is_deployable: Optional[bool]
        manifest_version: str
        referenced_by: Optional[list[UpdateId]]
        scan_result: Optional[str]
        update_id: UpdateId
        update_type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                compatibility: list[Compatibility], 
                created_date_time: datetime, 
                description: Optional[str] = ..., 
                etag: Optional[str] = ..., 
                friendly_name: Optional[str] = ..., 
                imported_date_time: datetime, 
                installed_criteria: Optional[str] = ..., 
                instructions: Optional[Instructions] = ..., 
                is_deployable: Optional[bool] = ..., 
                manifest_version: str, 
                referenced_by: Optional[list[UpdateId]] = ..., 
                scan_result: Optional[str] = ..., 
                update_id: UpdateId, 
                update_type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.iot.deviceregistrysoftwareupdate.models.UpdateFile(UpdateFileBase):
        download_handler: Optional[UpdateFileDownloadHandler]
        etag: Optional[str]
        file_id: str
        file_name: str
        hashes: dict[str, str]
        mime_type: str
        properties: dict[str, str]
        related_files: Optional[list[UpdateFileBase]]
        scan_details: str
        scan_result: str
        size_in_bytes: int

        @overload
        def __init__(
                self, 
                *, 
                download_handler: Optional[UpdateFileDownloadHandler] = ..., 
                etag: Optional[str] = ..., 
                file_id: str, 
                file_name: str, 
                hashes: dict[str, str], 
                mime_type: Optional[str] = ..., 
                properties: Optional[dict[str, str]] = ..., 
                related_files: Optional[list[UpdateFileBase]] = ..., 
                scan_details: Optional[str] = ..., 
                scan_result: Optional[str] = ..., 
                size_in_bytes: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.iot.deviceregistrysoftwareupdate.models.UpdateFileBase(_Model):
        file_name: str
        hashes: dict[str, str]
        mime_type: Optional[str]
        properties: Optional[dict[str, str]]
        scan_details: Optional[str]
        scan_result: Optional[str]
        size_in_bytes: int

        @overload
        def __init__(
                self, 
                *, 
                file_name: str, 
                hashes: dict[str, str], 
                mime_type: Optional[str] = ..., 
                properties: Optional[dict[str, str]] = ..., 
                scan_details: Optional[str] = ..., 
                scan_result: Optional[str] = ..., 
                size_in_bytes: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.iot.deviceregistrysoftwareupdate.models.UpdateFileDownloadHandler(_Model):
        id: str

        @overload
        def __init__(
                self, 
                *, 
                id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.iot.deviceregistrysoftwareupdate.models.UpdateId(_Model):
        name: str
        provider: str
        version: str

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                provider: str, 
                version: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.iot.deviceregistrysoftwareupdate.models.UpdateInfo(_Model):
        description: Optional[str]
        friendly_name: Optional[str]
        update_id: UpdateId

        @overload
        def __init__(
                self, 
                *, 
                update_id: UpdateId
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.iot.deviceregistrysoftwareupdate.models.UpdateOperation(_Model):
        created_date_time: datetime
        error: Optional[ODataV4Format]
        etag: Optional[str]
        last_action_date_time: datetime
        operation_id: str
        resource_location: Optional[str]
        status: Union[str, OperationState]
        trace_id: Optional[str]
        update_property: Optional[UpdateInfo]

        @overload
        def __init__(
                self, 
                *, 
                created_date_time: datetime, 
                error: Optional[ODataV4Format] = ..., 
                etag: Optional[str] = ..., 
                last_action_date_time: datetime, 
                operation_id: str, 
                resource_location: Optional[str] = ..., 
                status: Union[str, OperationState], 
                trace_id: Optional[str] = ..., 
                update_property: Optional[UpdateInfo] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


namespace azure.iot.deviceregistrysoftwareupdate.operations

    class azure.iot.deviceregistrysoftwareupdate.operations.DeviceClassesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def delete(
                self, 
                device_class_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get_device_class(
                self, 
                device_class_id: str, 
                **kwargs: Any
            ) -> DeviceClass: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[DeviceClass]: ...


    class azure.iot.deviceregistrysoftwareupdate.operations.SoftwareUpdateOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_delete_update(
                self, 
                provider: str, 
                name: str, 
                version: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_import_update(
                self, 
                import_update_request: ImportUpdateRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_import_update(
                self, 
                import_update_request: ImportUpdateRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_import_update(
                self, 
                import_update_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get_file(
                self, 
                provider: str, 
                name: str, 
                version: str, 
                file_id: str, 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> UpdateFile: ...

        @distributed_trace
        def get_operation_status(
                self, 
                operation_id: str, 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> UpdateOperation: ...

        @distributed_trace
        def get_update(
                self, 
                provider: str, 
                name: str, 
                version: str, 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> Update: ...

        @distributed_trace
        def list_files(
                self, 
                provider: str, 
                name: str, 
                version: str, 
                **kwargs: Any
            ) -> ItemPaged[str]: ...

        @distributed_trace
        def list_names(
                self, 
                provider: str, 
                **kwargs: Any
            ) -> ItemPaged[str]: ...

        @distributed_trace
        def list_operation_statuses(
                self, 
                *, 
                filter: Optional[str] = ..., 
                max_page_size: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[UpdateOperation]: ...

        @distributed_trace
        def list_providers(self, **kwargs: Any) -> ItemPaged[str]: ...

        @distributed_trace
        def list_updates(
                self, 
                *, 
                filter: Optional[str] = ..., 
                search: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Update]: ...

        @distributed_trace
        def list_versions(
                self, 
                provider: str, 
                name: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[str]: ...


namespace azure.iot.deviceregistrysoftwareupdate.types

    class azure.iot.deviceregistrysoftwareupdate.types.FileImportMetadata(TypedDict, total=False):
        key "fileName": Required[str]
        key "url": Required[str]
        fileName: str
        url: str


    class azure.iot.deviceregistrysoftwareupdate.types.ImportManifestMetadata(TypedDict, total=False):
        key "hashes": Required[dict[str, str]]
        key "sizeInBytes": Required[int]
        key "url": Required[str]
        hashes: dict[str, str]
        sizeInBytes: int
        url: str


    class azure.iot.deviceregistrysoftwareupdate.types.ImportUpdateInputItem(TypedDict, total=False):
        key "friendlyName": str
        key "importManifest": Required[ImportManifestMetadata]
        files: list[FileImportMetadata]
        friendlyName: str
        importManifest: ImportManifestMetadata


    class azure.iot.deviceregistrysoftwareupdate.types.ImportUpdateRequest(TypedDict, total=False):
        key "enableScan": bool
        key "importUpdateInput": Required[list[ImportUpdateInputItem]]
        enableScan: bool
        importUpdateInput: list[ImportUpdateInputItem]


```