```py
namespace azure.iot.deviceupdate

    class azure.iot.deviceupdate.DeviceUpdateClient: implements ContextManager 
        device_management: DeviceManagementOperations
        device_update: DeviceUpdateOperations

        def __init__(
                self,
                endpoint: str,
                instance_id: str,
                credential: 'TokenCredential',
                **kwargs: Any
            ) -> None: ...

        def send_request(
                self,
                request: HttpRequest,
                **kwargs: Any
            ) -> HttpResponse: ...

        def close(
                self
            ) -> None: ...

namespace azure.iot.deviceupdate.aio

    class azure.iot.deviceupdate.aio.DeviceUpdateClient: implements AsyncContextManager 
        device_management: DeviceManagementOperations
        device_update: DeviceUpdateOperations

        def __init__(
                self,
                endpoint: str,
                instance_id: str,
                credential: 'AsyncTokenCredential',
                **kwargs: Any
            ) -> None: ...

        def send_request(
                self,
                request: HttpRequest,
                **kwargs: Any
            ) -> Awaitable[AsyncHttpResponse]: ...

        async def close(
                self
            ) -> None: ...

namespace azure.iot.deviceupdate.aio.operations

    class azure.iot.deviceupdate.aio.operations.DeviceManagementOperations:

        def __init__(
                self,
                *args,
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_device_classes(
                self,
                **kwargs: Any
            ) -> AsyncIterable[JSON]: ...

        @distributed_trace_async
        async def get_device_class(
                self,
                device_class_id: str,
                **kwargs: Any
            ) -> JSON: ...

        @overload
        async def update_device_class(
                self,
                device_class_id: str,
                device_class_patch: JSON,
                *,
                content_type: str = 'application/merge-patch+json',
                **kwargs: Any
            ) -> JSON: ...

        @overload
        async def update_device_class(
                self,
                device_class_id: str,
                device_class_patch: IO,
                *,
                content_type: str = 'application/merge-patch+json',
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace_async
        async def delete_device_class(
                self,
                device_class_id: str,
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def list_installable_updates_for_device_class(
                self,
                device_class_id: str,
                **kwargs: Any
            ) -> AsyncIterable[JSON]: ...

        @distributed_trace
        def list_devices(
                self,
                *,
                filter: Optional[str] = ...,
                **kwargs: Any
            ) -> AsyncIterable[JSON]: ...

        @distributed_trace_async
        async def begin_import_devices(
                self,
                import_type: str,
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get_device(
                self,
                device_id: str,
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace_async
        async def get_device_module(
                self,
                device_id: str,
                module_id: str,
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace_async
        async def get_update_compliance(
                self,
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace
        def list_groups(
                self,
                *,
                orderby: Optional[str] = ...,
                **kwargs: Any
            ) -> AsyncIterable[JSON]: ...

        @distributed_trace_async
        async def get_group(
                self,
                group_id: str,
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace_async
        async def delete_group(
                self,
                group_id: str,
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get_group_update_compliance(
                self,
                group_id: str,
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace
        def list_best_updates_for_group(
                self,
                group_id: str,
                *,
                filter: Optional[str] = ...,
                **kwargs: Any
            ) -> AsyncIterable[JSON]: ...

        @distributed_trace
        def list_deployments_for_group(
                self,
                group_id: str,
                *,
                orderby: Optional[str] = ...,
                **kwargs: Any
            ) -> AsyncIterable[JSON]: ...

        @distributed_trace_async
        async def get_deployment(
                self,
                group_id: str,
                deployment_id: str,
                **kwargs: Any
            ) -> JSON: ...

        @overload
        async def create_or_update_deployment(
                self,
                group_id: str,
                deployment_id: str,
                deployment: JSON,
                *,
                content_type: str = 'application/json',
                **kwargs: Any
            ) -> JSON: ...

        @overload
        async def create_or_update_deployment(
                self,
                group_id: str,
                deployment_id: str,
                deployment: IO,
                *,
                content_type: str = 'application/json',
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace_async
        async def delete_deployment(
                self,
                group_id: str,
                deployment_id: str,
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get_deployment_status(
                self,
                group_id: str,
                deployment_id: str,
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace_async
        async def list_device_class_subgroups_for_group(
                self,
                group_id: str,
                *,
                filter: Optional[str] = ...,
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace_async
        async def get_device_class_subgroup_details(
                self,
                group_id: str,
                device_class_id: str,
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace_async
        async def delete_device_class_subgroup(
                self,
                group_id: str,
                device_class_id: str,
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get_device_class_subgroup_update_compliance(
                self,
                group_id: str,
                device_class_id: str,
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace_async
        async def list_best_updates_for_device_class_subgroup(
                self,
                group_id: str,
                device_class_id: str,
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace
        def list_deployments_for_device_class_subgroup(
                self,
                group_id: str,
                device_class_id: str,
                *,
                orderby: Optional[str] = ...,
                **kwargs: Any
            ) -> AsyncIterable[JSON]: ...

        @distributed_trace_async
        async def get_deployment_for_device_class_subgroup(
                self,
                group_id: str,
                device_class_id: str,
                deployment_id: str,
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace_async
        async def delete_device_class_subgroup_deployment(
                self,
                group_id: str,
                device_class_id: str,
                deployment_id: str,
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def stop_deployment(
                self,
                group_id: str,
                device_class_id: str,
                deployment_id: str,
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace_async
        async def retry_deployment(
                self,
                group_id: str,
                device_class_id: str,
                deployment_id: str,
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace_async
        async def get_device_class_subgroup_deployment_status(
                self,
                group_id: str,
                device_class_id: str,
                deployment_id: str,
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace
        def list_devices_for_device_class_subgroup_deployment(
                self,
                group_id: str,
                device_class_id: str,
                deployment_id: str,
                *,
                filter: Optional[str] = ...,
                **kwargs: Any
            ) -> AsyncIterable[JSON]: ...

        @distributed_trace_async
        async def get_operation(
                self,
                operation_id: str,
                *,
                if_none_match: Optional[str] = ...,
                **kwargs: Any
            ) -> Optional[JSON]: ...

        @distributed_trace
        def list_operations(
                self,
                *,
                filter: Optional[str] = ...,
                top: Optional[int] = ...,
                **kwargs: Any
            ) -> AsyncIterable[JSON]: ...

        @overload
        async def collect_logs(
                self,
                operation_id: str,
                log_collection_request: JSON,
                *,
                content_type: str = 'application/json',
                **kwargs: Any
            ) -> JSON: ...

        @overload
        async def collect_logs(
                self,
                operation_id: str,
                log_collection_request: IO,
                *,
                content_type: str = 'application/json',
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace_async
        async def get_log_collection_operation(
                self,
                operation_id: str,
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace
        def list_log_collection_operations(
                self,
                **kwargs: Any
            ) -> AsyncIterable[JSON]: ...

        @distributed_trace_async
        async def get_log_collection_operation_detailed_status(
                self,
                operation_id: str,
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace_async
        async def list_device_health(
                self,
                *,
                filter: str,
                **kwargs: Any
            ) -> JSON: ...


    class azure.iot.deviceupdate.aio.operations.DeviceUpdateOperations:

        def __init__(
                self,
                *args,
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_updates(
                self,
                *,
                search: Optional[str] = ...,
                filter: Optional[str] = ...,
                **kwargs: Any
            ) -> AsyncIterable[JSON]: ...

        @overload
        async def begin_import_update(
                self,
                update_to_import: list[JSON],
                *,
                content_type: str = 'application/json',
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_import_update(
                self,
                update_to_import: IO,
                *,
                content_type: str = 'application/json',
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get_update(
                self,
                provider: str,
                name: str,
                version: str,
                *,
                if_none_match: Optional[str] = ...,
                **kwargs: Any
            ) -> Optional[JSON]: ...

        @distributed_trace_async
        async def begin_delete_update(
                self,
                provider: str,
                name: str,
                version: str,
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace
        def list_providers(
                self,
                **kwargs: Any
            ) -> AsyncIterable[str]: ...

        @distributed_trace
        def list_names(
                self,
                provider: str,
                **kwargs: Any
            ) -> AsyncIterable[str]: ...

        @distributed_trace
        def list_versions(
                self,
                provider: str,
                name: str,
                *,
                filter: Optional[str] = ...,
                **kwargs: Any
            ) -> AsyncIterable[str]: ...

        @distributed_trace
        def list_files(
                self,
                provider: str,
                name: str,
                version: str,
                **kwargs: Any
            ) -> AsyncIterable[str]: ...

        @distributed_trace_async
        async def get_file(
                self,
                provider: str,
                name: str,
                version: str,
                file_id: str,
                *,
                if_none_match: Optional[str] = ...,
                **kwargs: Any
            ) -> Optional[JSON]: ...

        @distributed_trace
        def list_operations(
                self,
                *,
                filter: Optional[str] = ...,
                top: Optional[int] = ...,
                **kwargs: Any
            ) -> AsyncIterable[JSON]: ...

        @distributed_trace_async
        async def get_operation(
                self,
                operation_id: str,
                *,
                if_none_match: Optional[str] = ...,
                **kwargs: Any
            ) -> Optional[JSON]: ...


namespace azure.iot.deviceupdate.operations

    class azure.iot.deviceupdate.operations.DeviceManagementOperations:

        def __init__(
                self,
                *args,
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_device_classes(
                self,
                **kwargs: Any
            ) -> Iterable[JSON]: ...

        @distributed_trace
        def get_device_class(
                self,
                device_class_id: str,
                **kwargs: Any
            ) -> JSON: ...

        @overload
        def update_device_class(
                self,
                device_class_id: str,
                device_class_patch: JSON,
                *,
                content_type: str = 'application/merge-patch+json',
                **kwargs: Any
            ) -> JSON: ...

        @overload
        def update_device_class(
                self,
                device_class_id: str,
                device_class_patch: IO,
                *,
                content_type: str = 'application/merge-patch+json',
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace
        def delete_device_class(
                self,
                device_class_id: str,
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def list_installable_updates_for_device_class(
                self,
                device_class_id: str,
                **kwargs: Any
            ) -> Iterable[JSON]: ...

        @distributed_trace
        def list_devices(
                self,
                *,
                filter: Optional[str] = ...,
                **kwargs: Any
            ) -> Iterable[JSON]: ...

        @distributed_trace
        def begin_import_devices(
                self,
                import_type: str,
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get_device(
                self,
                device_id: str,
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace
        def get_device_module(
                self,
                device_id: str,
                module_id: str,
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace
        def get_update_compliance(
                self,
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace
        def list_groups(
                self,
                *,
                orderby: Optional[str] = ...,
                **kwargs: Any
            ) -> Iterable[JSON]: ...

        @distributed_trace
        def get_group(
                self,
                group_id: str,
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace
        def delete_group(
                self,
                group_id: str,
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get_group_update_compliance(
                self,
                group_id: str,
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace
        def list_best_updates_for_group(
                self,
                group_id: str,
                *,
                filter: Optional[str] = ...,
                **kwargs: Any
            ) -> Iterable[JSON]: ...

        @distributed_trace
        def list_deployments_for_group(
                self,
                group_id: str,
                *,
                orderby: Optional[str] = ...,
                **kwargs: Any
            ) -> Iterable[JSON]: ...

        @distributed_trace
        def get_deployment(
                self,
                group_id: str,
                deployment_id: str,
                **kwargs: Any
            ) -> JSON: ...

        @overload
        def create_or_update_deployment(
                self,
                group_id: str,
                deployment_id: str,
                deployment: JSON,
                *,
                content_type: str = 'application/json',
                **kwargs: Any
            ) -> JSON: ...

        @overload
        def create_or_update_deployment(
                self,
                group_id: str,
                deployment_id: str,
                deployment: IO,
                *,
                content_type: str = 'application/json',
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace
        def delete_deployment(
                self,
                group_id: str,
                deployment_id: str,
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get_deployment_status(
                self,
                group_id: str,
                deployment_id: str,
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace
        def list_device_class_subgroups_for_group(
                self,
                group_id: str,
                *,
                filter: Optional[str] = ...,
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace
        def get_device_class_subgroup_details(
                self,
                group_id: str,
                device_class_id: str,
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace
        def delete_device_class_subgroup(
                self,
                group_id: str,
                device_class_id: str,
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get_device_class_subgroup_update_compliance(
                self,
                group_id: str,
                device_class_id: str,
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace
        def list_best_updates_for_device_class_subgroup(
                self,
                group_id: str,
                device_class_id: str,
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace
        def list_deployments_for_device_class_subgroup(
                self,
                group_id: str,
                device_class_id: str,
                *,
                orderby: Optional[str] = ...,
                **kwargs: Any
            ) -> Iterable[JSON]: ...

        @distributed_trace
        def get_deployment_for_device_class_subgroup(
                self,
                group_id: str,
                device_class_id: str,
                deployment_id: str,
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace
        def delete_device_class_subgroup_deployment(
                self,
                group_id: str,
                device_class_id: str,
                deployment_id: str,
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def stop_deployment(
                self,
                group_id: str,
                device_class_id: str,
                deployment_id: str,
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace
        def retry_deployment(
                self,
                group_id: str,
                device_class_id: str,
                deployment_id: str,
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace
        def get_device_class_subgroup_deployment_status(
                self,
                group_id: str,
                device_class_id: str,
                deployment_id: str,
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace
        def list_devices_for_device_class_subgroup_deployment(
                self,
                group_id: str,
                device_class_id: str,
                deployment_id: str,
                *,
                filter: Optional[str] = ...,
                **kwargs: Any
            ) -> Iterable[JSON]: ...

        @distributed_trace
        def get_operation(
                self,
                operation_id: str,
                *,
                if_none_match: Optional[str] = ...,
                **kwargs: Any
            ) -> Optional[JSON]: ...

        @distributed_trace
        def list_operations(
                self,
                *,
                filter: Optional[str] = ...,
                top: Optional[int] = ...,
                **kwargs: Any
            ) -> Iterable[JSON]: ...

        @overload
        def collect_logs(
                self,
                operation_id: str,
                log_collection_request: JSON,
                *,
                content_type: str = 'application/json',
                **kwargs: Any
            ) -> JSON: ...

        @overload
        def collect_logs(
                self,
                operation_id: str,
                log_collection_request: IO,
                *,
                content_type: str = 'application/json',
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace
        def get_log_collection_operation(
                self,
                operation_id: str,
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace
        def list_log_collection_operations(
                self,
                **kwargs: Any
            ) -> Iterable[JSON]: ...

        @distributed_trace
        def get_log_collection_operation_detailed_status(
                self,
                operation_id: str,
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace
        def list_device_health(
                self,
                *,
                filter: str,
                **kwargs: Any
            ) -> JSON: ...


    class azure.iot.deviceupdate.operations.DeviceUpdateOperations:

        def __init__(
                self,
                *args,
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_updates(
                self,
                *,
                search: Optional[str] = ...,
                filter: Optional[str] = ...,
                **kwargs: Any
            ) -> Iterable[JSON]: ...

        @overload
        def begin_import_update(
                self,
                update_to_import: list[JSON],
                *,
                content_type: str = 'application/json',
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_import_update(
                self,
                update_to_import: IO,
                *,
                content_type: str = 'application/json',
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get_update(
                self,
                provider: str,
                name: str,
                version: str,
                *,
                if_none_match: Optional[str] = ...,
                **kwargs: Any
            ) -> Optional[JSON]: ...

        @distributed_trace
        def begin_delete_update(
                self,
                provider: str,
                name: str,
                version: str,
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def list_providers(
                self,
                **kwargs: Any
            ) -> Iterable[str]: ...

        @distributed_trace
        def list_names(
                self,
                provider: str,
                **kwargs: Any
            ) -> Iterable[str]: ...

        @distributed_trace
        def list_versions(
                self,
                provider: str,
                name: str,
                *,
                filter: Optional[str] = ...,
                **kwargs: Any
            ) -> Iterable[str]: ...

        @distributed_trace
        def list_files(
                self,
                provider: str,
                name: str,
                version: str,
                **kwargs: Any
            ) -> Iterable[str]: ...

        @distributed_trace
        def get_file(
                self,
                provider: str,
                name: str,
                version: str,
                file_id: str,
                *,
                if_none_match: Optional[str] = ...,
                **kwargs: Any
            ) -> Optional[JSON]: ...

        @distributed_trace
        def list_operations(
                self,
                *,
                filter: Optional[str] = ...,
                top: Optional[int] = ...,
                **kwargs: Any
            ) -> Iterable[JSON]: ...

        @distributed_trace
        def get_operation(
                self,
                operation_id: str,
                *,
                if_none_match: Optional[str] = ...,
                **kwargs: Any
            ) -> Optional[JSON]: ...


```
