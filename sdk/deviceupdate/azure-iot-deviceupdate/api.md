```py
namespace azure.iot.deviceupdate

    class azure.iot.deviceupdate.DeviceUpdateClient(DeviceUpdateClientGenerated): implements ContextManager 

        def __init__(
                self, 
                endpoint: str, 
                instance_id: str, 
                credential: TokenCredential, 
                *, 
                api_version: Optional[str] = ..., 
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


namespace azure.iot.deviceupdate.aio

    class azure.iot.deviceupdate.aio.DeviceUpdateClient(DeviceUpdateClientGenerated): implements AsyncContextManager 

        def __init__(
                self, 
                endpoint: str, 
                instance_id: str, 
                credential: AsyncTokenCredential, 
                *, 
                api_version: Optional[str] = ..., 
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


namespace azure.iot.deviceupdate.aio.operations

    class azure.iot.deviceupdate.aio.operations.DeviceManagementOperations(DeviceManagementOperationsGenerated):

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_import_devices(
                self, 
                import_type: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def create_or_update_deployment(
                self, 
                group_id: str, 
                deployment_id: str, 
                deployment: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JSON: ...

        @overload
        async def create_or_update_deployment(
                self, 
                group_id: str, 
                deployment_id: str, 
                deployment: IO[bytes], 
                *, 
                content_type: str = "application/json", 
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
        async def delete_deployment_for_device_class_subgroup(
                self, 
                group_id: str, 
                device_class_id: str, 
                deployment_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def delete_device_class(
                self, 
                device_class_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def delete_device_class_subgroup(
                self, 
                group_id: str, 
                device_class_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def delete_group(
                self, 
                group_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get_best_updates_for_device_class_subgroup(
                self, 
                group_id: str, 
                device_class_id: str, 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace_async
        async def get_deployment(
                self, 
                group_id: str, 
                deployment_id: str, 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace_async
        async def get_deployment_for_device_class_subgroup(
                self, 
                group_id: str, 
                device_class_id: str, 
                deployment_id: str, 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace_async
        async def get_deployment_status(
                self, 
                group_id: str, 
                deployment_id: str, 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace_async
        async def get_device(
                self, 
                device_id: str, 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace_async
        async def get_device_class(
                self, 
                device_class_id: str, 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace_async
        async def get_device_class_subgroup(
                self, 
                group_id: str, 
                device_class_id: str, 
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

        @distributed_trace_async
        async def get_device_class_subgroup_update_compliance(
                self, 
                group_id: str, 
                device_class_id: str, 
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
        async def get_group(
                self, 
                group_id: str, 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace_async
        async def get_log_collection(
                self, 
                log_collection_id: str, 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace_async
        async def get_log_collection_detailed_status(
                self, 
                log_collection_id: str, 
                **kwargs: Any
            ) -> JSON: ...

        async def get_operation_status(
                self, 
                operation_id: str, 
                *, 
                etag: Optional[str] = ..., 
                if_none_match: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ): ...

        @distributed_trace_async
        async def get_update_compliance(self, **kwargs: Any) -> JSON: ...

        @distributed_trace_async
        async def get_update_compliance_for_group(
                self, 
                group_id: str, 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace
        def list_best_updates_for_group(
                self, 
                group_id: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[JSON]: ...

        @distributed_trace
        def list_deployments_for_device_class_subgroup(
                self, 
                group_id: str, 
                device_class_id: str, 
                *, 
                order_by: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[JSON]: ...

        @distributed_trace
        def list_deployments_for_group(
                self, 
                group_id: str, 
                *, 
                order_by: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[JSON]: ...

        @distributed_trace
        def list_device_class_subgroups_for_group(
                self, 
                group_id: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[JSON]: ...

        @distributed_trace
        def list_device_classes(
                self, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[JSON]: ...

        @distributed_trace
        def list_device_states_for_device_class_subgroup_deployment(
                self, 
                group_id: str, 
                device_class_id: str, 
                deployment_id: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[JSON]: ...

        @distributed_trace
        def list_devices(
                self, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[JSON]: ...

        @distributed_trace
        def list_groups(
                self, 
                *, 
                order_by: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[JSON]: ...

        @distributed_trace
        def list_health_of_devices(
                self, 
                *, 
                filter: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[JSON]: ...

        @distributed_trace
        def list_installable_updates_for_device_class(
                self, 
                device_class_id: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[JSON]: ...

        @distributed_trace
        def list_log_collections(self, **kwargs: Any) -> AsyncItemPaged[JSON]: ...

        @distributed_trace
        def list_operation_statuses(
                self, 
                *, 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[JSON]: ...

        @distributed_trace_async
        async def retry_deployment(
                self, 
                group_id: str, 
                device_class_id: str, 
                deployment_id: str, 
                **kwargs: Any
            ) -> JSON: ...

        @overload
        async def start_log_collection(
                self, 
                log_collection_id: str, 
                log_collection: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JSON: ...

        @overload
        async def start_log_collection(
                self, 
                log_collection_id: str, 
                log_collection: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace_async
        async def stop_deployment(
                self, 
                group_id: str, 
                device_class_id: str, 
                deployment_id: str, 
                **kwargs: Any
            ) -> JSON: ...

        @overload
        async def update_device_class(
                self, 
                device_class_id: str, 
                device_class_patch: JSON, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> JSON: ...

        @overload
        async def update_device_class(
                self, 
                device_class_id: str, 
                device_class_patch: IO[bytes], 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> JSON: ...


    class azure.iot.deviceupdate.aio.operations.DeviceUpdateOperations(DeviceUpdateOperationsGenerated):

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
                update_to_import: list[JSON], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_import_update(
                self, 
                update_to_import: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        async def get_file(
                self, 
                provider: str, 
                name: str, 
                version: str, 
                file_id: str, 
                *, 
                etag: Optional[str] = ..., 
                if_none_match: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ): ...

        async def get_operation_status(
                self, 
                operation_id: str, 
                *, 
                etag: Optional[str] = ..., 
                if_none_match: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ): ...

        async def get_update(
                self, 
                provider: str, 
                name: str, 
                version: str, 
                *, 
                etag: Optional[str] = ..., 
                if_none_match: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ): ...

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
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[JSON]: ...

        @distributed_trace
        def list_providers(self, **kwargs: Any) -> AsyncItemPaged[str]: ...

        @distributed_trace
        def list_updates(
                self, 
                *, 
                filter: Optional[str] = ..., 
                search: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[JSON]: ...

        @distributed_trace
        def list_versions(
                self, 
                provider: str, 
                name: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[str]: ...


namespace azure.iot.deviceupdate.operations

    class azure.iot.deviceupdate.operations.DeviceManagementOperations(DeviceManagementOperationsGenerated):

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_import_devices(
                self, 
                import_type: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def create_or_update_deployment(
                self, 
                group_id: str, 
                deployment_id: str, 
                deployment: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JSON: ...

        @overload
        def create_or_update_deployment(
                self, 
                group_id: str, 
                deployment_id: str, 
                deployment: IO[bytes], 
                *, 
                content_type: str = "application/json", 
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
        def delete_deployment_for_device_class_subgroup(
                self, 
                group_id: str, 
                device_class_id: str, 
                deployment_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def delete_device_class(
                self, 
                device_class_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def delete_device_class_subgroup(
                self, 
                group_id: str, 
                device_class_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def delete_group(
                self, 
                group_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get_best_updates_for_device_class_subgroup(
                self, 
                group_id: str, 
                device_class_id: str, 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace
        def get_deployment(
                self, 
                group_id: str, 
                deployment_id: str, 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace
        def get_deployment_for_device_class_subgroup(
                self, 
                group_id: str, 
                device_class_id: str, 
                deployment_id: str, 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace
        def get_deployment_status(
                self, 
                group_id: str, 
                deployment_id: str, 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace
        def get_device(
                self, 
                device_id: str, 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace
        def get_device_class(
                self, 
                device_class_id: str, 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace
        def get_device_class_subgroup(
                self, 
                group_id: str, 
                device_class_id: str, 
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
        def get_device_class_subgroup_update_compliance(
                self, 
                group_id: str, 
                device_class_id: str, 
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
        def get_group(
                self, 
                group_id: str, 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace
        def get_log_collection(
                self, 
                log_collection_id: str, 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace
        def get_log_collection_detailed_status(
                self, 
                log_collection_id: str, 
                **kwargs: Any
            ) -> JSON: ...

        def get_operation_status(
                self, 
                operation_id: str, 
                *, 
                etag: Optional[str] = ..., 
                if_none_match: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ): ...

        @distributed_trace
        def get_update_compliance(self, **kwargs: Any) -> JSON: ...

        @distributed_trace
        def get_update_compliance_for_group(
                self, 
                group_id: str, 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace
        def list_best_updates_for_group(
                self, 
                group_id: str, 
                **kwargs: Any
            ) -> ItemPaged[JSON]: ...

        @distributed_trace
        def list_deployments_for_device_class_subgroup(
                self, 
                group_id: str, 
                device_class_id: str, 
                *, 
                order_by: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[JSON]: ...

        @distributed_trace
        def list_deployments_for_group(
                self, 
                group_id: str, 
                *, 
                order_by: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[JSON]: ...

        @distributed_trace
        def list_device_class_subgroups_for_group(
                self, 
                group_id: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[JSON]: ...

        @distributed_trace
        def list_device_classes(
                self, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[JSON]: ...

        @distributed_trace
        def list_device_states_for_device_class_subgroup_deployment(
                self, 
                group_id: str, 
                device_class_id: str, 
                deployment_id: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[JSON]: ...

        @distributed_trace
        def list_devices(
                self, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[JSON]: ...

        @distributed_trace
        def list_groups(
                self, 
                *, 
                order_by: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[JSON]: ...

        @distributed_trace
        def list_health_of_devices(
                self, 
                *, 
                filter: str, 
                **kwargs: Any
            ) -> ItemPaged[JSON]: ...

        @distributed_trace
        def list_installable_updates_for_device_class(
                self, 
                device_class_id: str, 
                **kwargs: Any
            ) -> ItemPaged[JSON]: ...

        @distributed_trace
        def list_log_collections(self, **kwargs: Any) -> ItemPaged[JSON]: ...

        @distributed_trace
        def list_operation_statuses(
                self, 
                *, 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[JSON]: ...

        @distributed_trace
        def retry_deployment(
                self, 
                group_id: str, 
                device_class_id: str, 
                deployment_id: str, 
                **kwargs: Any
            ) -> JSON: ...

        @overload
        def start_log_collection(
                self, 
                log_collection_id: str, 
                log_collection: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JSON: ...

        @overload
        def start_log_collection(
                self, 
                log_collection_id: str, 
                log_collection: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace
        def stop_deployment(
                self, 
                group_id: str, 
                device_class_id: str, 
                deployment_id: str, 
                **kwargs: Any
            ) -> JSON: ...

        @overload
        def update_device_class(
                self, 
                device_class_id: str, 
                device_class_patch: JSON, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> JSON: ...

        @overload
        def update_device_class(
                self, 
                device_class_id: str, 
                device_class_patch: IO[bytes], 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> JSON: ...


    class azure.iot.deviceupdate.operations.DeviceUpdateOperations(DeviceUpdateOperationsGenerated):

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
                update_to_import: list[JSON], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_import_update(
                self, 
                update_to_import: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        def get_file(
                self, 
                provider: str, 
                name: str, 
                version: str, 
                file_id: str, 
                *, 
                etag: Optional[str] = ..., 
                if_none_match: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ): ...

        def get_operation_status(
                self, 
                operation_id: str, 
                *, 
                etag: Optional[str] = ..., 
                if_none_match: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ): ...

        def get_update(
                self, 
                provider: str, 
                name: str, 
                version: str, 
                *, 
                etag: Optional[str] = ..., 
                if_none_match: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ): ...

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
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[JSON]: ...

        @distributed_trace
        def list_providers(self, **kwargs: Any) -> ItemPaged[str]: ...

        @distributed_trace
        def list_updates(
                self, 
                *, 
                filter: Optional[str] = ..., 
                search: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[JSON]: ...

        @distributed_trace
        def list_versions(
                self, 
                provider: str, 
                name: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[str]: ...


```