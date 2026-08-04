```py
namespace azure.mgmt.enclave

    class azure.mgmt.enclave.EnclaveMgmtClient: implements ContextManager 
        approval: ApprovalOperations
        community: CommunityOperations
        community_endpoints: CommunityEndpointsOperations
        dedicated_hub: DedicatedHubOperations
        enclave_connection: EnclaveConnectionOperations
        enclave_endpoints: EnclaveEndpointsOperations
        operations: Operations
        transit_hub: TransitHubOperations
        virtual_enclave: VirtualEnclaveOperations
        workload: WorkloadOperations

        def __init__(
                self, 
                credential: TokenCredential, 
                subscription_id: str, 
                base_url: Optional[str] = None, 
                *, 
                api_version: str = ..., 
                cloud_setting: Optional[AzureClouds] = ..., 
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


namespace azure.mgmt.enclave.aio

    class azure.mgmt.enclave.aio.EnclaveMgmtClient: implements AsyncContextManager 
        approval: ApprovalOperations
        community: CommunityOperations
        community_endpoints: CommunityEndpointsOperations
        dedicated_hub: DedicatedHubOperations
        enclave_connection: EnclaveConnectionOperations
        enclave_endpoints: EnclaveEndpointsOperations
        operations: Operations
        transit_hub: TransitHubOperations
        virtual_enclave: VirtualEnclaveOperations
        workload: WorkloadOperations

        def __init__(
                self, 
                credential: AsyncTokenCredential, 
                subscription_id: str, 
                base_url: Optional[str] = None, 
                *, 
                api_version: str = ..., 
                cloud_setting: Optional[AzureClouds] = ..., 
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


namespace azure.mgmt.enclave.aio.operations

    class azure.mgmt.enclave.aio.operations.ApprovalOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_uri: str, 
                approval_name: str, 
                resource: ApprovalResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ApprovalResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_uri: str, 
                approval_name: str, 
                resource: ApprovalResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ApprovalResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_uri: str, 
                approval_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ApprovalResource]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_uri: str, 
                approval_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_notify_initiator(
                self, 
                resource_uri: str, 
                approval_name: str, 
                body: ApprovalActionRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ApprovalActionResponse]: ...

        @overload
        async def begin_notify_initiator(
                self, 
                resource_uri: str, 
                approval_name: str, 
                body: ApprovalActionRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ApprovalActionResponse]: ...

        @overload
        async def begin_notify_initiator(
                self, 
                resource_uri: str, 
                approval_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ApprovalActionResponse]: ...

        @overload
        async def begin_update(
                self, 
                resource_uri: str, 
                approval_name: str, 
                properties: ApprovalPatchModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ApprovalResource]: ...

        @overload
        async def begin_update(
                self, 
                resource_uri: str, 
                approval_name: str, 
                properties: ApprovalPatchModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ApprovalResource]: ...

        @overload
        async def begin_update(
                self, 
                resource_uri: str, 
                approval_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ApprovalResource]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_uri: str, 
                approval_name: str, 
                **kwargs: Any
            ) -> ApprovalResource: ...

        @distributed_trace
        def list_by_parent(
                self, 
                resource_uri: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ApprovalResource]: ...


    class azure.mgmt.enclave.aio.operations.CommunityEndpointsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                community_name: str, 
                community_endpoint_name: str, 
                resource: CommunityEndpointResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CommunityEndpointResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                community_name: str, 
                community_endpoint_name: str, 
                resource: CommunityEndpointResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CommunityEndpointResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                community_name: str, 
                community_endpoint_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CommunityEndpointResource]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                community_name: str, 
                community_endpoint_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_handle_approval_creation(
                self, 
                resource_group_name: str, 
                community_name: str, 
                community_endpoint_name: str, 
                body: ApprovalCallbackRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ApprovalActionResponse]: ...

        @overload
        async def begin_handle_approval_creation(
                self, 
                resource_group_name: str, 
                community_name: str, 
                community_endpoint_name: str, 
                body: ApprovalCallbackRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ApprovalActionResponse]: ...

        @overload
        async def begin_handle_approval_creation(
                self, 
                resource_group_name: str, 
                community_name: str, 
                community_endpoint_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ApprovalActionResponse]: ...

        @overload
        async def begin_handle_approval_deletion(
                self, 
                resource_group_name: str, 
                community_name: str, 
                community_endpoint_name: str, 
                body: ApprovalDeletionCallbackRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ApprovalActionResponse]: ...

        @overload
        async def begin_handle_approval_deletion(
                self, 
                resource_group_name: str, 
                community_name: str, 
                community_endpoint_name: str, 
                body: ApprovalDeletionCallbackRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ApprovalActionResponse]: ...

        @overload
        async def begin_handle_approval_deletion(
                self, 
                resource_group_name: str, 
                community_name: str, 
                community_endpoint_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ApprovalActionResponse]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                community_name: str, 
                community_endpoint_name: str, 
                properties: CommunityEndpointPatchModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CommunityEndpointResource]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                community_name: str, 
                community_endpoint_name: str, 
                properties: CommunityEndpointPatchModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CommunityEndpointResource]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                community_name: str, 
                community_endpoint_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CommunityEndpointResource]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                community_name: str, 
                community_endpoint_name: str, 
                **kwargs: Any
            ) -> CommunityEndpointResource: ...

        @distributed_trace
        def list_by_community_resource(
                self, 
                resource_group_name: str, 
                community_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[CommunityEndpointResource]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                community_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[CommunityEndpointResource]: ...


    class azure.mgmt.enclave.aio.operations.CommunityOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                community_name: str, 
                resource: CommunityResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CommunityResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                community_name: str, 
                resource: CommunityResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CommunityResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                community_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CommunityResource]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                community_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                community_name: str, 
                properties: CommunityPatchModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CommunityResource]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                community_name: str, 
                properties: CommunityPatchModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CommunityResource]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                community_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CommunityResource]: ...

        @overload
        async def check_address_space_availability(
                self, 
                resource_group_name: str, 
                community_name: str, 
                check_address_space_availability_request: CheckAddressSpaceAvailabilityRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckAddressSpaceAvailabilityResponse: ...

        @overload
        async def check_address_space_availability(
                self, 
                resource_group_name: str, 
                community_name: str, 
                check_address_space_availability_request: CheckAddressSpaceAvailabilityRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckAddressSpaceAvailabilityResponse: ...

        @overload
        async def check_address_space_availability(
                self, 
                resource_group_name: str, 
                community_name: str, 
                check_address_space_availability_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckAddressSpaceAvailabilityResponse: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                community_name: str, 
                **kwargs: Any
            ) -> CommunityResource: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[CommunityResource]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[CommunityResource]: ...


    class azure.mgmt.enclave.aio.operations.DedicatedHubOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                community_name: str, 
                dedicated_hub_name: str, 
                resource: DedicatedHubResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DedicatedHubResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                community_name: str, 
                dedicated_hub_name: str, 
                resource: DedicatedHubResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DedicatedHubResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                community_name: str, 
                dedicated_hub_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DedicatedHubResource]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-11-01-preview', params_added_on={'2025-11-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'community_name', 'dedicated_hub_name']}, api_versions_list=['2025-11-01-preview', '2026-03-01-preview'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                community_name: str, 
                dedicated_hub_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                community_name: str, 
                dedicated_hub_name: str, 
                properties: DedicatedHubPatchModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DedicatedHubResource]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                community_name: str, 
                dedicated_hub_name: str, 
                properties: DedicatedHubPatchModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DedicatedHubResource]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                community_name: str, 
                dedicated_hub_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DedicatedHubResource]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-11-01-preview', params_added_on={'2025-11-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'community_name', 'dedicated_hub_name', 'accept']}, api_versions_list=['2025-11-01-preview', '2026-03-01-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                community_name: str, 
                dedicated_hub_name: str, 
                **kwargs: Any
            ) -> DedicatedHubResource: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-11-01-preview', params_added_on={'2025-11-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'community_name', 'accept']}, api_versions_list=['2025-11-01-preview', '2026-03-01-preview'])
        def list_by_community_resource(
                self, 
                resource_group_name: str, 
                community_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[DedicatedHubResource]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-11-01-preview', params_added_on={'2025-11-01-preview': ['api_version', 'subscription_id', 'community_name', 'accept']}, api_versions_list=['2025-11-01-preview', '2026-03-01-preview'])
        def list_by_subscription(
                self, 
                community_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[DedicatedHubResource]: ...


    class azure.mgmt.enclave.aio.operations.EnclaveConnectionOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                enclave_connection_name: str, 
                resource: EnclaveConnectionResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EnclaveConnectionResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                enclave_connection_name: str, 
                resource: EnclaveConnectionResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EnclaveConnectionResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                enclave_connection_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EnclaveConnectionResource]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                enclave_connection_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_handle_approval_creation(
                self, 
                resource_group_name: str, 
                enclave_connection_name: str, 
                body: ApprovalCallbackRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ApprovalActionResponse]: ...

        @overload
        async def begin_handle_approval_creation(
                self, 
                resource_group_name: str, 
                enclave_connection_name: str, 
                body: ApprovalCallbackRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ApprovalActionResponse]: ...

        @overload
        async def begin_handle_approval_creation(
                self, 
                resource_group_name: str, 
                enclave_connection_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ApprovalActionResponse]: ...

        @overload
        async def begin_handle_approval_deletion(
                self, 
                resource_group_name: str, 
                enclave_connection_name: str, 
                body: ApprovalDeletionCallbackRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ApprovalActionResponse]: ...

        @overload
        async def begin_handle_approval_deletion(
                self, 
                resource_group_name: str, 
                enclave_connection_name: str, 
                body: ApprovalDeletionCallbackRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ApprovalActionResponse]: ...

        @overload
        async def begin_handle_approval_deletion(
                self, 
                resource_group_name: str, 
                enclave_connection_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ApprovalActionResponse]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                enclave_connection_name: str, 
                properties: EnclaveConnectionPatchModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EnclaveConnectionResource]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                enclave_connection_name: str, 
                properties: EnclaveConnectionPatchModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EnclaveConnectionResource]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                enclave_connection_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EnclaveConnectionResource]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                enclave_connection_name: str, 
                **kwargs: Any
            ) -> EnclaveConnectionResource: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[EnclaveConnectionResource]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[EnclaveConnectionResource]: ...


    class azure.mgmt.enclave.aio.operations.EnclaveEndpointsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                virtual_enclave_name: str, 
                enclave_endpoint_name: str, 
                resource: EnclaveEndpointResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EnclaveEndpointResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                virtual_enclave_name: str, 
                enclave_endpoint_name: str, 
                resource: EnclaveEndpointResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EnclaveEndpointResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                virtual_enclave_name: str, 
                enclave_endpoint_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EnclaveEndpointResource]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                virtual_enclave_name: str, 
                enclave_endpoint_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_handle_approval_creation(
                self, 
                resource_group_name: str, 
                virtual_enclave_name: str, 
                enclave_endpoint_name: str, 
                body: ApprovalCallbackRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ApprovalActionResponse]: ...

        @overload
        async def begin_handle_approval_creation(
                self, 
                resource_group_name: str, 
                virtual_enclave_name: str, 
                enclave_endpoint_name: str, 
                body: ApprovalCallbackRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ApprovalActionResponse]: ...

        @overload
        async def begin_handle_approval_creation(
                self, 
                resource_group_name: str, 
                virtual_enclave_name: str, 
                enclave_endpoint_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ApprovalActionResponse]: ...

        @overload
        async def begin_handle_approval_deletion(
                self, 
                resource_group_name: str, 
                virtual_enclave_name: str, 
                enclave_endpoint_name: str, 
                body: ApprovalDeletionCallbackRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ApprovalActionResponse]: ...

        @overload
        async def begin_handle_approval_deletion(
                self, 
                resource_group_name: str, 
                virtual_enclave_name: str, 
                enclave_endpoint_name: str, 
                body: ApprovalDeletionCallbackRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ApprovalActionResponse]: ...

        @overload
        async def begin_handle_approval_deletion(
                self, 
                resource_group_name: str, 
                virtual_enclave_name: str, 
                enclave_endpoint_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ApprovalActionResponse]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                virtual_enclave_name: str, 
                enclave_endpoint_name: str, 
                properties: EnclaveEndpointPatchModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EnclaveEndpointResource]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                virtual_enclave_name: str, 
                enclave_endpoint_name: str, 
                properties: EnclaveEndpointPatchModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EnclaveEndpointResource]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                virtual_enclave_name: str, 
                enclave_endpoint_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EnclaveEndpointResource]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                virtual_enclave_name: str, 
                enclave_endpoint_name: str, 
                **kwargs: Any
            ) -> EnclaveEndpointResource: ...

        @distributed_trace
        def list_by_enclave_resource(
                self, 
                resource_group_name: str, 
                virtual_enclave_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[EnclaveEndpointResource]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                virtual_enclave_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[EnclaveEndpointResource]: ...


    class azure.mgmt.enclave.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


    class azure.mgmt.enclave.aio.operations.TransitHubOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                community_name: str, 
                transit_hub_name: str, 
                resource: TransitHubResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[TransitHubResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                community_name: str, 
                transit_hub_name: str, 
                resource: TransitHubResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[TransitHubResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                community_name: str, 
                transit_hub_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[TransitHubResource]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                community_name: str, 
                transit_hub_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                community_name: str, 
                transit_hub_name: str, 
                properties: TransitHubPatchModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[TransitHubResource]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                community_name: str, 
                transit_hub_name: str, 
                properties: TransitHubPatchModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[TransitHubResource]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                community_name: str, 
                transit_hub_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[TransitHubResource]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                community_name: str, 
                transit_hub_name: str, 
                **kwargs: Any
            ) -> TransitHubResource: ...

        @distributed_trace
        def list_by_community_resource(
                self, 
                resource_group_name: str, 
                community_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[TransitHubResource]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                community_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[TransitHubResource]: ...


    class azure.mgmt.enclave.aio.operations.VirtualEnclaveOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                virtual_enclave_name: str, 
                resource: EnclaveResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EnclaveResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                virtual_enclave_name: str, 
                resource: EnclaveResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EnclaveResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                virtual_enclave_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EnclaveResource]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                virtual_enclave_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_handle_approval_creation(
                self, 
                resource_group_name: str, 
                virtual_enclave_name: str, 
                body: ApprovalCallbackRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ApprovalActionResponse]: ...

        @overload
        async def begin_handle_approval_creation(
                self, 
                resource_group_name: str, 
                virtual_enclave_name: str, 
                body: ApprovalCallbackRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ApprovalActionResponse]: ...

        @overload
        async def begin_handle_approval_creation(
                self, 
                resource_group_name: str, 
                virtual_enclave_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ApprovalActionResponse]: ...

        @overload
        async def begin_handle_approval_deletion(
                self, 
                resource_group_name: str, 
                virtual_enclave_name: str, 
                body: ApprovalDeletionCallbackRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ApprovalActionResponse]: ...

        @overload
        async def begin_handle_approval_deletion(
                self, 
                resource_group_name: str, 
                virtual_enclave_name: str, 
                body: ApprovalDeletionCallbackRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ApprovalActionResponse]: ...

        @overload
        async def begin_handle_approval_deletion(
                self, 
                resource_group_name: str, 
                virtual_enclave_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ApprovalActionResponse]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                virtual_enclave_name: str, 
                properties: VirtualEnclavePatchModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EnclaveResource]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                virtual_enclave_name: str, 
                properties: VirtualEnclavePatchModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EnclaveResource]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                virtual_enclave_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EnclaveResource]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                virtual_enclave_name: str, 
                **kwargs: Any
            ) -> EnclaveResource: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[EnclaveResource]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[EnclaveResource]: ...


    class azure.mgmt.enclave.aio.operations.WorkloadOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                virtual_enclave_name: str, 
                workload_name: str, 
                resource: WorkloadResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[WorkloadResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                virtual_enclave_name: str, 
                workload_name: str, 
                resource: WorkloadResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[WorkloadResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                virtual_enclave_name: str, 
                workload_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[WorkloadResource]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                virtual_enclave_name: str, 
                workload_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                virtual_enclave_name: str, 
                workload_name: str, 
                properties: WorkloadPatchModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[WorkloadResource]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                virtual_enclave_name: str, 
                workload_name: str, 
                properties: WorkloadPatchModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[WorkloadResource]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                virtual_enclave_name: str, 
                workload_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[WorkloadResource]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                virtual_enclave_name: str, 
                workload_name: str, 
                **kwargs: Any
            ) -> WorkloadResource: ...

        @distributed_trace
        def list_by_enclave_resource(
                self, 
                resource_group_name: str, 
                virtual_enclave_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[WorkloadResource]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                virtual_enclave_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[WorkloadResource]: ...


namespace azure.mgmt.enclave.models

    class azure.mgmt.enclave.models.ActionPerformed(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPROVED = "Approved"
        REJECTED = "Rejected"


    class azure.mgmt.enclave.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.enclave.models.ApprovalActionRequest(_Model):
        approval_status: Union[Literal["Approved"], Literal["Rejected"], str]

        @overload
        def __init__(
                self, 
                *, 
                approval_status: Union[Literal[Approved], Literal[Rejected], str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.enclave.models.ApprovalActionResponse(_Model):
        message: str

        @overload
        def __init__(
                self, 
                *, 
                message: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.enclave.models.ApprovalCallbackRequest(_Model):
        approval_callback_payload: Optional[str]
        approval_status: Union[Literal["Approved"], Literal["Rejected"], str]
        resource_request_action: Union[Literal["Create"], Literal["Delete"], Literal["Update"], Literal["Reset"], str]

        @overload
        def __init__(
                self, 
                *, 
                approval_callback_payload: Optional[str] = ..., 
                approval_status: Union[Literal[Approved], Literal[Rejected], str], 
                resource_request_action: Union[Literal[Create], Literal[Delete], Literal[Update], Literal[Reset], str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.enclave.models.ApprovalDeletionCallbackRequest(_Model):
        resource_request_action: Union[Literal["Create"], Literal["Delete"], Literal["Update"], str]

        @overload
        def __init__(
                self, 
                *, 
                resource_request_action: Union[Literal[Create], Literal[Delete], Literal[Update], str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.enclave.models.ApprovalPatchModel(_Model):
        properties: Optional[ApprovalPatchProperties]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ApprovalPatchProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.enclave.models.ApprovalPatchProperties(_Model):
        approvers: Optional[list[Approver]]
        created_at: Optional[datetime]
        grandparent_resource_id: Optional[str]
        parent_resource_id: Optional[str]
        request_metadata: RequestMetadataUpdatableProperties
        state_changed_at: Optional[datetime]
        ticket_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                approvers: Optional[list[Approver]] = ..., 
                created_at: Optional[datetime] = ..., 
                grandparent_resource_id: Optional[str] = ..., 
                parent_resource_id: Optional[str] = ..., 
                request_metadata: RequestMetadataUpdatableProperties, 
                state_changed_at: Optional[datetime] = ..., 
                ticket_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.enclave.models.ApprovalPolicy(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NOT_REQUIRED = "NotRequired"
        REQUIRED = "Required"


    class azure.mgmt.enclave.models.ApprovalProperties(_Model):
        approved_by_entra_ids: Optional[list[str]]
        approvers: Optional[list[Approver]]
        approvers_approved_count: Optional[int]
        created_at: Optional[datetime]
        grandparent_resource_id: Optional[str]
        mandatory_approvers: Optional[list[MandatoryApprover]]
        mandatory_approvers_approved_count: Optional[int]
        minimum_approvers_required: Optional[int]
        parent_resource_id: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        request_metadata: RequestMetadata
        state_changed_at: Optional[datetime]
        ticket_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                approvers: Optional[list[Approver]] = ..., 
                created_at: Optional[datetime] = ..., 
                grandparent_resource_id: Optional[str] = ..., 
                parent_resource_id: Optional[str] = ..., 
                request_metadata: RequestMetadata, 
                state_changed_at: Optional[datetime] = ..., 
                ticket_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.enclave.models.ApprovalResource(ExtensionResource):
        id: str
        name: str
        properties: Optional[ApprovalProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ApprovalProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.enclave.models.ApprovalSettingConfiguration(_Model):
        approval_policy: Optional[Union[str, ApprovalPolicy]]
        mandatory_approvers: Optional[list[MandatoryApprover]]
        minimum_approvers_required: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                approval_policy: Optional[Union[str, ApprovalPolicy]] = ..., 
                mandatory_approvers: Optional[list[MandatoryApprover]] = ..., 
                minimum_approvers_required: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.enclave.models.ApprovalSettings(_Model):
        community_endpoint_update: Optional[ApprovalSettingConfiguration]
        community_maintenance_mode: Optional[ApprovalSettingConfiguration]
        connection_creation: Optional[ApprovalSettingConfiguration]
        connection_update: Optional[ApprovalSettingConfiguration]
        enclave_creation: Optional[ApprovalSettingConfiguration]
        enclave_endpoint_update: Optional[ApprovalSettingConfiguration]
        enclave_maintenance_mode: Optional[ApprovalSettingConfiguration]

        @overload
        def __init__(
                self, 
                *, 
                community_endpoint_update: Optional[ApprovalSettingConfiguration] = ..., 
                community_maintenance_mode: Optional[ApprovalSettingConfiguration] = ..., 
                connection_creation: Optional[ApprovalSettingConfiguration] = ..., 
                connection_update: Optional[ApprovalSettingConfiguration] = ..., 
                enclave_creation: Optional[ApprovalSettingConfiguration] = ..., 
                enclave_endpoint_update: Optional[ApprovalSettingConfiguration] = ..., 
                enclave_maintenance_mode: Optional[ApprovalSettingConfiguration] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.enclave.models.ApprovalSettingsPatchProperties(_Model):
        community_endpoint_update: Optional[ApprovalSettingConfiguration]
        community_maintenance_mode: Optional[ApprovalSettingConfiguration]
        connection_creation: Optional[ApprovalSettingConfiguration]
        connection_update: Optional[ApprovalSettingConfiguration]
        enclave_creation: Optional[ApprovalSettingConfiguration]
        enclave_endpoint_update: Optional[ApprovalSettingConfiguration]
        enclave_maintenance_mode: Optional[ApprovalSettingConfiguration]

        @overload
        def __init__(
                self, 
                *, 
                community_endpoint_update: Optional[ApprovalSettingConfiguration] = ..., 
                community_maintenance_mode: Optional[ApprovalSettingConfiguration] = ..., 
                connection_creation: Optional[ApprovalSettingConfiguration] = ..., 
                connection_update: Optional[ApprovalSettingConfiguration] = ..., 
                enclave_creation: Optional[ApprovalSettingConfiguration] = ..., 
                enclave_endpoint_update: Optional[ApprovalSettingConfiguration] = ..., 
                enclave_maintenance_mode: Optional[ApprovalSettingConfiguration] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.enclave.models.ApprovalStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPROVED = "Approved"
        DELETED = "Deleted"
        EXPIRED = "Expired"
        PENDING = "Pending"
        REJECTED = "Rejected"


    class azure.mgmt.enclave.models.Approver(_Model):
        action_performed: Optional[Union[str, ActionPerformed]]
        approver_entra_id: str
        last_updated_at: datetime
        mandatory_approval_group_membership_ids: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                action_performed: Optional[Union[str, ActionPerformed]] = ..., 
                approver_entra_id: str, 
                last_updated_at: datetime
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.enclave.models.CheckAddressSpaceAvailabilityRequest(_Model):
        community_resource_id: str
        enclave_virtual_network: EnclaveVirtualNetworkModel

        @overload
        def __init__(
                self, 
                *, 
                community_resource_id: str, 
                enclave_virtual_network: EnclaveVirtualNetworkModel
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.enclave.models.CheckAddressSpaceAvailabilityResponse(_Model):
        value: bool

        @overload
        def __init__(
                self, 
                *, 
                value: bool
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.enclave.models.CommunityEndpointDestinationRule(_Model):
        destination: Optional[str]
        destination_type: Optional[Union[str, DestinationType]]
        endpoint_rule_name: Optional[str]
        ports: Optional[str]
        protocols: Optional[list[Union[str, CommunityEndpointProtocol]]]
        transit_hub_resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                destination: Optional[str] = ..., 
                destination_type: Optional[Union[str, DestinationType]] = ..., 
                endpoint_rule_name: Optional[str] = ..., 
                ports: Optional[str] = ..., 
                protocols: Optional[list[Union[str, CommunityEndpointProtocol]]] = ..., 
                transit_hub_resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.enclave.models.CommunityEndpointPatchModel(_Model):
        properties: Optional[CommunityEndpointPatchProperties]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[CommunityEndpointPatchProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.enclave.models.CommunityEndpointPatchProperties(_Model):
        rule_collection: list[CommunityEndpointDestinationRule]
        update_mode: Optional[Union[str, UpdateMode]]

        @overload
        def __init__(
                self, 
                *, 
                rule_collection: list[CommunityEndpointDestinationRule], 
                update_mode: Optional[Union[str, UpdateMode]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.enclave.models.CommunityEndpointProperties(_Model):
        provisioning_state: Optional[Union[str, ProvisioningState]]
        resource_collection: Optional[list[str]]
        rule_collection: list[CommunityEndpointDestinationRule]
        update_mode: Optional[Union[str, UpdateMode]]

        @overload
        def __init__(
                self, 
                *, 
                rule_collection: list[CommunityEndpointDestinationRule], 
                update_mode: Optional[Union[str, UpdateMode]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.enclave.models.CommunityEndpointProtocol(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AH = "AH"
        ANY = "ANY"
        ESP = "ESP"
        HTTP = "HTTP"
        HTTPS = "HTTPS"
        ICMP = "ICMP"
        TCP = "TCP"
        UDP = "UDP"


    class azure.mgmt.enclave.models.CommunityEndpointResource(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[CommunityEndpointProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[CommunityEndpointProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.enclave.models.CommunityPatchModel(_Model):
        identity: Optional[ManagedServiceIdentity]
        properties: Optional[CommunityPatchProperties]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                properties: Optional[CommunityPatchProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.enclave.models.CommunityPatchProperties(_Model):
        address_spaces: Optional[list[str]]
        community_role_assignments: Optional[list[RoleAssignmentItem]]
        dns_servers: Optional[list[str]]
        firewall_sku: Optional[Union[str, FirewallSKU]]
        governed_service_list: Optional[list[GovernedServiceItem]]
        granular_approval_settings: Optional[ApprovalSettingsPatchProperties]
        maintenance_mode_configuration: Optional[MaintenanceModeConfigurationPatchModel]
        monitoring_settings: Optional[MonitoringSettingsPatchModel]
        policy_override: Optional[Union[Literal["Enclave"], Literal["None"], str]]

        @overload
        def __init__(
                self, 
                *, 
                address_spaces: Optional[list[str]] = ..., 
                community_role_assignments: Optional[list[RoleAssignmentItem]] = ..., 
                dns_servers: Optional[list[str]] = ..., 
                firewall_sku: Optional[Union[str, FirewallSKU]] = ..., 
                governed_service_list: Optional[list[GovernedServiceItem]] = ..., 
                granular_approval_settings: Optional[ApprovalSettingsPatchProperties] = ..., 
                maintenance_mode_configuration: Optional[MaintenanceModeConfigurationPatchModel] = ..., 
                monitoring_settings: Optional[MonitoringSettingsPatchModel] = ..., 
                policy_override: Optional[Union[Literal[Enclave], Literal[None], str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.enclave.models.CommunityProperties(_Model):
        address_space: Optional[str]
        address_spaces: Optional[list[str]]
        community_role_assignments: Optional[list[RoleAssignmentItem]]
        dedicated_hub_list: Optional[list[DedicatedHubResource]]
        dns_servers: Optional[list[str]]
        firewall_sku: Optional[Union[str, FirewallSKU]]
        governed_service_list: Optional[list[GovernedServiceItem]]
        granular_approval_settings: Optional[ApprovalSettings]
        maintenance_mode_configuration: Optional[MaintenanceModeConfigurationModel]
        managed_on_behalf_of_configuration: Optional[ManagedOnBehalfOfConfiguration]
        managed_resource_group_name: Optional[str]
        monitoring_settings: Optional[MonitoringSettingsModel]
        policy_override: Optional[Union[Literal["Enclave"], Literal["None"], str]]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        resource_collection: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                address_space: Optional[str] = ..., 
                address_spaces: Optional[list[str]] = ..., 
                community_role_assignments: Optional[list[RoleAssignmentItem]] = ..., 
                dns_servers: Optional[list[str]] = ..., 
                firewall_sku: Optional[Union[str, FirewallSKU]] = ..., 
                governed_service_list: Optional[list[GovernedServiceItem]] = ..., 
                granular_approval_settings: Optional[ApprovalSettings] = ..., 
                maintenance_mode_configuration: Optional[MaintenanceModeConfigurationModel] = ..., 
                monitoring_settings: Optional[MonitoringSettingsModel] = ..., 
                policy_override: Optional[Union[Literal[Enclave], Literal[None], str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.enclave.models.CommunityResource(TrackedResource):
        id: str
        identity: Optional[ManagedServiceIdentity]
        location: str
        name: str
        properties: Optional[CommunityProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                location: str, 
                properties: Optional[CommunityProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.enclave.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.enclave.models.DedicatedHubPatchModel(_Model):
        properties: Optional[DedicatedHubPatchProperties]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[DedicatedHubPatchProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.enclave.models.DedicatedHubPatchProperties(_Model):
        designation: Optional[Union[str, Designation]]

        @overload
        def __init__(
                self, 
                *, 
                designation: Optional[Union[str, Designation]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.enclave.models.DedicatedHubProperties(_Model):
        designation: Optional[Union[str, Designation]]
        firewall_policy_resource_id: Optional[str]
        firewall_resource_id: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        v_hub_resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                designation: Optional[Union[str, Designation]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.enclave.models.DedicatedHubResource(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[DedicatedHubProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[DedicatedHubProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.enclave.models.Designation(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        POOLED = "Pooled"
        RESERVED = "Reserved"


    class azure.mgmt.enclave.models.DestinationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FQDN = "FQDN"
        FQDN_TAG = "FQDNTag"
        IP_ADDRESS = "IPAddress"
        PRIVATE_NETWORK = "PrivateNetwork"
        SERVICE_TAG = "ServiceTag"


    class azure.mgmt.enclave.models.DiagnosticDestination(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BOTH = "Both"
        COMMUNITY_ONLY = "CommunityOnly"
        ENCLAVE_ONLY = "EnclaveOnly"


    class azure.mgmt.enclave.models.EnclaveAddressSpacesModel(_Model):
        enclave_address_space: Optional[str]
        managed_address_space: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                enclave_address_space: Optional[str] = ..., 
                managed_address_space: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.enclave.models.EnclaveConnectionPatchModel(_Model):
        properties: Optional[EnclaveConnectionPatchProperties]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[EnclaveConnectionPatchProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.enclave.models.EnclaveConnectionPatchProperties(_Model):
        source_cidr: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                source_cidr: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.enclave.models.EnclaveConnectionProperties(_Model):
        community_resource_id: str
        destination_endpoint_id: str
        provisioning_state: Optional[Union[str, ProvisioningState]]
        resource_collection: Optional[list[str]]
        source_cidr: Optional[str]
        source_resource_id: str
        state: Optional[Union[str, EnclaveConnectionState]]
        update_mode: Optional[Union[str, UpdateMode]]

        @overload
        def __init__(
                self, 
                *, 
                community_resource_id: str, 
                destination_endpoint_id: str, 
                source_cidr: Optional[str] = ..., 
                source_resource_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.enclave.models.EnclaveConnectionResource(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[EnclaveConnectionProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[EnclaveConnectionProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.enclave.models.EnclaveConnectionState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        APPROVED = "Approved"
        CONNECTED = "Connected"
        DISCONNECTED = "Disconnected"
        FAILED = "Failed"
        PENDING_APPROVAL = "PendingApproval"
        PENDING_UPDATE = "PendingUpdate"


    class azure.mgmt.enclave.models.EnclaveDefaultSettingsModel(_Model):
        diagnostic_destination: Optional[Union[str, DiagnosticDestination]]
        key_vault_resource_id: Optional[str]
        log_analytics_resource_id_collection: Optional[list[str]]
        storage_account_resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                diagnostic_destination: Optional[Union[str, DiagnosticDestination]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.enclave.models.EnclaveDefaultSettingsPatchModel(_Model):
        diagnostic_destination: Optional[Union[str, DiagnosticDestination]]

        @overload
        def __init__(
                self, 
                *, 
                diagnostic_destination: Optional[Union[str, DiagnosticDestination]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.enclave.models.EnclaveEndpointDestinationRule(_Model):
        destination: Optional[str]
        endpoint_rule_name: Optional[str]
        ports: Optional[str]
        protocols: Optional[list[Union[str, EnclaveEndpointProtocol]]]

        @overload
        def __init__(
                self, 
                *, 
                destination: Optional[str] = ..., 
                endpoint_rule_name: Optional[str] = ..., 
                ports: Optional[str] = ..., 
                protocols: Optional[list[Union[str, EnclaveEndpointProtocol]]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.enclave.models.EnclaveEndpointPatchModel(_Model):
        properties: Optional[EnclaveEndpointPatchProperties]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[EnclaveEndpointPatchProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.enclave.models.EnclaveEndpointPatchProperties(_Model):
        rule_collection: list[EnclaveEndpointDestinationRule]
        update_mode: Optional[Union[str, UpdateMode]]

        @overload
        def __init__(
                self, 
                *, 
                rule_collection: list[EnclaveEndpointDestinationRule], 
                update_mode: Optional[Union[str, UpdateMode]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.enclave.models.EnclaveEndpointProperties(_Model):
        provisioning_state: Optional[Union[str, ProvisioningState]]
        resource_collection: Optional[list[str]]
        rule_collection: list[EnclaveEndpointDestinationRule]
        update_mode: Optional[Union[str, UpdateMode]]

        @overload
        def __init__(
                self, 
                *, 
                rule_collection: list[EnclaveEndpointDestinationRule], 
                update_mode: Optional[Union[str, UpdateMode]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.enclave.models.EnclaveEndpointProtocol(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AH = "AH"
        ANY = "ANY"
        ESP = "ESP"
        ICMP = "ICMP"
        TCP = "TCP"
        UDP = "UDP"


    class azure.mgmt.enclave.models.EnclaveEndpointResource(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[EnclaveEndpointProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[EnclaveEndpointProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.enclave.models.EnclaveResource(TrackedResource):
        id: str
        identity: Optional[ManagedServiceIdentity]
        location: str
        name: str
        properties: Optional[VirtualEnclaveProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                location: str, 
                properties: Optional[VirtualEnclaveProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.enclave.models.EnclaveVirtualNetworkModel(_Model):
        allow_subnet_communication: Optional[bool]
        custom_cidr_range: Optional[str]
        network_name: Optional[str]
        network_size: Optional[str]
        subnet_configurations: Optional[list[SubnetConfiguration]]

        @overload
        def __init__(
                self, 
                *, 
                allow_subnet_communication: Optional[bool] = ..., 
                custom_cidr_range: Optional[str] = ..., 
                network_name: Optional[str] = ..., 
                network_size: Optional[str] = ..., 
                subnet_configurations: Optional[list[SubnetConfiguration]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.enclave.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.enclave.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.enclave.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.enclave.models.ExtensionResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.enclave.models.FirewallSKU(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BASIC = "Basic"
        PREMIUM = "Premium"
        STANDARD = "Standard"


    class azure.mgmt.enclave.models.GovernedServiceItem(_Model):
        enforcement: Optional[Union[Literal["Enabled"], Literal["Disabled"], str]]
        initiatives: Optional[list[str]]
        option: Optional[Union[Literal["Allow"], Literal["Deny"], Literal["ExceptionOnly"], Literal["NotApplicable"], str]]
        policy_action: Optional[Union[Literal["AuditOnly"], Literal["Enforce"], Literal["None"], str]]
        service_id: Union[str, ServiceIdentifier]
        service_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                enforcement: Optional[Union[Literal[Enabled], Literal[Disabled], str]] = ..., 
                option: Optional[Union[Literal[Allow], Literal[Deny], Literal[ExceptionOnly], Literal[NotApplicable], str]] = ..., 
                policy_action: Optional[Union[Literal[AuditOnly], Literal[Enforce], Literal[None], str]] = ..., 
                service_id: Union[str, ServiceIdentifier]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.enclave.models.MaintenanceModeConfigurationModel(_Model):
        justification: Optional[Union[Literal["Networking"], Literal["Governance"], Literal["Off"], str]]
        mode: Union[Literal["On"], Literal["CanNotDelete"], Literal["Off"], Literal["General"], Literal["Advanced"], str]
        principals: Optional[list[Principal]]

        @overload
        def __init__(
                self, 
                *, 
                justification: Optional[Union[Literal[Networking], Literal[Governance], Literal[Off], str]] = ..., 
                mode: Union[Literal[On], Literal[CanNotDelete], Literal[Off], Literal[General], Literal[Advanced], str], 
                principals: Optional[list[Principal]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.enclave.models.MaintenanceModeConfigurationPatchModel(_Model):
        justification: Optional[Union[Literal["Networking"], Literal["Governance"], Literal["Off"], str]]
        mode: Union[Literal["On"], Literal["CanNotDelete"], Literal["Off"], Literal["General"], Literal["Advanced"], str]
        principals: Optional[list[Principal]]

        @overload
        def __init__(
                self, 
                *, 
                justification: Optional[Union[Literal[Networking], Literal[Governance], Literal[Off], str]] = ..., 
                mode: Union[Literal[On], Literal[CanNotDelete], Literal[Off], Literal[General], Literal[Advanced], str], 
                principals: Optional[list[Principal]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.enclave.models.ManagedOnBehalfOfConfiguration(_Model):
        mobo_broker_resources: Optional[list[MoboBrokerResource]]


    class azure.mgmt.enclave.models.ManagedServiceIdentity(_Model):
        principal_id: Optional[str]
        tenant_id: Optional[str]
        type: Union[str, ManagedServiceIdentityType]
        user_assigned_identities: Optional[dict[str, UserAssignedIdentity]]

        @overload
        def __init__(
                self, 
                *, 
                type: Union[str, ManagedServiceIdentityType], 
                user_assigned_identities: Optional[dict[str, UserAssignedIdentity]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.enclave.models.ManagedServiceIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        SYSTEM_ASSIGNED_USER_ASSIGNED = "SystemAssigned,UserAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.enclave.models.MandatoryApprover(_Model):
        approver_entra_id: str

        @overload
        def __init__(
                self, 
                *, 
                approver_entra_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.enclave.models.MoboBrokerResource(_Model):
        id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.enclave.models.MonitoringDestination(_Model):
        custom_workspace_resource_id: Optional[str]
        destination_type: Union[str, MonitoringDestinationType]
        diagnostic_settings_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                custom_workspace_resource_id: Optional[str] = ..., 
                destination_type: Union[str, MonitoringDestinationType], 
                diagnostic_settings_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.enclave.models.MonitoringDestinationPatchModel(_Model):
        custom_workspace_resource_id: Optional[str]
        destination_type: Union[str, MonitoringDestinationType]
        diagnostic_settings_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                custom_workspace_resource_id: Optional[str] = ..., 
                destination_type: Union[str, MonitoringDestinationType], 
                diagnostic_settings_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.enclave.models.MonitoringDestinationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMMUNITY_WORKSPACE = "CommunityWorkspace"
        CUSTOM_WORKSPACE = "CustomWorkspace"
        ENCLAVE_WORKSPACE = "EnclaveWorkspace"


    class azure.mgmt.enclave.models.MonitoringSettingsModel(_Model):
        diagnostic_destinations: Optional[list[MonitoringDestination]]
        flow_log_destination: Optional[MonitoringDestination]

        @overload
        def __init__(
                self, 
                *, 
                diagnostic_destinations: Optional[list[MonitoringDestination]] = ..., 
                flow_log_destination: Optional[MonitoringDestination] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.enclave.models.MonitoringSettingsPatchModel(_Model):
        diagnostic_destinations: Optional[list[MonitoringDestinationPatchModel]]
        flow_log_destination: Optional[MonitoringDestinationPatchModel]

        @overload
        def __init__(
                self, 
                *, 
                diagnostic_destinations: Optional[list[MonitoringDestinationPatchModel]] = ..., 
                flow_log_destination: Optional[MonitoringDestinationPatchModel] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.enclave.models.Operation(_Model):
        action_type: Optional[Union[str, ActionType]]
        display: Optional[OperationDisplay]
        is_data_action: Optional[bool]
        name: Optional[str]
        origin: Optional[Union[str, Origin]]

        @overload
        def __init__(
                self, 
                *, 
                display: Optional[OperationDisplay] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.enclave.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.enclave.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.enclave.models.Principal(_Model):
        id: str
        type: Union[Literal["User"], Literal["Group"], Literal["ServicePrincipal"], str]

        @overload
        def __init__(
                self, 
                *, 
                id: str, 
                type: Union[Literal[User], Literal[Group], Literal[ServicePrincipal], str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.enclave.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        NOT_SPECIFIED = "NotSpecified"
        RUNNING = "Running"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.enclave.models.RbacInheritanceMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.enclave.models.RequestMetadata(_Model):
        approval_callback_payload: Optional[str]
        approval_callback_route: Optional[str]
        approval_status: Optional[Union[str, ApprovalStatus]]
        resource_action: str

        @overload
        def __init__(
                self, 
                *, 
                approval_callback_payload: Optional[str] = ..., 
                approval_callback_route: Optional[str] = ..., 
                approval_status: Optional[Union[str, ApprovalStatus]] = ..., 
                resource_action: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.enclave.models.RequestMetadataUpdatableProperties(_Model):
        approval_callback_payload: Optional[str]
        approval_callback_route: Optional[str]
        approval_status: Optional[Union[str, ApprovalStatus]]
        resource_action: str

        @overload
        def __init__(
                self, 
                *, 
                approval_callback_payload: Optional[str] = ..., 
                approval_callback_route: Optional[str] = ..., 
                approval_status: Optional[Union[str, ApprovalStatus]] = ..., 
                resource_action: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.enclave.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.enclave.models.ResourceVisibilityMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.enclave.models.RoleAssignmentItem(_Model):
        condition: Optional[str]
        principals: Optional[list[Principal]]
        role_definition_id: str

        @overload
        def __init__(
                self, 
                *, 
                condition: Optional[str] = ..., 
                principals: Optional[list[Principal]] = ..., 
                role_definition_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.enclave.models.SecurityProvider(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_FIREWALL = "AzureFirewall"
        NONE = "None"


    class azure.mgmt.enclave.models.ServiceIdentifier(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AKS = "AKS"
        APP_SERVICE = "AppService"
        AZURE_FIREWALLS = "AzureFirewalls"
        CONTAINER_REGISTRY = "ContainerRegistry"
        COSMOS_DB = "CosmosDB"
        DATA_CONNECTORS = "DataConnectors"
        INSIGHTS = "Insights"
        KEY_VAULT = "KeyVault"
        LOGIC = "Logic"
        MICROSOFT_SQL = "MicrosoftSQL"
        MONITORING = "Monitoring"
        POSTGRE_SQL = "PostgreSQL"
        PRIVATE_DNS_ZONES = "PrivateDNSZones"
        SERVICE_BUS = "ServiceBus"
        STORAGE = "Storage"


    class azure.mgmt.enclave.models.SubnetConfiguration(_Model):
        address_prefix: Optional[str]
        network_prefix_size: int
        network_security_group_resource_id: Optional[str]
        subnet_delegation: Optional[str]
        subnet_name: str
        subnet_resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                network_prefix_size: int, 
                subnet_delegation: Optional[str] = ..., 
                subnet_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.enclave.models.SystemData(_Model):
        created_at: Optional[datetime]
        created_by: Optional[str]
        created_by_type: Optional[Union[str, CreatedByType]]
        last_modified_at: Optional[datetime]
        last_modified_by: Optional[str]
        last_modified_by_type: Optional[Union[str, CreatedByType]]

        @overload
        def __init__(
                self, 
                *, 
                created_at: Optional[datetime] = ..., 
                created_by: Optional[str] = ..., 
                created_by_type: Optional[Union[str, CreatedByType]] = ..., 
                last_modified_at: Optional[datetime] = ..., 
                last_modified_by: Optional[str] = ..., 
                last_modified_by_type: Optional[Union[str, CreatedByType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.enclave.models.TrackedResource(Resource):
        id: str
        location: str
        name: str
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.enclave.models.TransitHubPatchModel(_Model):
        properties: Optional[TransitHubPatchProperties]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[TransitHubPatchProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.enclave.models.TransitHubPatchProperties(_Model):
        security_provider: Optional[Union[str, SecurityProvider]]
        state: Optional[Union[str, TransitHubState]]
        transit_option: Optional[TransitOption]

        @overload
        def __init__(
                self, 
                *, 
                security_provider: Optional[Union[str, SecurityProvider]] = ..., 
                state: Optional[Union[str, TransitHubState]] = ..., 
                transit_option: Optional[TransitOption] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.enclave.models.TransitHubProperties(_Model):
        provisioning_state: Optional[Union[str, ProvisioningState]]
        resource_collection: Optional[list[str]]
        security_provider: Optional[Union[str, SecurityProvider]]
        state: Optional[Union[str, TransitHubState]]
        transit_option: Optional[TransitOption]

        @overload
        def __init__(
                self, 
                *, 
                security_provider: Optional[Union[str, SecurityProvider]] = ..., 
                state: Optional[Union[str, TransitHubState]] = ..., 
                transit_option: Optional[TransitOption] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.enclave.models.TransitHubResource(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[TransitHubProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[TransitHubProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.enclave.models.TransitHubState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        APPROVED = "Approved"
        FAILED = "Failed"
        PENDING_APPROVAL = "PendingApproval"
        PENDING_UPDATE = "PendingUpdate"


    class azure.mgmt.enclave.models.TransitOption(_Model):
        params: Optional[TransitOptionParams]
        type: Optional[Union[str, TransitOptionType]]

        @overload
        def __init__(
                self, 
                *, 
                params: Optional[TransitOptionParams] = ..., 
                type: Optional[Union[str, TransitOptionType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.enclave.models.TransitOptionParams(_Model):
        remote_virtual_network_id: Optional[str]
        scale_units: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                remote_virtual_network_id: Optional[str] = ..., 
                scale_units: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.enclave.models.TransitOptionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EXPRESS_ROUTE = "ExpressRoute"
        GATEWAY = "Gateway"
        PEERING = "Peering"


    class azure.mgmt.enclave.models.UpdateMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTOMATIC = "Automatic"
        MANUAL = "Manual"


    class azure.mgmt.enclave.models.UserAssignedIdentity(_Model):
        client_id: Optional[str]
        principal_id: Optional[str]


    class azure.mgmt.enclave.models.VirtualEnclaveApprovalSettings(_Model):
        connection_creation: Optional[ApprovalSettingConfiguration]
        connection_update: Optional[ApprovalSettingConfiguration]
        enclave_endpoint_update: Optional[ApprovalSettingConfiguration]
        enclave_maintenance_mode: Optional[ApprovalSettingConfiguration]

        @overload
        def __init__(
                self, 
                *, 
                connection_creation: Optional[ApprovalSettingConfiguration] = ..., 
                connection_update: Optional[ApprovalSettingConfiguration] = ..., 
                enclave_endpoint_update: Optional[ApprovalSettingConfiguration] = ..., 
                enclave_maintenance_mode: Optional[ApprovalSettingConfiguration] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.enclave.models.VirtualEnclaveApprovalSettingsPatchProperties(_Model):
        connection_creation: Optional[ApprovalSettingConfiguration]
        connection_update: Optional[ApprovalSettingConfiguration]
        enclave_endpoint_update: Optional[ApprovalSettingConfiguration]
        enclave_maintenance_mode: Optional[ApprovalSettingConfiguration]

        @overload
        def __init__(
                self, 
                *, 
                connection_creation: Optional[ApprovalSettingConfiguration] = ..., 
                connection_update: Optional[ApprovalSettingConfiguration] = ..., 
                enclave_endpoint_update: Optional[ApprovalSettingConfiguration] = ..., 
                enclave_maintenance_mode: Optional[ApprovalSettingConfiguration] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.enclave.models.VirtualEnclavePatchModel(_Model):
        identity: Optional[ManagedServiceIdentity]
        properties: Optional[VirtualEnclavePatchProperties]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                properties: Optional[VirtualEnclavePatchProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.enclave.models.VirtualEnclavePatchProperties(_Model):
        approval_settings: Optional[VirtualEnclaveApprovalSettingsPatchProperties]
        bastion_enabled: Optional[bool]
        dedicated_hub_resource_id: Optional[str]
        enclave_default_settings: Optional[EnclaveDefaultSettingsPatchModel]
        enclave_role_assignments: Optional[list[RoleAssignmentItem]]
        enclave_virtual_network: EnclaveVirtualNetworkModel
        governed_service_list: Optional[list[GovernedServiceItem]]
        maintenance_mode_configuration: Optional[MaintenanceModeConfigurationPatchModel]
        monitoring_settings: Optional[MonitoringSettingsPatchModel]
        rbac_inheritance: Optional[Union[str, RbacInheritanceMode]]
        workload_resource_visibility: Optional[Union[str, ResourceVisibilityMode]]
        workload_role_assignments: Optional[list[RoleAssignmentItem]]

        @overload
        def __init__(
                self, 
                *, 
                approval_settings: Optional[VirtualEnclaveApprovalSettingsPatchProperties] = ..., 
                bastion_enabled: Optional[bool] = ..., 
                dedicated_hub_resource_id: Optional[str] = ..., 
                enclave_default_settings: Optional[EnclaveDefaultSettingsPatchModel] = ..., 
                enclave_role_assignments: Optional[list[RoleAssignmentItem]] = ..., 
                enclave_virtual_network: EnclaveVirtualNetworkModel, 
                governed_service_list: Optional[list[GovernedServiceItem]] = ..., 
                maintenance_mode_configuration: Optional[MaintenanceModeConfigurationPatchModel] = ..., 
                monitoring_settings: Optional[MonitoringSettingsPatchModel] = ..., 
                rbac_inheritance: Optional[Union[str, RbacInheritanceMode]] = ..., 
                workload_resource_visibility: Optional[Union[str, ResourceVisibilityMode]] = ..., 
                workload_role_assignments: Optional[list[RoleAssignmentItem]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.enclave.models.VirtualEnclaveProperties(_Model):
        approval_settings: Optional[VirtualEnclaveApprovalSettings]
        bastion_enabled: Optional[bool]
        community_resource_id: str
        dedicated_hub_resource_id: Optional[str]
        enclave_address_spaces: Optional[EnclaveAddressSpacesModel]
        enclave_default_settings: Optional[EnclaveDefaultSettingsModel]
        enclave_role_assignments: Optional[list[RoleAssignmentItem]]
        enclave_virtual_network: EnclaveVirtualNetworkModel
        governed_service_list: Optional[list[GovernedServiceItem]]
        maintenance_mode_configuration: Optional[MaintenanceModeConfigurationModel]
        managed_on_behalf_of_configuration: Optional[ManagedOnBehalfOfConfiguration]
        managed_resource_group_name: Optional[str]
        monitoring_settings: Optional[MonitoringSettingsModel]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        rbac_inheritance: Optional[Union[str, RbacInheritanceMode]]
        resource_collection: Optional[list[str]]
        workload_resource_visibility: Optional[Union[str, ResourceVisibilityMode]]
        workload_role_assignments: Optional[list[RoleAssignmentItem]]

        @overload
        def __init__(
                self, 
                *, 
                approval_settings: Optional[VirtualEnclaveApprovalSettings] = ..., 
                bastion_enabled: Optional[bool] = ..., 
                community_resource_id: str, 
                dedicated_hub_resource_id: Optional[str] = ..., 
                enclave_default_settings: Optional[EnclaveDefaultSettingsModel] = ..., 
                enclave_role_assignments: Optional[list[RoleAssignmentItem]] = ..., 
                enclave_virtual_network: EnclaveVirtualNetworkModel, 
                governed_service_list: Optional[list[GovernedServiceItem]] = ..., 
                maintenance_mode_configuration: Optional[MaintenanceModeConfigurationModel] = ..., 
                monitoring_settings: Optional[MonitoringSettingsModel] = ..., 
                rbac_inheritance: Optional[Union[str, RbacInheritanceMode]] = ..., 
                workload_resource_visibility: Optional[Union[str, ResourceVisibilityMode]] = ..., 
                workload_role_assignments: Optional[list[RoleAssignmentItem]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.enclave.models.WorkloadPatchModel(_Model):
        properties: Optional[WorkloadPatchProperties]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[WorkloadPatchProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.enclave.models.WorkloadPatchProperties(_Model):
        resource_group_collection: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                resource_group_collection: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.enclave.models.WorkloadProperties(_Model):
        managed_on_behalf_of_configuration: Optional[ManagedOnBehalfOfConfiguration]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        resource_group_collection: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                resource_group_collection: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.enclave.models.WorkloadResource(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[WorkloadProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[WorkloadProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


namespace azure.mgmt.enclave.operations

    class azure.mgmt.enclave.operations.ApprovalOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_uri: str, 
                approval_name: str, 
                resource: ApprovalResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ApprovalResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_uri: str, 
                approval_name: str, 
                resource: ApprovalResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ApprovalResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_uri: str, 
                approval_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ApprovalResource]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_uri: str, 
                approval_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_notify_initiator(
                self, 
                resource_uri: str, 
                approval_name: str, 
                body: ApprovalActionRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ApprovalActionResponse]: ...

        @overload
        def begin_notify_initiator(
                self, 
                resource_uri: str, 
                approval_name: str, 
                body: ApprovalActionRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ApprovalActionResponse]: ...

        @overload
        def begin_notify_initiator(
                self, 
                resource_uri: str, 
                approval_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ApprovalActionResponse]: ...

        @overload
        def begin_update(
                self, 
                resource_uri: str, 
                approval_name: str, 
                properties: ApprovalPatchModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ApprovalResource]: ...

        @overload
        def begin_update(
                self, 
                resource_uri: str, 
                approval_name: str, 
                properties: ApprovalPatchModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ApprovalResource]: ...

        @overload
        def begin_update(
                self, 
                resource_uri: str, 
                approval_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ApprovalResource]: ...

        @distributed_trace
        def get(
                self, 
                resource_uri: str, 
                approval_name: str, 
                **kwargs: Any
            ) -> ApprovalResource: ...

        @distributed_trace
        def list_by_parent(
                self, 
                resource_uri: str, 
                **kwargs: Any
            ) -> ItemPaged[ApprovalResource]: ...


    class azure.mgmt.enclave.operations.CommunityEndpointsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                community_name: str, 
                community_endpoint_name: str, 
                resource: CommunityEndpointResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CommunityEndpointResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                community_name: str, 
                community_endpoint_name: str, 
                resource: CommunityEndpointResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CommunityEndpointResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                community_name: str, 
                community_endpoint_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CommunityEndpointResource]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                community_name: str, 
                community_endpoint_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_handle_approval_creation(
                self, 
                resource_group_name: str, 
                community_name: str, 
                community_endpoint_name: str, 
                body: ApprovalCallbackRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ApprovalActionResponse]: ...

        @overload
        def begin_handle_approval_creation(
                self, 
                resource_group_name: str, 
                community_name: str, 
                community_endpoint_name: str, 
                body: ApprovalCallbackRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ApprovalActionResponse]: ...

        @overload
        def begin_handle_approval_creation(
                self, 
                resource_group_name: str, 
                community_name: str, 
                community_endpoint_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ApprovalActionResponse]: ...

        @overload
        def begin_handle_approval_deletion(
                self, 
                resource_group_name: str, 
                community_name: str, 
                community_endpoint_name: str, 
                body: ApprovalDeletionCallbackRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ApprovalActionResponse]: ...

        @overload
        def begin_handle_approval_deletion(
                self, 
                resource_group_name: str, 
                community_name: str, 
                community_endpoint_name: str, 
                body: ApprovalDeletionCallbackRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ApprovalActionResponse]: ...

        @overload
        def begin_handle_approval_deletion(
                self, 
                resource_group_name: str, 
                community_name: str, 
                community_endpoint_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ApprovalActionResponse]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                community_name: str, 
                community_endpoint_name: str, 
                properties: CommunityEndpointPatchModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CommunityEndpointResource]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                community_name: str, 
                community_endpoint_name: str, 
                properties: CommunityEndpointPatchModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CommunityEndpointResource]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                community_name: str, 
                community_endpoint_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CommunityEndpointResource]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                community_name: str, 
                community_endpoint_name: str, 
                **kwargs: Any
            ) -> CommunityEndpointResource: ...

        @distributed_trace
        def list_by_community_resource(
                self, 
                resource_group_name: str, 
                community_name: str, 
                **kwargs: Any
            ) -> ItemPaged[CommunityEndpointResource]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                community_name: str, 
                **kwargs: Any
            ) -> ItemPaged[CommunityEndpointResource]: ...


    class azure.mgmt.enclave.operations.CommunityOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                community_name: str, 
                resource: CommunityResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CommunityResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                community_name: str, 
                resource: CommunityResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CommunityResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                community_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CommunityResource]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                community_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                community_name: str, 
                properties: CommunityPatchModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CommunityResource]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                community_name: str, 
                properties: CommunityPatchModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CommunityResource]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                community_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CommunityResource]: ...

        @overload
        def check_address_space_availability(
                self, 
                resource_group_name: str, 
                community_name: str, 
                check_address_space_availability_request: CheckAddressSpaceAvailabilityRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckAddressSpaceAvailabilityResponse: ...

        @overload
        def check_address_space_availability(
                self, 
                resource_group_name: str, 
                community_name: str, 
                check_address_space_availability_request: CheckAddressSpaceAvailabilityRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckAddressSpaceAvailabilityResponse: ...

        @overload
        def check_address_space_availability(
                self, 
                resource_group_name: str, 
                community_name: str, 
                check_address_space_availability_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckAddressSpaceAvailabilityResponse: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                community_name: str, 
                **kwargs: Any
            ) -> CommunityResource: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[CommunityResource]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[CommunityResource]: ...


    class azure.mgmt.enclave.operations.DedicatedHubOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                community_name: str, 
                dedicated_hub_name: str, 
                resource: DedicatedHubResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DedicatedHubResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                community_name: str, 
                dedicated_hub_name: str, 
                resource: DedicatedHubResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DedicatedHubResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                community_name: str, 
                dedicated_hub_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DedicatedHubResource]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-11-01-preview', params_added_on={'2025-11-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'community_name', 'dedicated_hub_name']}, api_versions_list=['2025-11-01-preview', '2026-03-01-preview'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                community_name: str, 
                dedicated_hub_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                community_name: str, 
                dedicated_hub_name: str, 
                properties: DedicatedHubPatchModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DedicatedHubResource]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                community_name: str, 
                dedicated_hub_name: str, 
                properties: DedicatedHubPatchModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DedicatedHubResource]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                community_name: str, 
                dedicated_hub_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DedicatedHubResource]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-11-01-preview', params_added_on={'2025-11-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'community_name', 'dedicated_hub_name', 'accept']}, api_versions_list=['2025-11-01-preview', '2026-03-01-preview'])
        def get(
                self, 
                resource_group_name: str, 
                community_name: str, 
                dedicated_hub_name: str, 
                **kwargs: Any
            ) -> DedicatedHubResource: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-11-01-preview', params_added_on={'2025-11-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'community_name', 'accept']}, api_versions_list=['2025-11-01-preview', '2026-03-01-preview'])
        def list_by_community_resource(
                self, 
                resource_group_name: str, 
                community_name: str, 
                **kwargs: Any
            ) -> ItemPaged[DedicatedHubResource]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-11-01-preview', params_added_on={'2025-11-01-preview': ['api_version', 'subscription_id', 'community_name', 'accept']}, api_versions_list=['2025-11-01-preview', '2026-03-01-preview'])
        def list_by_subscription(
                self, 
                community_name: str, 
                **kwargs: Any
            ) -> ItemPaged[DedicatedHubResource]: ...


    class azure.mgmt.enclave.operations.EnclaveConnectionOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                enclave_connection_name: str, 
                resource: EnclaveConnectionResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EnclaveConnectionResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                enclave_connection_name: str, 
                resource: EnclaveConnectionResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EnclaveConnectionResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                enclave_connection_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EnclaveConnectionResource]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                enclave_connection_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_handle_approval_creation(
                self, 
                resource_group_name: str, 
                enclave_connection_name: str, 
                body: ApprovalCallbackRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ApprovalActionResponse]: ...

        @overload
        def begin_handle_approval_creation(
                self, 
                resource_group_name: str, 
                enclave_connection_name: str, 
                body: ApprovalCallbackRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ApprovalActionResponse]: ...

        @overload
        def begin_handle_approval_creation(
                self, 
                resource_group_name: str, 
                enclave_connection_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ApprovalActionResponse]: ...

        @overload
        def begin_handle_approval_deletion(
                self, 
                resource_group_name: str, 
                enclave_connection_name: str, 
                body: ApprovalDeletionCallbackRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ApprovalActionResponse]: ...

        @overload
        def begin_handle_approval_deletion(
                self, 
                resource_group_name: str, 
                enclave_connection_name: str, 
                body: ApprovalDeletionCallbackRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ApprovalActionResponse]: ...

        @overload
        def begin_handle_approval_deletion(
                self, 
                resource_group_name: str, 
                enclave_connection_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ApprovalActionResponse]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                enclave_connection_name: str, 
                properties: EnclaveConnectionPatchModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EnclaveConnectionResource]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                enclave_connection_name: str, 
                properties: EnclaveConnectionPatchModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EnclaveConnectionResource]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                enclave_connection_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EnclaveConnectionResource]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                enclave_connection_name: str, 
                **kwargs: Any
            ) -> EnclaveConnectionResource: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[EnclaveConnectionResource]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[EnclaveConnectionResource]: ...


    class azure.mgmt.enclave.operations.EnclaveEndpointsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                virtual_enclave_name: str, 
                enclave_endpoint_name: str, 
                resource: EnclaveEndpointResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EnclaveEndpointResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                virtual_enclave_name: str, 
                enclave_endpoint_name: str, 
                resource: EnclaveEndpointResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EnclaveEndpointResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                virtual_enclave_name: str, 
                enclave_endpoint_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EnclaveEndpointResource]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                virtual_enclave_name: str, 
                enclave_endpoint_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_handle_approval_creation(
                self, 
                resource_group_name: str, 
                virtual_enclave_name: str, 
                enclave_endpoint_name: str, 
                body: ApprovalCallbackRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ApprovalActionResponse]: ...

        @overload
        def begin_handle_approval_creation(
                self, 
                resource_group_name: str, 
                virtual_enclave_name: str, 
                enclave_endpoint_name: str, 
                body: ApprovalCallbackRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ApprovalActionResponse]: ...

        @overload
        def begin_handle_approval_creation(
                self, 
                resource_group_name: str, 
                virtual_enclave_name: str, 
                enclave_endpoint_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ApprovalActionResponse]: ...

        @overload
        def begin_handle_approval_deletion(
                self, 
                resource_group_name: str, 
                virtual_enclave_name: str, 
                enclave_endpoint_name: str, 
                body: ApprovalDeletionCallbackRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ApprovalActionResponse]: ...

        @overload
        def begin_handle_approval_deletion(
                self, 
                resource_group_name: str, 
                virtual_enclave_name: str, 
                enclave_endpoint_name: str, 
                body: ApprovalDeletionCallbackRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ApprovalActionResponse]: ...

        @overload
        def begin_handle_approval_deletion(
                self, 
                resource_group_name: str, 
                virtual_enclave_name: str, 
                enclave_endpoint_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ApprovalActionResponse]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                virtual_enclave_name: str, 
                enclave_endpoint_name: str, 
                properties: EnclaveEndpointPatchModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EnclaveEndpointResource]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                virtual_enclave_name: str, 
                enclave_endpoint_name: str, 
                properties: EnclaveEndpointPatchModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EnclaveEndpointResource]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                virtual_enclave_name: str, 
                enclave_endpoint_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EnclaveEndpointResource]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                virtual_enclave_name: str, 
                enclave_endpoint_name: str, 
                **kwargs: Any
            ) -> EnclaveEndpointResource: ...

        @distributed_trace
        def list_by_enclave_resource(
                self, 
                resource_group_name: str, 
                virtual_enclave_name: str, 
                **kwargs: Any
            ) -> ItemPaged[EnclaveEndpointResource]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                virtual_enclave_name: str, 
                **kwargs: Any
            ) -> ItemPaged[EnclaveEndpointResource]: ...


    class azure.mgmt.enclave.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


    class azure.mgmt.enclave.operations.TransitHubOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                community_name: str, 
                transit_hub_name: str, 
                resource: TransitHubResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[TransitHubResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                community_name: str, 
                transit_hub_name: str, 
                resource: TransitHubResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[TransitHubResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                community_name: str, 
                transit_hub_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[TransitHubResource]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                community_name: str, 
                transit_hub_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                community_name: str, 
                transit_hub_name: str, 
                properties: TransitHubPatchModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[TransitHubResource]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                community_name: str, 
                transit_hub_name: str, 
                properties: TransitHubPatchModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[TransitHubResource]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                community_name: str, 
                transit_hub_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[TransitHubResource]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                community_name: str, 
                transit_hub_name: str, 
                **kwargs: Any
            ) -> TransitHubResource: ...

        @distributed_trace
        def list_by_community_resource(
                self, 
                resource_group_name: str, 
                community_name: str, 
                **kwargs: Any
            ) -> ItemPaged[TransitHubResource]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                community_name: str, 
                **kwargs: Any
            ) -> ItemPaged[TransitHubResource]: ...


    class azure.mgmt.enclave.operations.VirtualEnclaveOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                virtual_enclave_name: str, 
                resource: EnclaveResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EnclaveResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                virtual_enclave_name: str, 
                resource: EnclaveResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EnclaveResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                virtual_enclave_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EnclaveResource]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                virtual_enclave_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_handle_approval_creation(
                self, 
                resource_group_name: str, 
                virtual_enclave_name: str, 
                body: ApprovalCallbackRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ApprovalActionResponse]: ...

        @overload
        def begin_handle_approval_creation(
                self, 
                resource_group_name: str, 
                virtual_enclave_name: str, 
                body: ApprovalCallbackRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ApprovalActionResponse]: ...

        @overload
        def begin_handle_approval_creation(
                self, 
                resource_group_name: str, 
                virtual_enclave_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ApprovalActionResponse]: ...

        @overload
        def begin_handle_approval_deletion(
                self, 
                resource_group_name: str, 
                virtual_enclave_name: str, 
                body: ApprovalDeletionCallbackRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ApprovalActionResponse]: ...

        @overload
        def begin_handle_approval_deletion(
                self, 
                resource_group_name: str, 
                virtual_enclave_name: str, 
                body: ApprovalDeletionCallbackRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ApprovalActionResponse]: ...

        @overload
        def begin_handle_approval_deletion(
                self, 
                resource_group_name: str, 
                virtual_enclave_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ApprovalActionResponse]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                virtual_enclave_name: str, 
                properties: VirtualEnclavePatchModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EnclaveResource]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                virtual_enclave_name: str, 
                properties: VirtualEnclavePatchModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EnclaveResource]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                virtual_enclave_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EnclaveResource]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                virtual_enclave_name: str, 
                **kwargs: Any
            ) -> EnclaveResource: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[EnclaveResource]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[EnclaveResource]: ...


    class azure.mgmt.enclave.operations.WorkloadOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                virtual_enclave_name: str, 
                workload_name: str, 
                resource: WorkloadResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[WorkloadResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                virtual_enclave_name: str, 
                workload_name: str, 
                resource: WorkloadResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[WorkloadResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                virtual_enclave_name: str, 
                workload_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[WorkloadResource]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                virtual_enclave_name: str, 
                workload_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                virtual_enclave_name: str, 
                workload_name: str, 
                properties: WorkloadPatchModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[WorkloadResource]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                virtual_enclave_name: str, 
                workload_name: str, 
                properties: WorkloadPatchModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[WorkloadResource]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                virtual_enclave_name: str, 
                workload_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[WorkloadResource]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                virtual_enclave_name: str, 
                workload_name: str, 
                **kwargs: Any
            ) -> WorkloadResource: ...

        @distributed_trace
        def list_by_enclave_resource(
                self, 
                resource_group_name: str, 
                virtual_enclave_name: str, 
                **kwargs: Any
            ) -> ItemPaged[WorkloadResource]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                virtual_enclave_name: str, 
                **kwargs: Any
            ) -> ItemPaged[WorkloadResource]: ...


namespace azure.mgmt.enclave.types

    class azure.mgmt.enclave.types.ApprovalActionRequest(TypedDict, total=False):
        key "approvalStatus": Required[Union[Literal["Approved"], Literal["Rejected"], str]]
        approval_status: Union[Literal[Approved], Literal[Rejected], str]


    class azure.mgmt.enclave.types.ApprovalCallbackRequest(TypedDict, total=False):
        key "approvalCallbackPayload": str
        key "approvalStatus": Required[Union[Literal["Approved"], Literal["Rejected"], str]]
        key "resourceRequestAction": Required[Union[Literal["Create"], Literal["Delete"], Literal["Update"], Literal["Reset"], str]]
        approval_callback_payload: str
        approval_status: Union[Literal[Approved], Literal[Rejected], str]
        resource_request_action: Union[Literal[Create], Literal[Delete], Literal[Update], Literal[Reset], str]


    class azure.mgmt.enclave.types.ApprovalDeletionCallbackRequest(TypedDict, total=False):
        key "resourceRequestAction": Required[Union[Literal["Create"], Literal["Delete"], Literal["Update"], str]]
        resource_request_action: Union[Literal[Create], Literal[Delete], Literal[Update], str]


    class azure.mgmt.enclave.types.ApprovalPatchModel(TypedDict, total=False):
        key "properties": ForwardRef('ApprovalPatchProperties', module='types')
        properties: ApprovalPatchProperties


    class azure.mgmt.enclave.types.ApprovalPatchProperties(TypedDict, total=False):
        key "createdAt": str
        key "grandparentResourceId": str
        key "parentResourceId": str
        key "requestMetadata": Required[RequestMetadataUpdatableProperties]
        key "stateChangedAt": str
        key "ticketId": str
        approvers: list[Approver]
        created_at: str
        grandparent_resource_id: str
        parent_resource_id: str
        request_metadata: RequestMetadataUpdatableProperties
        state_changed_at: str
        ticket_id: str


    class azure.mgmt.enclave.types.ApprovalProperties(TypedDict, total=False):
        key "approversApprovedCount": int
        key "createdAt": str
        key "grandparentResourceId": str
        key "mandatoryApproversApprovedCount": int
        key "minimumApproversRequired": int
        key "parentResourceId": str
        key "provisioningState": Union[str, ProvisioningState]
        key "requestMetadata": Required[RequestMetadata]
        key "stateChangedAt": str
        key "ticketId": str
        approvedByEntraIds: list[str]
        approved_by_entra_ids: list[str]
        approvers: list[Approver]
        approvers_approved_count: int
        created_at: str
        grandparent_resource_id: str
        mandatoryApprovers: list[MandatoryApprover]
        mandatory_approvers: list[MandatoryApprover]
        mandatory_approvers_approved_count: int
        minimum_approvers_required: int
        parent_resource_id: str
        provisioning_state: Union[str, ProvisioningState]
        request_metadata: RequestMetadata
        state_changed_at: str
        ticket_id: str


    class azure.mgmt.enclave.types.ApprovalResource(ExtensionResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('ApprovalProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: ApprovalProperties
        system_data: SystemData
        type: str


    class azure.mgmt.enclave.types.ApprovalSettingConfiguration(TypedDict, total=False):
        key "approvalPolicy": Union[str, ApprovalPolicy]
        key "minimumApproversRequired": int
        approval_policy: Union[str, ApprovalPolicy]
        mandatoryApprovers: list[MandatoryApprover]
        mandatory_approvers: list[MandatoryApprover]
        minimum_approvers_required: int


    class azure.mgmt.enclave.types.ApprovalSettings(TypedDict, total=False):
        key "communityEndpointUpdate": ForwardRef('ApprovalSettingConfiguration', module='types')
        key "communityMaintenanceMode": ForwardRef('ApprovalSettingConfiguration', module='types')
        key "connectionCreation": ForwardRef('ApprovalSettingConfiguration', module='types')
        key "connectionUpdate": ForwardRef('ApprovalSettingConfiguration', module='types')
        key "enclaveCreation": ForwardRef('ApprovalSettingConfiguration', module='types')
        key "enclaveEndpointUpdate": ForwardRef('ApprovalSettingConfiguration', module='types')
        key "enclaveMaintenanceMode": ForwardRef('ApprovalSettingConfiguration', module='types')
        community_endpoint_update: ApprovalSettingConfiguration
        community_maintenance_mode: ApprovalSettingConfiguration
        connection_creation: ApprovalSettingConfiguration
        connection_update: ApprovalSettingConfiguration
        enclave_creation: ApprovalSettingConfiguration
        enclave_endpoint_update: ApprovalSettingConfiguration
        enclave_maintenance_mode: ApprovalSettingConfiguration


    class azure.mgmt.enclave.types.ApprovalSettingsPatchProperties(TypedDict, total=False):
        key "communityEndpointUpdate": ForwardRef('ApprovalSettingConfiguration', module='types')
        key "communityMaintenanceMode": ForwardRef('ApprovalSettingConfiguration', module='types')
        key "connectionCreation": ForwardRef('ApprovalSettingConfiguration', module='types')
        key "connectionUpdate": ForwardRef('ApprovalSettingConfiguration', module='types')
        key "enclaveCreation": ForwardRef('ApprovalSettingConfiguration', module='types')
        key "enclaveEndpointUpdate": ForwardRef('ApprovalSettingConfiguration', module='types')
        key "enclaveMaintenanceMode": ForwardRef('ApprovalSettingConfiguration', module='types')
        community_endpoint_update: ApprovalSettingConfiguration
        community_maintenance_mode: ApprovalSettingConfiguration
        connection_creation: ApprovalSettingConfiguration
        connection_update: ApprovalSettingConfiguration
        enclave_creation: ApprovalSettingConfiguration
        enclave_endpoint_update: ApprovalSettingConfiguration
        enclave_maintenance_mode: ApprovalSettingConfiguration


    class azure.mgmt.enclave.types.Approver(TypedDict, total=False):
        key "actionPerformed": Union[str, ActionPerformed]
        key "approverEntraId": Required[str]
        key "lastUpdatedAt": Required[str]
        action_performed: Union[str, ActionPerformed]
        approver_entra_id: str
        last_updated_at: str
        mandatoryApprovalGroupMembershipIds: list[str]
        mandatory_approval_group_membership_ids: list[str]


    class azure.mgmt.enclave.types.CheckAddressSpaceAvailabilityRequest(TypedDict, total=False):
        key "communityResourceId": Required[str]
        key "enclaveVirtualNetwork": Required[EnclaveVirtualNetworkModel]
        community_resource_id: str
        enclave_virtual_network: EnclaveVirtualNetworkModel


    class azure.mgmt.enclave.types.CommunityEndpointDestinationRule(TypedDict, total=False):
        key "destination": str
        key "destinationType": Union[str, DestinationType]
        key "endpointRuleName": str
        key "ports": str
        key "transitHubResourceId": str
        destination: str
        destination_type: Union[str, DestinationType]
        endpoint_rule_name: str
        ports: str
        protocols: list[Union[str, CommunityEndpointProtocol]]
        transit_hub_resource_id: str


    class azure.mgmt.enclave.types.CommunityEndpointPatchModel(TypedDict, total=False):
        key "properties": ForwardRef('CommunityEndpointPatchProperties', module='types')
        properties: CommunityEndpointPatchProperties
        tags: dict[str, str]


    class azure.mgmt.enclave.types.CommunityEndpointPatchProperties(TypedDict, total=False):
        key "ruleCollection": Required[list[CommunityEndpointDestinationRule]]
        key "updateMode": Union[str, UpdateMode]
        rule_collection: list[CommunityEndpointDestinationRule]
        update_mode: Union[str, UpdateMode]


    class azure.mgmt.enclave.types.CommunityEndpointProperties(TypedDict, total=False):
        key "provisioningState": Union[str, ProvisioningState]
        key "ruleCollection": Required[list[CommunityEndpointDestinationRule]]
        key "updateMode": Union[str, UpdateMode]
        provisioning_state: Union[str, ProvisioningState]
        resourceCollection: list[str]
        resource_collection: list[str]
        rule_collection: list[CommunityEndpointDestinationRule]
        update_mode: Union[str, UpdateMode]


    class azure.mgmt.enclave.types.CommunityEndpointResource(TrackedResource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('CommunityEndpointProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: CommunityEndpointProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.enclave.types.CommunityPatchModel(TypedDict, total=False):
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        key "properties": ForwardRef('CommunityPatchProperties', module='types')
        identity: ManagedServiceIdentity
        properties: CommunityPatchProperties
        tags: dict[str, str]


    class azure.mgmt.enclave.types.CommunityPatchProperties(TypedDict, total=False):
        key "approvalSettings": ForwardRef('ApprovalSettingsPatchProperties', module='types')
        key "firewallSku": Union[str, FirewallSKU]
        key "maintenanceModeConfiguration": ForwardRef('MaintenanceModeConfigurationPatchModel', module='types')
        key "monitoringSettings": ForwardRef('MonitoringSettingsPatchModel', module='types')
        key "policyOverride": Union[Literal["Enclave"], Literal["None"], str]
        addressSpaces: list[str]
        address_spaces: list[str]
        communityRoleAssignments: list[RoleAssignmentItem]
        community_role_assignments: list[RoleAssignmentItem]
        dnsServers: list[str]
        dns_servers: list[str]
        firewall_sku: Union[str, FirewallSKU]
        governedServiceList: list[GovernedServiceItem]
        governed_service_list: list[GovernedServiceItem]
        granular_approval_settings: ApprovalSettingsPatchProperties
        maintenance_mode_configuration: MaintenanceModeConfigurationPatchModel
        monitoring_settings: MonitoringSettingsPatchModel
        policy_override: Union[Literal[Enclave], Literal[None], str]


    class azure.mgmt.enclave.types.CommunityProperties(TypedDict, total=False):
        key "addressSpace": str
        key "approvalSettings": ForwardRef('ApprovalSettings', module='types')
        key "firewallSku": Union[str, FirewallSKU]
        key "maintenanceModeConfiguration": ForwardRef('MaintenanceModeConfigurationModel', module='types')
        key "managedOnBehalfOfConfiguration": ForwardRef('ManagedOnBehalfOfConfiguration', module='types')
        key "managedResourceGroupName": str
        key "monitoringSettings": ForwardRef('MonitoringSettingsModel', module='types')
        key "policyOverride": Union[Literal["Enclave"], Literal["None"], str]
        key "provisioningState": Union[str, ProvisioningState]
        addressSpaces: list[str]
        address_space: str
        address_spaces: list[str]
        communityRoleAssignments: list[RoleAssignmentItem]
        community_role_assignments: list[RoleAssignmentItem]
        dedicatedHubList: list[DedicatedHubResource]
        dedicated_hub_list: list[DedicatedHubResource]
        dnsServers: list[str]
        dns_servers: list[str]
        firewall_sku: Union[str, FirewallSKU]
        governedServiceList: list[GovernedServiceItem]
        governed_service_list: list[GovernedServiceItem]
        granular_approval_settings: ApprovalSettings
        maintenance_mode_configuration: MaintenanceModeConfigurationModel
        managed_on_behalf_of_configuration: ManagedOnBehalfOfConfiguration
        managed_resource_group_name: str
        monitoring_settings: MonitoringSettingsModel
        policy_override: Union[Literal[Enclave], Literal[None], str]
        provisioning_state: Union[str, ProvisioningState]
        resourceCollection: list[str]
        resource_collection: list[str]


    class azure.mgmt.enclave.types.CommunityResource(TrackedResource):
        key "id": str
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('CommunityProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        identity: ManagedServiceIdentity
        location: str
        name: str
        properties: CommunityProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.enclave.types.DedicatedHubPatchModel(TypedDict, total=False):
        key "properties": ForwardRef('DedicatedHubPatchProperties', module='types')
        properties: DedicatedHubPatchProperties
        tags: dict[str, str]


    class azure.mgmt.enclave.types.DedicatedHubPatchProperties(TypedDict, total=False):
        key "designation": Union[str, Designation]
        designation: Union[str, Designation]


    class azure.mgmt.enclave.types.DedicatedHubProperties(TypedDict, total=False):
        key "designation": Union[str, Designation]
        key "firewallPolicyResourceId": str
        key "firewallResourceId": str
        key "provisioningState": Union[str, ProvisioningState]
        key "vHubResourceId": str
        designation: Union[str, Designation]
        firewall_policy_resource_id: str
        firewall_resource_id: str
        provisioning_state: Union[str, ProvisioningState]
        v_hub_resource_id: str


    class azure.mgmt.enclave.types.DedicatedHubResource(TrackedResource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('DedicatedHubProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: DedicatedHubProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.enclave.types.EnclaveAddressSpacesModel(TypedDict, total=False):
        key "enclaveAddressSpace": str
        key "managedAddressSpace": str
        enclave_address_space: str
        managed_address_space: str


    class azure.mgmt.enclave.types.EnclaveConnectionPatchModel(TypedDict, total=False):
        key "properties": ForwardRef('EnclaveConnectionPatchProperties', module='types')
        properties: EnclaveConnectionPatchProperties
        tags: dict[str, str]


    class azure.mgmt.enclave.types.EnclaveConnectionPatchProperties(TypedDict, total=False):
        key "sourceCidr": str
        source_cidr: str


    class azure.mgmt.enclave.types.EnclaveConnectionProperties(TypedDict, total=False):
        key "communityResourceId": Required[str]
        key "destinationEndpointId": Required[str]
        key "provisioningState": Union[str, ProvisioningState]
        key "sourceCidr": str
        key "sourceResourceId": Required[str]
        key "state": Union[str, EnclaveConnectionState]
        key "updateMode": Union[str, UpdateMode]
        community_resource_id: str
        destination_endpoint_id: str
        provisioning_state: Union[str, ProvisioningState]
        resourceCollection: list[str]
        resource_collection: list[str]
        source_cidr: str
        source_resource_id: str
        state: Union[str, EnclaveConnectionState]
        update_mode: Union[str, UpdateMode]


    class azure.mgmt.enclave.types.EnclaveConnectionResource(TrackedResource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('EnclaveConnectionProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: EnclaveConnectionProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.enclave.types.EnclaveDefaultSettingsModel(TypedDict, total=False):
        key "diagnosticDestination": Union[str, DiagnosticDestination]
        key "keyVaultResourceId": str
        key "storageAccountResourceId": str
        diagnostic_destination: Union[str, DiagnosticDestination]
        key_vault_resource_id: str
        logAnalyticsResourceIdCollection: list[str]
        log_analytics_resource_id_collection: list[str]
        storage_account_resource_id: str


    class azure.mgmt.enclave.types.EnclaveDefaultSettingsPatchModel(TypedDict, total=False):
        key "diagnosticDestination": Union[str, DiagnosticDestination]
        diagnostic_destination: Union[str, DiagnosticDestination]


    class azure.mgmt.enclave.types.EnclaveEndpointDestinationRule(TypedDict, total=False):
        key "destination": str
        key "endpointRuleName": str
        key "ports": str
        destination: str
        endpoint_rule_name: str
        ports: str
        protocols: list[Union[str, EnclaveEndpointProtocol]]


    class azure.mgmt.enclave.types.EnclaveEndpointPatchModel(TypedDict, total=False):
        key "properties": ForwardRef('EnclaveEndpointPatchProperties', module='types')
        properties: EnclaveEndpointPatchProperties
        tags: dict[str, str]


    class azure.mgmt.enclave.types.EnclaveEndpointPatchProperties(TypedDict, total=False):
        key "ruleCollection": Required[list[EnclaveEndpointDestinationRule]]
        key "updateMode": Union[str, UpdateMode]
        rule_collection: list[EnclaveEndpointDestinationRule]
        update_mode: Union[str, UpdateMode]


    class azure.mgmt.enclave.types.EnclaveEndpointProperties(TypedDict, total=False):
        key "provisioningState": Union[str, ProvisioningState]
        key "ruleCollection": Required[list[EnclaveEndpointDestinationRule]]
        key "updateMode": Union[str, UpdateMode]
        provisioning_state: Union[str, ProvisioningState]
        resourceCollection: list[str]
        resource_collection: list[str]
        rule_collection: list[EnclaveEndpointDestinationRule]
        update_mode: Union[str, UpdateMode]


    class azure.mgmt.enclave.types.EnclaveEndpointResource(TrackedResource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('EnclaveEndpointProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: EnclaveEndpointProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.enclave.types.EnclaveResource(TrackedResource):
        key "id": str
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('VirtualEnclaveProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        identity: ManagedServiceIdentity
        location: str
        name: str
        properties: VirtualEnclaveProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.enclave.types.EnclaveVirtualNetworkModel(TypedDict, total=False):
        key "allowSubnetCommunication": bool
        key "customCidrRange": str
        key "networkName": str
        key "networkSize": str
        allow_subnet_communication: bool
        custom_cidr_range: str
        network_name: str
        network_size: str
        subnetConfigurations: list[SubnetConfiguration]
        subnet_configurations: list[SubnetConfiguration]


    class azure.mgmt.enclave.types.ExtensionResource(Resource):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.enclave.types.GovernedServiceItem(TypedDict, total=False):
        key "enforcement": Union[Literal["Enabled"], Literal["Disabled"], str]
        key "option": Union[Literal["Allow"], Literal["Deny"], Literal["ExceptionOnly"], Literal["NotApplicable"], str]
        key "policyAction": Union[Literal["AuditOnly"], Literal["Enforce"], Literal["None"], str]
        key "serviceId": Required[Union[str, ServiceIdentifier]]
        key "serviceName": str
        enforcement: Union[Literal[Enabled], Literal[Disabled], str]
        initiatives: list[str]
        option: Union[Literal[Allow], Literal[Deny], Literal[ExceptionOnly], Literal[NotApplicable], str]
        policy_action: Union[Literal[AuditOnly], Literal[Enforce], Literal[None], str]
        service_id: Union[str, ServiceIdentifier]
        service_name: str


    class azure.mgmt.enclave.types.MaintenanceModeConfigurationModel(TypedDict, total=False):
        key "justification": Union[Literal["Networking"], Literal["Governance"], Literal["Off"], str]
        key "mode": Required[Union[Literal["On"], Literal["CanNotDelete"], Literal["Off"], Literal["General"], Literal["Advanced"], str]]
        justification: Union[Literal[Networking], Literal[Governance], Literal[Off], str]
        mode: Union[Literal[On], Literal[CanNotDelete], Literal[Off], Literal[General], Literal[Advanced], str]
        principals: list[Principal]


    class azure.mgmt.enclave.types.MaintenanceModeConfigurationPatchModel(TypedDict, total=False):
        key "justification": Union[Literal["Networking"], Literal["Governance"], Literal["Off"], str]
        key "mode": Required[Union[Literal["On"], Literal["CanNotDelete"], Literal["Off"], Literal["General"], Literal["Advanced"], str]]
        justification: Union[Literal[Networking], Literal[Governance], Literal[Off], str]
        mode: Union[Literal[On], Literal[CanNotDelete], Literal[Off], Literal[General], Literal[Advanced], str]
        principals: list[Principal]


    class azure.mgmt.enclave.types.ManagedOnBehalfOfConfiguration(TypedDict, total=False):
        moboBrokerResources: list[MoboBrokerResource]
        mobo_broker_resources: list[MoboBrokerResource]


    class azure.mgmt.enclave.types.ManagedServiceIdentity(TypedDict, total=False):
        key "principalId": str
        key "tenantId": str
        key "type": Required[Union[str, ManagedServiceIdentityType]]
        principal_id: str
        tenant_id: str
        type: Union[str, ManagedServiceIdentityType]
        userAssignedIdentities: dict[str, UserAssignedIdentity]
        user_assigned_identities: dict[str, UserAssignedIdentity]


    class azure.mgmt.enclave.types.MandatoryApprover(TypedDict, total=False):
        key "approverEntraId": Required[str]
        approver_entra_id: str


    class azure.mgmt.enclave.types.MoboBrokerResource(TypedDict, total=False):
        key "id": str
        id: str


    class azure.mgmt.enclave.types.MonitoringDestination(TypedDict, total=False):
        key "customWorkspaceResourceId": str
        key "destinationType": Required[Union[str, MonitoringDestinationType]]
        key "diagnosticSettingsName": str
        custom_workspace_resource_id: str
        destination_type: Union[str, MonitoringDestinationType]
        diagnostic_settings_name: str


    class azure.mgmt.enclave.types.MonitoringDestinationPatchModel(TypedDict, total=False):
        key "customWorkspaceResourceId": str
        key "destinationType": Required[Union[str, MonitoringDestinationType]]
        key "diagnosticSettingsName": str
        custom_workspace_resource_id: str
        destination_type: Union[str, MonitoringDestinationType]
        diagnostic_settings_name: str


    class azure.mgmt.enclave.types.MonitoringSettingsModel(TypedDict, total=False):
        key "flowLogDestination": ForwardRef('MonitoringDestination', module='types')
        diagnosticDestinations: list[MonitoringDestination]
        diagnostic_destinations: list[MonitoringDestination]
        flow_log_destination: MonitoringDestination


    class azure.mgmt.enclave.types.MonitoringSettingsPatchModel(TypedDict, total=False):
        key "flowLogDestination": ForwardRef('MonitoringDestinationPatchModel', module='types')
        diagnosticDestinations: list[MonitoringDestinationPatchModel]
        diagnostic_destinations: list[MonitoringDestinationPatchModel]
        flow_log_destination: MonitoringDestinationPatchModel


    class azure.mgmt.enclave.types.Principal(TypedDict, total=False):
        key "id": Required[str]
        key "type": Required[Union[Literal["User"], Literal["Group"], Literal["ServicePrincipal"], str]]
        id: str
        type: Union[Literal[User], Literal[Group], Literal[ServicePrincipal], str]


    class azure.mgmt.enclave.types.RequestMetadata(TypedDict, total=False):
        key "approvalCallbackPayload": str
        key "approvalCallbackRoute": str
        key "approvalStatus": Union[str, ApprovalStatus]
        key "resourceAction": Required[str]
        approval_callback_payload: str
        approval_callback_route: str
        approval_status: Union[str, ApprovalStatus]
        resource_action: str


    class azure.mgmt.enclave.types.RequestMetadataUpdatableProperties(TypedDict, total=False):
        key "approvalCallbackPayload": str
        key "approvalCallbackRoute": str
        key "approvalStatus": Union[str, ApprovalStatus]
        key "resourceAction": Required[str]
        approval_callback_payload: str
        approval_callback_route: str
        approval_status: Union[str, ApprovalStatus]
        resource_action: str


    class azure.mgmt.enclave.types.Resource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.enclave.types.RoleAssignmentItem(TypedDict, total=False):
        key "condition": str
        key "roleDefinitionId": Required[str]
        condition: str
        principals: list[Principal]
        role_definition_id: str


    class azure.mgmt.enclave.types.SubnetConfiguration(TypedDict, total=False):
        key "addressPrefix": str
        key "networkPrefixSize": Required[int]
        key "networkSecurityGroupResourceId": str
        key "subnetDelegation": str
        key "subnetName": Required[str]
        key "subnetResourceId": str
        address_prefix: str
        network_prefix_size: int
        network_security_group_resource_id: str
        subnet_delegation: str
        subnet_name: str
        subnet_resource_id: str


    class azure.mgmt.enclave.types.SystemData(TypedDict, total=False):
        key "createdAt": str
        key "createdBy": str
        key "createdByType": Union[str, CreatedByType]
        key "lastModifiedAt": str
        key "lastModifiedBy": str
        key "lastModifiedByType": Union[str, CreatedByType]
        created_at: str
        created_by: str
        created_by_type: Union[str, CreatedByType]
        last_modified_at: str
        last_modified_by: str
        last_modified_by_type: Union[str, CreatedByType]


    class azure.mgmt.enclave.types.TrackedResource(Resource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.enclave.types.TransitHubPatchModel(TypedDict, total=False):
        key "properties": ForwardRef('TransitHubPatchProperties', module='types')
        properties: TransitHubPatchProperties
        tags: dict[str, str]


    class azure.mgmt.enclave.types.TransitHubPatchProperties(TypedDict, total=False):
        key "securityProvider": Union[str, SecurityProvider]
        key "state": Union[str, TransitHubState]
        key "transitOption": ForwardRef('TransitOption', module='types')
        security_provider: Union[str, SecurityProvider]
        state: Union[str, TransitHubState]
        transit_option: TransitOption


    class azure.mgmt.enclave.types.TransitHubProperties(TypedDict, total=False):
        key "provisioningState": Union[str, ProvisioningState]
        key "securityProvider": Union[str, SecurityProvider]
        key "state": Union[str, TransitHubState]
        key "transitOption": ForwardRef('TransitOption', module='types')
        provisioning_state: Union[str, ProvisioningState]
        resourceCollection: list[str]
        resource_collection: list[str]
        security_provider: Union[str, SecurityProvider]
        state: Union[str, TransitHubState]
        transit_option: TransitOption


    class azure.mgmt.enclave.types.TransitHubResource(TrackedResource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('TransitHubProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: TransitHubProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.enclave.types.TransitOption(TypedDict, total=False):
        key "params": ForwardRef('TransitOptionParams', module='types')
        key "type": Union[str, TransitOptionType]
        params: TransitOptionParams
        type: Union[str, TransitOptionType]


    class azure.mgmt.enclave.types.TransitOptionParams(TypedDict, total=False):
        key "remoteVirtualNetworkId": str
        key "scaleUnits": int
        remote_virtual_network_id: str
        scale_units: int


    class azure.mgmt.enclave.types.UserAssignedIdentity(TypedDict, total=False):
        key "clientId": str
        key "principalId": str
        client_id: str
        principal_id: str


    class azure.mgmt.enclave.types.VirtualEnclaveApprovalSettings(TypedDict, total=False):
        key "connectionCreation": ForwardRef('ApprovalSettingConfiguration', module='types')
        key "connectionUpdate": ForwardRef('ApprovalSettingConfiguration', module='types')
        key "enclaveEndpointUpdate": ForwardRef('ApprovalSettingConfiguration', module='types')
        key "enclaveMaintenanceMode": ForwardRef('ApprovalSettingConfiguration', module='types')
        connection_creation: ApprovalSettingConfiguration
        connection_update: ApprovalSettingConfiguration
        enclave_endpoint_update: ApprovalSettingConfiguration
        enclave_maintenance_mode: ApprovalSettingConfiguration


    class azure.mgmt.enclave.types.VirtualEnclaveApprovalSettingsPatchProperties(TypedDict, total=False):
        key "connectionCreation": ForwardRef('ApprovalSettingConfiguration', module='types')
        key "connectionUpdate": ForwardRef('ApprovalSettingConfiguration', module='types')
        key "enclaveEndpointUpdate": ForwardRef('ApprovalSettingConfiguration', module='types')
        key "enclaveMaintenanceMode": ForwardRef('ApprovalSettingConfiguration', module='types')
        connection_creation: ApprovalSettingConfiguration
        connection_update: ApprovalSettingConfiguration
        enclave_endpoint_update: ApprovalSettingConfiguration
        enclave_maintenance_mode: ApprovalSettingConfiguration


    class azure.mgmt.enclave.types.VirtualEnclavePatchModel(TypedDict, total=False):
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        key "properties": ForwardRef('VirtualEnclavePatchProperties', module='types')
        identity: ManagedServiceIdentity
        properties: VirtualEnclavePatchProperties
        tags: dict[str, str]


    class azure.mgmt.enclave.types.VirtualEnclavePatchProperties(TypedDict, total=False):
        key "approvalSettings": ForwardRef('VirtualEnclaveApprovalSettingsPatchProperties', module='types')
        key "bastionEnabled": bool
        key "dedicatedHubResourceId": str
        key "enclaveDefaultSettings": ForwardRef('EnclaveDefaultSettingsPatchModel', module='types')
        key "enclaveVirtualNetwork": Required[EnclaveVirtualNetworkModel]
        key "maintenanceModeConfiguration": ForwardRef('MaintenanceModeConfigurationPatchModel', module='types')
        key "monitoringSettings": ForwardRef('MonitoringSettingsPatchModel', module='types')
        key "rbacInheritance": Union[str, RbacInheritanceMode]
        key "workloadResourceVisibility": Union[str, ResourceVisibilityMode]
        approval_settings: VirtualEnclaveApprovalSettingsPatchProperties
        bastion_enabled: bool
        dedicated_hub_resource_id: str
        enclaveRoleAssignments: list[RoleAssignmentItem]
        enclave_default_settings: EnclaveDefaultSettingsPatchModel
        enclave_role_assignments: list[RoleAssignmentItem]
        enclave_virtual_network: EnclaveVirtualNetworkModel
        governedServiceList: list[GovernedServiceItem]
        governed_service_list: list[GovernedServiceItem]
        maintenance_mode_configuration: MaintenanceModeConfigurationPatchModel
        monitoring_settings: MonitoringSettingsPatchModel
        rbac_inheritance: Union[str, RbacInheritanceMode]
        workloadRoleAssignments: list[RoleAssignmentItem]
        workload_resource_visibility: Union[str, ResourceVisibilityMode]
        workload_role_assignments: list[RoleAssignmentItem]


    class azure.mgmt.enclave.types.VirtualEnclaveProperties(TypedDict, total=False):
        key "approvalSettings": ForwardRef('VirtualEnclaveApprovalSettings', module='types')
        key "bastionEnabled": bool
        key "communityResourceId": Required[str]
        key "dedicatedHubResourceId": str
        key "enclaveAddressSpaces": ForwardRef('EnclaveAddressSpacesModel', module='types')
        key "enclaveDefaultSettings": ForwardRef('EnclaveDefaultSettingsModel', module='types')
        key "enclaveVirtualNetwork": Required[EnclaveVirtualNetworkModel]
        key "maintenanceModeConfiguration": ForwardRef('MaintenanceModeConfigurationModel', module='types')
        key "managedOnBehalfOfConfiguration": ForwardRef('ManagedOnBehalfOfConfiguration', module='types')
        key "managedResourceGroupName": str
        key "monitoringSettings": ForwardRef('MonitoringSettingsModel', module='types')
        key "provisioningState": Union[str, ProvisioningState]
        key "rbacInheritance": Union[str, RbacInheritanceMode]
        key "workloadResourceVisibility": Union[str, ResourceVisibilityMode]
        approval_settings: VirtualEnclaveApprovalSettings
        bastion_enabled: bool
        community_resource_id: str
        dedicated_hub_resource_id: str
        enclaveRoleAssignments: list[RoleAssignmentItem]
        enclave_address_spaces: EnclaveAddressSpacesModel
        enclave_default_settings: EnclaveDefaultSettingsModel
        enclave_role_assignments: list[RoleAssignmentItem]
        enclave_virtual_network: EnclaveVirtualNetworkModel
        governedServiceList: list[GovernedServiceItem]
        governed_service_list: list[GovernedServiceItem]
        maintenance_mode_configuration: MaintenanceModeConfigurationModel
        managed_on_behalf_of_configuration: ManagedOnBehalfOfConfiguration
        managed_resource_group_name: str
        monitoring_settings: MonitoringSettingsModel
        provisioning_state: Union[str, ProvisioningState]
        rbac_inheritance: Union[str, RbacInheritanceMode]
        resourceCollection: list[str]
        resource_collection: list[str]
        workloadRoleAssignments: list[RoleAssignmentItem]
        workload_resource_visibility: Union[str, ResourceVisibilityMode]
        workload_role_assignments: list[RoleAssignmentItem]


    class azure.mgmt.enclave.types.WorkloadPatchModel(TypedDict, total=False):
        key "properties": ForwardRef('WorkloadPatchProperties', module='types')
        properties: WorkloadPatchProperties
        tags: dict[str, str]


    class azure.mgmt.enclave.types.WorkloadPatchProperties(TypedDict, total=False):
        resourceGroupCollection: list[str]
        resource_group_collection: list[str]


    class azure.mgmt.enclave.types.WorkloadProperties(TypedDict, total=False):
        key "managedOnBehalfOfConfiguration": ForwardRef('ManagedOnBehalfOfConfiguration', module='types')
        key "provisioningState": Union[str, ProvisioningState]
        managed_on_behalf_of_configuration: ManagedOnBehalfOfConfiguration
        provisioning_state: Union[str, ProvisioningState]
        resourceGroupCollection: list[str]
        resource_group_collection: list[str]


    class azure.mgmt.enclave.types.WorkloadResource(TrackedResource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('WorkloadProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: WorkloadProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str


```