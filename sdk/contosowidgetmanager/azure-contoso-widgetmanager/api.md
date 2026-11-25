```py
namespace azure.contoso.widgetmanager

    class azure.contoso.widgetmanager.WidgetManagerClient: implements ContextManager 
        widgets: WidgetsOperations

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


namespace azure.contoso.widgetmanager.aio

    class azure.contoso.widgetmanager.aio.WidgetManagerClient: implements AsyncContextManager 
        widgets: WidgetsOperations

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


namespace azure.contoso.widgetmanager.aio.operations

    class azure.contoso.widgetmanager.aio.operations.WidgetsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update_widget(
                self, 
                widget_name: str, 
                resource: WidgetSuite, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> AsyncLROPoller[WidgetSuite]: ...

        @overload
        async def begin_create_or_update_widget(
                self, 
                widget_name: str, 
                resource: WidgetSuite, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> AsyncLROPoller[WidgetSuite]: ...

        @overload
        async def begin_create_or_update_widget(
                self, 
                widget_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> AsyncLROPoller[WidgetSuite]: ...

        @distributed_trace_async
        async def begin_delete_widget(
                self, 
                widget_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[WidgetSuite]: ...

        @distributed_trace_async
        async def get_widget(
                self, 
                widget_name: str, 
                **kwargs: Any
            ) -> WidgetSuite: ...

        @distributed_trace_async
        async def get_widget_operation_status(
                self, 
                widget_name: str, 
                operation_id: str, 
                **kwargs: Any
            ) -> ResourceOperationStatusWidgetSuiteWidgetSuiteError: ...

        @distributed_trace
        def list_widgets(self, **kwargs: Any) -> AsyncItemPaged[WidgetSuite]: ...


namespace azure.contoso.widgetmanager.models

    class azure.contoso.widgetmanager.models.FakedSharedModel(_Model):
        created_at: datetime
        tag: str

        @overload
        def __init__(
                self, 
                *, 
                created_at: datetime, 
                tag: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.contoso.widgetmanager.models.OperationState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        FAILED = "Failed"
        NOT_STARTED = "NotStarted"
        RUNNING = "Running"
        SUCCEEDED = "Succeeded"


    class azure.contoso.widgetmanager.models.ResourceOperationStatusWidgetSuiteWidgetSuiteError(_Model):
        error: Optional[ODataV4Format]
        id: str
        result: Optional[WidgetSuite]
        status: Union[str, OperationState]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ODataV4Format] = ..., 
                id: str, 
                result: Optional[WidgetSuite] = ..., 
                status: Union[str, OperationState]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.contoso.widgetmanager.models.WidgetSuite(_Model):
        manufacturer_id: str
        name: str
        shared_model: Optional[FakedSharedModel]

        @overload
        def __init__(
                self, 
                *, 
                manufacturer_id: str, 
                shared_model: Optional[FakedSharedModel] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


namespace azure.contoso.widgetmanager.operations

    class azure.contoso.widgetmanager.operations.WidgetsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update_widget(
                self, 
                widget_name: str, 
                resource: WidgetSuite, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> LROPoller[WidgetSuite]: ...

        @overload
        def begin_create_or_update_widget(
                self, 
                widget_name: str, 
                resource: WidgetSuite, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> LROPoller[WidgetSuite]: ...

        @overload
        def begin_create_or_update_widget(
                self, 
                widget_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> LROPoller[WidgetSuite]: ...

        @distributed_trace
        def begin_delete_widget(
                self, 
                widget_name: str, 
                **kwargs: Any
            ) -> LROPoller[WidgetSuite]: ...

        @distributed_trace
        def get_widget(
                self, 
                widget_name: str, 
                **kwargs: Any
            ) -> WidgetSuite: ...

        @distributed_trace
        def get_widget_operation_status(
                self, 
                widget_name: str, 
                operation_id: str, 
                **kwargs: Any
            ) -> ResourceOperationStatusWidgetSuiteWidgetSuiteError: ...

        @distributed_trace
        def list_widgets(self, **kwargs: Any) -> ItemPaged[WidgetSuite]: ...


namespace azure.contoso.widgetmanager.types

    class azure.contoso.widgetmanager.types.FakedSharedModel(TypedDict, total=False):
        key "createdAt": Required[str]
        key "tag": Required[str]
        createdAt: str
        tag: str


    class azure.contoso.widgetmanager.types.WidgetSuite(TypedDict, total=False):
        key "manufacturerId": Required[str]
        key "name": Required[str]
        key "sharedModel": ForwardRef('FakedSharedModel', module='types')
        manufacturerId: str
        name: str
        sharedModel: FakedSharedModel


```