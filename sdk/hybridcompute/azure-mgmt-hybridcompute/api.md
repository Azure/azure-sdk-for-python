```py
namespace azure.mgmt.hybridcompute

    class azure.mgmt.hybridcompute.HybridComputeManagementClient(_HybridComputeManagementClientOperationsMixin): implements ContextManager 
        extension_metadata: ExtensionMetadataOperations
        extension_metadata_v2: ExtensionMetadataV2Operations
        extension_publisher: ExtensionPublisherOperations
        extension_type: ExtensionTypeOperations
        gateways: GatewaysOperations
        license_profiles: LicenseProfilesOperations
        licenses: LicensesOperations
        machine_extensions: MachineExtensionsOperations
        machine_run_commands: MachineRunCommandsOperations
        machines: MachinesOperations
        network_profile: NetworkProfileOperations
        network_security_perimeter_configurations: NetworkSecurityPerimeterConfigurationsOperations
        operations: Operations
        private_endpoint_connections: PrivateEndpointConnectionsOperations
        private_link_resources: PrivateLinkResourcesOperations
        private_link_scopes: PrivateLinkScopesOperations
        settings: SettingsOperations

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

        @overload
        def begin_setup_extensions(
                self, 
                resource_group_name: str, 
                machine_name: str, 
                extensions: SetupExtensionRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SetupExtensionRequest]: ...

        @overload
        def begin_setup_extensions(
                self, 
                resource_group_name: str, 
                machine_name: str, 
                extensions: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SetupExtensionRequest]: ...

        @overload
        def begin_setup_extensions(
                self, 
                resource_group_name: str, 
                machine_name: str, 
                extensions: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SetupExtensionRequest]: ...

        @overload
        def begin_upgrade_extensions(
                self, 
                resource_group_name: str, 
                machine_name: str, 
                extension_upgrade_parameters: MachineExtensionUpgrade, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_upgrade_extensions(
                self, 
                resource_group_name: str, 
                machine_name: str, 
                extension_upgrade_parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_upgrade_extensions(
                self, 
                resource_group_name: str, 
                machine_name: str, 
                extension_upgrade_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        def close(self) -> None: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> HttpResponse: ...


namespace azure.mgmt.hybridcompute.aio

    class azure.mgmt.hybridcompute.aio.HybridComputeManagementClient(_HybridComputeManagementClientOperationsMixin): implements AsyncContextManager 
        extension_metadata: ExtensionMetadataOperations
        extension_metadata_v2: ExtensionMetadataV2Operations
        extension_publisher: ExtensionPublisherOperations
        extension_type: ExtensionTypeOperations
        gateways: GatewaysOperations
        license_profiles: LicenseProfilesOperations
        licenses: LicensesOperations
        machine_extensions: MachineExtensionsOperations
        machine_run_commands: MachineRunCommandsOperations
        machines: MachinesOperations
        network_profile: NetworkProfileOperations
        network_security_perimeter_configurations: NetworkSecurityPerimeterConfigurationsOperations
        operations: Operations
        private_endpoint_connections: PrivateEndpointConnectionsOperations
        private_link_resources: PrivateLinkResourcesOperations
        private_link_scopes: PrivateLinkScopesOperations
        settings: SettingsOperations

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

        @overload
        async def begin_setup_extensions(
                self, 
                resource_group_name: str, 
                machine_name: str, 
                extensions: SetupExtensionRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SetupExtensionRequest]: ...

        @overload
        async def begin_setup_extensions(
                self, 
                resource_group_name: str, 
                machine_name: str, 
                extensions: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SetupExtensionRequest]: ...

        @overload
        async def begin_setup_extensions(
                self, 
                resource_group_name: str, 
                machine_name: str, 
                extensions: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SetupExtensionRequest]: ...

        @overload
        async def begin_upgrade_extensions(
                self, 
                resource_group_name: str, 
                machine_name: str, 
                extension_upgrade_parameters: MachineExtensionUpgrade, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_upgrade_extensions(
                self, 
                resource_group_name: str, 
                machine_name: str, 
                extension_upgrade_parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_upgrade_extensions(
                self, 
                resource_group_name: str, 
                machine_name: str, 
                extension_upgrade_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        async def close(self) -> None: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> Awaitable[AsyncHttpResponse]: ...


namespace azure.mgmt.hybridcompute.aio.operations

    class azure.mgmt.hybridcompute.aio.operations.ExtensionMetadataOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                location: str, 
                publisher: str, 
                extension_type: str, 
                version: str, 
                **kwargs: Any
            ) -> ExtensionValue: ...

        @distributed_trace
        def list(
                self, 
                location: str, 
                publisher: str, 
                extension_type: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ExtensionValue]: ...


    class azure.mgmt.hybridcompute.aio.operations.ExtensionMetadataV2Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                location: str, 
                publisher: str, 
                extension_type: str, 
                version: str, 
                **kwargs: Any
            ) -> ExtensionValueV2: ...

        @distributed_trace
        def list(
                self, 
                location: str, 
                publisher: str, 
                extension_type: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ExtensionValueV2]: ...


    class azure.mgmt.hybridcompute.aio.operations.ExtensionPublisherOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                location: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ExtensionPublisher]: ...


    class azure.mgmt.hybridcompute.aio.operations.ExtensionTypeOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                location: str, 
                publisher: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ExtensionType]: ...


    class azure.mgmt.hybridcompute.aio.operations.GatewaysOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                gateway_name: str, 
                parameters: Gateway, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Gateway]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                gateway_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Gateway]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                gateway_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Gateway]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                gateway_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                gateway_name: str, 
                **kwargs: Any
            ) -> Gateway: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Gateway]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[Gateway]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                gateway_name: str, 
                parameters: GatewayUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Gateway: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                gateway_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Gateway: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                gateway_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Gateway: ...


    class azure.mgmt.hybridcompute.aio.operations.LicenseProfilesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                machine_name: str, 
                parameters: LicenseProfile, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[LicenseProfile]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                machine_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[LicenseProfile]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                machine_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[LicenseProfile]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                machine_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                machine_name: str, 
                parameters: LicenseProfileUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[LicenseProfile]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                machine_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[LicenseProfile]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                machine_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[LicenseProfile]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                machine_name: str, 
                **kwargs: Any
            ) -> LicenseProfile: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                machine_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[LicenseProfile]: ...


    class azure.mgmt.hybridcompute.aio.operations.LicensesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                license_name: str, 
                parameters: License, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[License]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                license_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[License]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                license_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[License]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                license_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                license_name: str, 
                parameters: LicenseUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[License]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                license_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[License]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                license_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[License]: ...

        @overload
        async def begin_validate_license(
                self, 
                parameters: License, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[License]: ...

        @overload
        async def begin_validate_license(
                self, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[License]: ...

        @overload
        async def begin_validate_license(
                self, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[License]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                license_name: str, 
                **kwargs: Any
            ) -> License: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[License]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[License]: ...


    class azure.mgmt.hybridcompute.aio.operations.MachineExtensionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                machine_name: str, 
                extension_name: str, 
                extension_parameters: MachineExtension, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MachineExtension]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                machine_name: str, 
                extension_name: str, 
                extension_parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MachineExtension]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                machine_name: str, 
                extension_name: str, 
                extension_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MachineExtension]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                machine_name: str, 
                extension_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                machine_name: str, 
                extension_name: str, 
                extension_parameters: MachineExtensionUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MachineExtension]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                machine_name: str, 
                extension_name: str, 
                extension_parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MachineExtension]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                machine_name: str, 
                extension_name: str, 
                extension_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MachineExtension]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                machine_name: str, 
                extension_name: str, 
                **kwargs: Any
            ) -> MachineExtension: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                machine_name: str, 
                *, 
                expand: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[MachineExtension]: ...


    class azure.mgmt.hybridcompute.aio.operations.MachineRunCommandsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                machine_name: str, 
                run_command_name: str, 
                run_command_properties: MachineRunCommand, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MachineRunCommand]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                machine_name: str, 
                run_command_name: str, 
                run_command_properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MachineRunCommand]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                machine_name: str, 
                run_command_name: str, 
                run_command_properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MachineRunCommand]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                machine_name: str, 
                run_command_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                machine_name: str, 
                run_command_name: str, 
                **kwargs: Any
            ) -> MachineRunCommand: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                machine_name: str, 
                *, 
                expand: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[MachineRunCommand]: ...


    class azure.mgmt.hybridcompute.aio.operations.MachinesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_assess_patches(
                self, 
                resource_group_name: str, 
                name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[MachineAssessPatchesResult]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                machine_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_install_patches(
                self, 
                resource_group_name: str, 
                name: str, 
                install_patches_input: MachineInstallPatchesParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MachineInstallPatchesResult]: ...

        @overload
        async def begin_install_patches(
                self, 
                resource_group_name: str, 
                name: str, 
                install_patches_input: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MachineInstallPatchesResult]: ...

        @overload
        async def begin_install_patches(
                self, 
                resource_group_name: str, 
                name: str, 
                install_patches_input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MachineInstallPatchesResult]: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                machine_name: str, 
                parameters: Machine, 
                *, 
                content_type: str = "application/json", 
                expand: Optional[str] = ..., 
                **kwargs: Any
            ) -> Machine: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                machine_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                expand: Optional[str] = ..., 
                **kwargs: Any
            ) -> Machine: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                machine_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                expand: Optional[str] = ..., 
                **kwargs: Any
            ) -> Machine: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                machine_name: str, 
                *, 
                expand: Optional[Union[str, InstanceViewTypes]] = ..., 
                **kwargs: Any
            ) -> Machine: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                expand: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Machine]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[Machine]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                machine_name: str, 
                parameters: MachineUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Machine: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                machine_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Machine: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                machine_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Machine: ...


    class azure.mgmt.hybridcompute.aio.operations.NetworkProfileOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                machine_name: str, 
                **kwargs: Any
            ) -> NetworkProfile: ...


    class azure.mgmt.hybridcompute.aio.operations.NetworkSecurityPerimeterConfigurationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_reconcile_for_private_link_scope(
                self, 
                resource_group_name: str, 
                scope_name: str, 
                perimeter_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkSecurityPerimeterConfigurationReconcileResult]: ...

        @distributed_trace_async
        async def get_by_private_link_scope(
                self, 
                resource_group_name: str, 
                scope_name: str, 
                perimeter_name: str, 
                **kwargs: Any
            ) -> NetworkSecurityPerimeterConfiguration: ...

        @distributed_trace
        def list_by_private_link_scope(
                self, 
                resource_group_name: str, 
                scope_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[NetworkSecurityPerimeterConfiguration]: ...


    class azure.mgmt.hybridcompute.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[OperationValue]: ...


    class azure.mgmt.hybridcompute.aio.operations.PrivateEndpointConnectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                scope_name: str, 
                private_endpoint_connection_name: str, 
                parameters: PrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateEndpointConnection]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                scope_name: str, 
                private_endpoint_connection_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateEndpointConnection]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                scope_name: str, 
                private_endpoint_connection_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateEndpointConnection]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                scope_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                scope_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @distributed_trace
        def list_by_private_link_scope(
                self, 
                resource_group_name: str, 
                scope_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[PrivateEndpointConnection]: ...


    class azure.mgmt.hybridcompute.aio.operations.PrivateLinkResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                scope_name: str, 
                group_name: str, 
                **kwargs: Any
            ) -> PrivateLinkResource: ...

        @distributed_trace
        def list_by_private_link_scope(
                self, 
                resource_group_name: str, 
                scope_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[PrivateLinkResource]: ...


    class azure.mgmt.hybridcompute.aio.operations.PrivateLinkScopesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                scope_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                scope_name: str, 
                parameters: HybridComputePrivateLinkScope, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> HybridComputePrivateLinkScope: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                scope_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> HybridComputePrivateLinkScope: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                scope_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> HybridComputePrivateLinkScope: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                scope_name: str, 
                **kwargs: Any
            ) -> HybridComputePrivateLinkScope: ...

        @distributed_trace_async
        async def get_validation_details(
                self, 
                location: str, 
                private_link_scope_id: str, 
                **kwargs: Any
            ) -> PrivateLinkScopeValidationDetails: ...

        @distributed_trace_async
        async def get_validation_details_for_machine(
                self, 
                resource_group_name: str, 
                machine_name: str, 
                **kwargs: Any
            ) -> PrivateLinkScopeValidationDetails: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[HybridComputePrivateLinkScope]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[HybridComputePrivateLinkScope]: ...

        @overload
        async def update_tags(
                self, 
                resource_group_name: str, 
                scope_name: str, 
                private_link_scope_tags: TagsResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> HybridComputePrivateLinkScope: ...

        @overload
        async def update_tags(
                self, 
                resource_group_name: str, 
                scope_name: str, 
                private_link_scope_tags: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> HybridComputePrivateLinkScope: ...

        @overload
        async def update_tags(
                self, 
                resource_group_name: str, 
                scope_name: str, 
                private_link_scope_tags: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> HybridComputePrivateLinkScope: ...


    class azure.mgmt.hybridcompute.aio.operations.SettingsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                base_provider: str, 
                base_resource_type: str, 
                base_resource_name: str, 
                settings_resource_name: str, 
                **kwargs: Any
            ) -> Settings: ...

        @overload
        async def patch(
                self, 
                resource_group_name: str, 
                base_provider: str, 
                base_resource_type: str, 
                base_resource_name: str, 
                settings_resource_name: str, 
                parameters: Settings, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Settings: ...

        @overload
        async def patch(
                self, 
                resource_group_name: str, 
                base_provider: str, 
                base_resource_type: str, 
                base_resource_name: str, 
                settings_resource_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Settings: ...

        @overload
        async def patch(
                self, 
                resource_group_name: str, 
                base_provider: str, 
                base_resource_type: str, 
                base_resource_name: str, 
                settings_resource_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Settings: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                base_provider: str, 
                base_resource_type: str, 
                base_resource_name: str, 
                settings_resource_name: str, 
                parameters: Settings, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Settings: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                base_provider: str, 
                base_resource_type: str, 
                base_resource_name: str, 
                settings_resource_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Settings: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                base_provider: str, 
                base_resource_type: str, 
                base_resource_name: str, 
                settings_resource_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Settings: ...


namespace azure.mgmt.hybridcompute.models

    class azure.mgmt.hybridcompute.models.AccessMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUDIT = "audit"
        ENFORCED = "enforced"
        LEARNING = "learning"


    class azure.mgmt.hybridcompute.models.AccessRule(_Model):
        name: Optional[str]
        properties: Optional[AccessRuleProperties]


    class azure.mgmt.hybridcompute.models.AccessRuleDirection(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INBOUND = "Inbound"
        OUTBOUND = "Outbound"


    class azure.mgmt.hybridcompute.models.AccessRuleProperties(_Model):
        address_prefixes: Optional[list[str]]
        direction: Optional[Union[str, AccessRuleDirection]]


    class azure.mgmt.hybridcompute.models.AgentConfiguration(_Model):
        config_mode: Optional[Union[str, AgentConfigurationMode]]
        extensions_allow_list: Optional[list[ConfigurationExtension]]
        extensions_block_list: Optional[list[ConfigurationExtension]]
        extensions_enabled: Optional[str]
        guest_configuration_enabled: Optional[str]
        incoming_connections_ports: Optional[list[str]]
        proxy_bypass: Optional[list[str]]
        proxy_url: Optional[str]


    class azure.mgmt.hybridcompute.models.AgentConfigurationMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FULL = "full"
        MONITOR = "monitor"


    class azure.mgmt.hybridcompute.models.AgentUpgrade(_Model):
        correlation_id: Optional[str]
        desired_version: Optional[str]
        enable_automatic_upgrade: Optional[bool]
        last_attempt_desired_version: Optional[str]
        last_attempt_message: Optional[str]
        last_attempt_status: Optional[Union[str, LastAttemptStatusEnum]]
        last_attempt_timestamp: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                correlation_id: Optional[str] = ..., 
                desired_version: Optional[str] = ..., 
                enable_automatic_upgrade: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hybridcompute.models.ArcKindEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AVS = "AVS"
        AWS = "AWS"
        EPS = "EPS"
        GCP = "GCP"
        HCI = "HCI"
        SCVMM = "SCVMM"
        V_MWARE = "VMware"


    class azure.mgmt.hybridcompute.models.AssessmentModeTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTOMATIC_BY_PLATFORM = "AutomaticByPlatform"
        IMAGE_DEFAULT = "ImageDefault"


    class azure.mgmt.hybridcompute.models.AvailablePatchCountByClassification(_Model):
        critical: Optional[int]
        definition: Optional[int]
        feature_pack: Optional[int]
        other: Optional[int]
        security: Optional[int]
        service_pack: Optional[int]
        tools: Optional[int]
        update_rollup: Optional[int]
        updates: Optional[int]


    class azure.mgmt.hybridcompute.models.CloudMetadata(_Model):
        provider: Optional[str]


    class azure.mgmt.hybridcompute.models.ConfigurationExtension(_Model):
        publisher: Optional[str]
        type: Optional[str]


    class azure.mgmt.hybridcompute.models.ConnectionDetail(_Model):
        group_id: Optional[str]
        id: Optional[str]
        link_identifier: Optional[str]
        member_name: Optional[str]
        private_ip_address: Optional[str]


    class azure.mgmt.hybridcompute.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.hybridcompute.models.Disk(_Model):
        disk_type: Optional[str]
        generated_id: Optional[str]
        id: Optional[str]
        max_size_in_bytes: Optional[int]
        name: Optional[str]
        path: Optional[str]
        used_space_in_bytes: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                disk_type: Optional[str] = ..., 
                generated_id: Optional[str] = ..., 
                id: Optional[str] = ..., 
                max_size_in_bytes: Optional[int] = ..., 
                name: Optional[str] = ..., 
                path: Optional[str] = ..., 
                used_space_in_bytes: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hybridcompute.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.hybridcompute.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.hybridcompute.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hybridcompute.models.EsuEligibility(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ELIGIBLE = "Eligible"
        INELIGIBLE = "Ineligible"
        UNKNOWN = "Unknown"


    class azure.mgmt.hybridcompute.models.EsuKey(_Model):
        license_status: Optional[int]
        sku: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                license_status: Optional[int] = ..., 
                sku: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hybridcompute.models.EsuKeyState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        INACTIVE = "Inactive"


    class azure.mgmt.hybridcompute.models.EsuProfileUpdateProperties(_Model):
        assigned_license: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                assigned_license: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hybridcompute.models.EsuServerType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DATACENTER = "Datacenter"
        STANDARD = "Standard"


    class azure.mgmt.hybridcompute.models.ExecutionState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        FAILED = "Failed"
        PENDING = "Pending"
        RUNNING = "Running"
        SUCCEEDED = "Succeeded"
        TIMED_OUT = "TimedOut"
        UNKNOWN = "Unknown"


    class azure.mgmt.hybridcompute.models.ExtensionPublisher(_Model):
        id: Optional[str]
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hybridcompute.models.ExtensionTargetProperties(_Model):
        target_version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                target_version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hybridcompute.models.ExtensionType(_Model):
        id: Optional[str]
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hybridcompute.models.ExtensionValue(ProxyResource):
        id: str
        name: str
        properties: Optional[ExtensionValueProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ExtensionValueProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.hybridcompute.models.ExtensionValueProperties(_Model):
        extension_type: Optional[str]
        publisher: Optional[str]
        version: Optional[str]


    class azure.mgmt.hybridcompute.models.ExtensionValueV2(ProxyResource):
        id: str
        name: str
        properties: Optional[ExtensionValueV2Properties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ExtensionValueV2Properties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.hybridcompute.models.ExtensionValueV2Properties(ExtensionValueProperties):
        architecture: Optional[list[str]]
        extension_signature_uri: Optional[str]
        extension_type: str
        extension_uris: Optional[list[str]]
        operating_system: Optional[str]
        publisher: str
        version: str


    class azure.mgmt.hybridcompute.models.ExtensionsResourceStatus(_Model):
        code: Optional[str]
        display_status: Optional[str]
        level: Optional[Union[str, ExtensionsStatusLevelTypes]]
        message: Optional[str]
        time: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                display_status: Optional[str] = ..., 
                level: Optional[Union[str, ExtensionsStatusLevelTypes]] = ..., 
                message: Optional[str] = ..., 
                time: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hybridcompute.models.ExtensionsStatusLevelTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ERROR = "Error"
        INFO = "Info"
        WARNING = "Warning"


    class azure.mgmt.hybridcompute.models.FirmwareProfile(_Model):
        serial_number: Optional[str]
        type: Optional[str]


    class azure.mgmt.hybridcompute.models.Gateway(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[GatewayProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[GatewayProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.hybridcompute.models.GatewayProperties(_Model):
        allowed_features: Optional[list[str]]
        gateway_endpoint: Optional[str]
        gateway_id: Optional[str]
        gateway_type: Optional[Union[str, GatewayType]]
        provisioning_state: Optional[Union[str, ProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                allowed_features: Optional[list[str]] = ..., 
                gateway_type: Optional[Union[str, GatewayType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hybridcompute.models.GatewayType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PUBLIC = "Public"


    class azure.mgmt.hybridcompute.models.GatewayUpdate(ResourceUpdate):
        properties: Optional[GatewayUpdateProperties]
        tags: dict[str, str]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[GatewayUpdateProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.hybridcompute.models.GatewayUpdateProperties(_Model):
        allowed_features: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                allowed_features: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hybridcompute.models.HardwareProfile(_Model):
        number_of_cpu_sockets: Optional[int]
        processors: Optional[list[Processor]]
        total_physical_memory_in_bytes: Optional[int]


    class azure.mgmt.hybridcompute.models.HotpatchEnablementStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTION_REQUIRED = "ActionRequired"
        DISABLED = "Disabled"
        ENABLED = "Enabled"
        PENDING_EVALUATION = "PendingEvaluation"
        UNKNOWN = "Unknown"


    class azure.mgmt.hybridcompute.models.HybridComputePrivateLinkScope(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[HybridComputePrivateLinkScopeProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[HybridComputePrivateLinkScopeProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hybridcompute.models.HybridComputePrivateLinkScopeProperties(_Model):
        private_endpoint_connections: Optional[list[PrivateEndpointConnectionDataModel]]
        private_link_scope_id: Optional[str]
        provisioning_state: Optional[str]
        public_network_access: Optional[Union[str, PublicNetworkAccessType]]
        service_extensions: Optional[list[ServiceExtension]]

        @overload
        def __init__(
                self, 
                *, 
                public_network_access: Optional[Union[str, PublicNetworkAccessType]] = ..., 
                service_extensions: Optional[list[ServiceExtension]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hybridcompute.models.Identity(_Model):
        principal_id: Optional[str]
        tenant_id: Optional[str]
        type: Optional[Union[str, ResourceIdentityType]]

        @overload
        def __init__(
                self, 
                *, 
                type: Optional[Union[str, ResourceIdentityType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hybridcompute.models.IdentityKeyStore(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEFAULT = "Default"
        TPM = "TPM"


    class azure.mgmt.hybridcompute.models.InstanceViewTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INSTANCE_VIEW = "instanceView"


    class azure.mgmt.hybridcompute.models.IpAddress(_Model):
        address: Optional[str]
        ip_address_version: Optional[str]
        subnet: Optional[Subnet]

        @overload
        def __init__(
                self, 
                *, 
                address: Optional[str] = ..., 
                ip_address_version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hybridcompute.models.LastAttemptStatusEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAILED = "Failed"
        SUCCESS = "Success"


    class azure.mgmt.hybridcompute.models.License(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[LicenseProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[LicenseProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.hybridcompute.models.LicenseAssignmentState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ASSIGNED = "Assigned"
        NOT_ASSIGNED = "NotAssigned"


    class azure.mgmt.hybridcompute.models.LicenseCoreType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        P_CORE = "pCore"
        V_CORE = "vCore"


    class azure.mgmt.hybridcompute.models.LicenseDetails(_Model):
        assigned_licenses: Optional[int]
        edition: Optional[Union[str, LicenseEdition]]
        immutable_id: Optional[str]
        processors: Optional[int]
        state: Optional[Union[str, LicenseState]]
        target: Optional[Union[str, LicenseTarget]]
        type: Optional[Union[str, LicenseCoreType]]
        volume_license_details: Optional[list[VolumeLicenseDetails]]

        @overload
        def __init__(
                self, 
                *, 
                edition: Optional[Union[str, LicenseEdition]] = ..., 
                processors: Optional[int] = ..., 
                state: Optional[Union[str, LicenseState]] = ..., 
                target: Optional[Union[str, LicenseTarget]] = ..., 
                type: Optional[Union[str, LicenseCoreType]] = ..., 
                volume_license_details: Optional[list[VolumeLicenseDetails]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hybridcompute.models.LicenseEdition(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DATACENTER = "Datacenter"
        STANDARD = "Standard"


    class azure.mgmt.hybridcompute.models.LicenseProfile(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[LicenseProfileProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[LicenseProfileProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hybridcompute.models.LicenseProfileArmEsuProperties(LicenseProfileArmEsuPropertiesWithoutAssignedLicense):
        assigned_license: Optional[str]
        assigned_license_immutable_id: str
        esu_eligibility: Union[str, EsuEligibility]
        esu_key_state: Union[str, EsuKeyState]
        esu_keys: list[EsuKey]
        server_type: Union[str, EsuServerType]

        @overload
        def __init__(
                self, 
                *, 
                assigned_license: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hybridcompute.models.LicenseProfileArmEsuPropertiesWithoutAssignedLicense(LicenseProfileStorageModelEsuProperties):
        assigned_license_immutable_id: str
        esu_eligibility: Optional[Union[str, EsuEligibility]]
        esu_key_state: Optional[Union[str, EsuKeyState]]
        esu_keys: list[EsuKey]
        server_type: Optional[Union[str, EsuServerType]]


    class azure.mgmt.hybridcompute.models.LicenseProfileArmProductProfileProperties(_Model):
        billing_end_date: Optional[datetime]
        billing_start_date: Optional[datetime]
        disenrollment_date: Optional[datetime]
        enrollment_date: Optional[datetime]
        error: Optional[ErrorDetail]
        product_features: Optional[list[ProductFeature]]
        product_type: Optional[Union[str, LicenseProfileProductType]]
        subscription_status: Optional[Union[str, LicenseProfileSubscriptionStatus]]

        @overload
        def __init__(
                self, 
                *, 
                product_features: Optional[list[ProductFeature]] = ..., 
                product_type: Optional[Union[str, LicenseProfileProductType]] = ..., 
                subscription_status: Optional[Union[str, LicenseProfileSubscriptionStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hybridcompute.models.LicenseProfileMachineInstanceView(_Model):
        esu_profile: Optional[LicenseProfileMachineInstanceViewEsuProperties]
        license_channel: Optional[str]
        license_status: Optional[Union[str, LicenseStatus]]
        product_profile: Optional[LicenseProfileArmProductProfileProperties]
        software_assurance: Optional[LicenseProfileMachineInstanceViewSoftwareAssurance]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                esu_profile: Optional[LicenseProfileMachineInstanceViewEsuProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.hybridcompute.models.LicenseProfileMachineInstanceViewEsuProperties(LicenseProfileArmEsuPropertiesWithoutAssignedLicense):
        assigned_license: Optional[License]
        assigned_license_immutable_id: str
        esu_eligibility: Union[str, EsuEligibility]
        esu_key_state: Union[str, EsuKeyState]
        esu_keys: list[EsuKey]
        license_assignment_state: Optional[Union[str, LicenseAssignmentState]]
        server_type: Union[str, EsuServerType]

        @overload
        def __init__(
                self, 
                *, 
                assigned_license: Optional[License] = ..., 
                license_assignment_state: Optional[Union[str, LicenseAssignmentState]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hybridcompute.models.LicenseProfileMachineInstanceViewSoftwareAssurance(_Model):
        software_assurance_customer: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                software_assurance_customer: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hybridcompute.models.LicenseProfileProductType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        WINDOWS_IO_T_ENTERPRISE = "WindowsIoTEnterprise"
        WINDOWS_SERVER = "WindowsServer"


    class azure.mgmt.hybridcompute.models.LicenseProfileProperties(_Model):
        esu_profile: Optional[LicenseProfileArmEsuProperties]
        product_profile: Optional[LicenseProfileArmProductProfileProperties]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        software_assurance: Optional[LicenseProfilePropertiesSoftwareAssurance]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                esu_profile: Optional[LicenseProfileArmEsuProperties] = ..., 
                product_profile: Optional[LicenseProfileArmProductProfileProperties] = ..., 
                software_assurance: Optional[LicenseProfilePropertiesSoftwareAssurance] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.hybridcompute.models.LicenseProfilePropertiesSoftwareAssurance(_Model):
        software_assurance_customer: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                software_assurance_customer: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hybridcompute.models.LicenseProfileStorageModelEsuProperties(_Model):
        assigned_license_immutable_id: Optional[str]
        esu_keys: Optional[list[EsuKey]]


    class azure.mgmt.hybridcompute.models.LicenseProfileSubscriptionStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        DISABLING = "Disabling"
        ENABLED = "Enabled"
        ENABLING = "Enabling"
        FAILED = "Failed"
        UNKNOWN = "Unknown"


    class azure.mgmt.hybridcompute.models.LicenseProfileSubscriptionStatusUpdate(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLE = "Disable"
        ENABLE = "Enable"


    class azure.mgmt.hybridcompute.models.LicenseProfileUpdate(ResourceUpdate):
        properties: Optional[LicenseProfileUpdateProperties]
        tags: dict[str, str]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[LicenseProfileUpdateProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hybridcompute.models.LicenseProfileUpdateProperties(_Model):
        esu_profile: Optional[EsuProfileUpdateProperties]
        product_profile: Optional[ProductProfileUpdateProperties]
        software_assurance: Optional[LicenseProfileUpdatePropertiesSoftwareAssurance]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                esu_profile: Optional[EsuProfileUpdateProperties] = ..., 
                product_profile: Optional[ProductProfileUpdateProperties] = ..., 
                software_assurance: Optional[LicenseProfileUpdatePropertiesSoftwareAssurance] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.hybridcompute.models.LicenseProfileUpdatePropertiesSoftwareAssurance(_Model):
        software_assurance_customer: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                software_assurance_customer: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hybridcompute.models.LicenseProperties(_Model):
        license_details: Optional[LicenseDetails]
        license_type: Optional[Union[str, LicenseType]]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        tenant_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                license_details: Optional[LicenseDetails] = ..., 
                license_type: Optional[Union[str, LicenseType]] = ..., 
                tenant_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hybridcompute.models.LicenseState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVATED = "Activated"
        DEACTIVATED = "Deactivated"


    class azure.mgmt.hybridcompute.models.LicenseStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EXTENDED_GRACE = "ExtendedGrace"
        LICENSED = "Licensed"
        NON_GENUINE_GRACE = "NonGenuineGrace"
        NOTIFICATION = "Notification"
        OOB_GRACE = "OOBGrace"
        OOT_GRACE = "OOTGrace"
        UNLICENSED = "Unlicensed"


    class azure.mgmt.hybridcompute.models.LicenseTarget(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        WINDOWS_SERVER2012 = "Windows Server 2012"
        WINDOWS_SERVER2012_R2 = "Windows Server 2012 R2"


    class azure.mgmt.hybridcompute.models.LicenseType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ESU = "ESU"


    class azure.mgmt.hybridcompute.models.LicenseUpdate(ResourceUpdate):
        properties: Optional[LicenseUpdateProperties]
        tags: dict[str, str]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[LicenseUpdateProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hybridcompute.models.LicenseUpdateProperties(_Model):
        license_details: Optional[LicenseUpdatePropertiesLicenseDetails]
        license_type: Optional[Union[str, LicenseType]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                license_details: Optional[LicenseUpdatePropertiesLicenseDetails] = ..., 
                license_type: Optional[Union[str, LicenseType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.hybridcompute.models.LicenseUpdatePropertiesLicenseDetails(_Model):
        edition: Optional[Union[str, LicenseEdition]]
        processors: Optional[int]
        state: Optional[Union[str, LicenseState]]
        target: Optional[Union[str, LicenseTarget]]
        type: Optional[Union[str, LicenseCoreType]]

        @overload
        def __init__(
                self, 
                *, 
                edition: Optional[Union[str, LicenseEdition]] = ..., 
                processors: Optional[int] = ..., 
                state: Optional[Union[str, LicenseState]] = ..., 
                target: Optional[Union[str, LicenseTarget]] = ..., 
                type: Optional[Union[str, LicenseCoreType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hybridcompute.models.LinuxParameters(_Model):
        classifications_to_include: Optional[list[Union[str, VMGuestPatchClassificationLinux]]]
        package_name_masks_to_exclude: Optional[list[str]]
        package_name_masks_to_include: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                classifications_to_include: Optional[list[Union[str, VMGuestPatchClassificationLinux]]] = ..., 
                package_name_masks_to_exclude: Optional[list[str]] = ..., 
                package_name_masks_to_include: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hybridcompute.models.LocationData(_Model):
        city: Optional[str]
        country_or_region: Optional[str]
        district: Optional[str]
        name: str

        @overload
        def __init__(
                self, 
                *, 
                city: Optional[str] = ..., 
                country_or_region: Optional[str] = ..., 
                district: Optional[str] = ..., 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hybridcompute.models.Machine(TrackedResource):
        id: str
        identity: Optional[Identity]
        kind: Optional[Union[str, ArcKindEnum]]
        location: str
        name: str
        properties: Optional[MachineProperties]
        resources: Optional[list[MachineExtension]]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[Identity] = ..., 
                kind: Optional[Union[str, ArcKindEnum]] = ..., 
                location: str, 
                properties: Optional[MachineProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.hybridcompute.models.MachineAssessPatchesResult(_Model):
        assessment_activity_id: Optional[str]
        available_patch_count_by_classification: Optional[AvailablePatchCountByClassification]
        error_details: Optional[ErrorDetail]
        last_modified_date_time: Optional[datetime]
        os_type: Optional[Union[str, OsType]]
        patch_service_used: Optional[Union[str, PatchServiceUsed]]
        reboot_pending: Optional[bool]
        start_date_time: Optional[datetime]
        started_by: Optional[Union[str, PatchOperationStartedBy]]
        status: Optional[Union[str, PatchOperationStatus]]

        @overload
        def __init__(
                self, 
                *, 
                available_patch_count_by_classification: Optional[AvailablePatchCountByClassification] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hybridcompute.models.MachineExtension(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[MachineExtensionProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[MachineExtensionProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hybridcompute.models.MachineExtensionInstanceView(_Model):
        name: Optional[str]
        status: Optional[MachineExtensionInstanceViewStatus]
        type: Optional[str]
        type_handler_version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                status: Optional[MachineExtensionInstanceViewStatus] = ..., 
                type: Optional[str] = ..., 
                type_handler_version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hybridcompute.models.MachineExtensionInstanceViewStatus(_Model):
        code: Optional[str]
        display_status: Optional[str]
        level: Optional[Union[str, StatusLevelTypes]]
        message: Optional[str]
        time: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                display_status: Optional[str] = ..., 
                level: Optional[Union[str, StatusLevelTypes]] = ..., 
                message: Optional[str] = ..., 
                time: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hybridcompute.models.MachineExtensionProperties(_Model):
        auto_upgrade_minor_version: Optional[bool]
        enable_automatic_upgrade: Optional[bool]
        force_update_tag: Optional[str]
        instance_view: Optional[MachineExtensionInstanceView]
        protected_settings: Optional[dict[str, Any]]
        provisioning_state: Optional[str]
        publisher: Optional[str]
        settings: Optional[dict[str, Any]]
        type: Optional[str]
        type_handler_version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                auto_upgrade_minor_version: Optional[bool] = ..., 
                enable_automatic_upgrade: Optional[bool] = ..., 
                force_update_tag: Optional[str] = ..., 
                instance_view: Optional[MachineExtensionInstanceView] = ..., 
                protected_settings: Optional[dict[str, Any]] = ..., 
                publisher: Optional[str] = ..., 
                settings: Optional[dict[str, Any]] = ..., 
                type: Optional[str] = ..., 
                type_handler_version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hybridcompute.models.MachineExtensionUpdate(ResourceUpdate):
        properties: Optional[MachineExtensionUpdateProperties]
        tags: dict[str, str]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[MachineExtensionUpdateProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.hybridcompute.models.MachineExtensionUpdateProperties(_Model):
        auto_upgrade_minor_version: Optional[bool]
        enable_automatic_upgrade: Optional[bool]
        force_update_tag: Optional[str]
        protected_settings: Optional[dict[str, Any]]
        publisher: Optional[str]
        settings: Optional[dict[str, Any]]
        type: Optional[str]
        type_handler_version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                auto_upgrade_minor_version: Optional[bool] = ..., 
                enable_automatic_upgrade: Optional[bool] = ..., 
                force_update_tag: Optional[str] = ..., 
                protected_settings: Optional[dict[str, Any]] = ..., 
                publisher: Optional[str] = ..., 
                settings: Optional[dict[str, Any]] = ..., 
                type: Optional[str] = ..., 
                type_handler_version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hybridcompute.models.MachineExtensionUpgrade(_Model):
        extension_targets: Optional[dict[str, ExtensionTargetProperties]]

        @overload
        def __init__(
                self, 
                *, 
                extension_targets: Optional[dict[str, ExtensionTargetProperties]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hybridcompute.models.MachineInstallPatchesParameters(_Model):
        linux_parameters: Optional[LinuxParameters]
        maximum_duration: timedelta
        reboot_setting: Union[str, VMGuestPatchRebootSetting]
        windows_parameters: Optional[WindowsParameters]

        @overload
        def __init__(
                self, 
                *, 
                linux_parameters: Optional[LinuxParameters] = ..., 
                maximum_duration: timedelta, 
                reboot_setting: Union[str, VMGuestPatchRebootSetting], 
                windows_parameters: Optional[WindowsParameters] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hybridcompute.models.MachineInstallPatchesResult(_Model):
        error_details: Optional[ErrorDetail]
        excluded_patch_count: Optional[int]
        failed_patch_count: Optional[int]
        installation_activity_id: Optional[str]
        installed_patch_count: Optional[int]
        last_modified_date_time: Optional[datetime]
        maintenance_window_exceeded: Optional[bool]
        not_selected_patch_count: Optional[int]
        os_type: Optional[Union[str, OsType]]
        patch_service_used: Optional[Union[str, PatchServiceUsed]]
        pending_patch_count: Optional[int]
        reboot_status: Optional[Union[str, VMGuestPatchRebootStatus]]
        start_date_time: Optional[datetime]
        started_by: Optional[Union[str, PatchOperationStartedBy]]
        status: Optional[Union[str, PatchOperationStatus]]


    class azure.mgmt.hybridcompute.models.MachineProperties(_Model):
        ad_fqdn: Optional[str]
        agent_configuration: Optional[AgentConfiguration]
        agent_upgrade: Optional[AgentUpgrade]
        agent_version: Optional[str]
        client_public_key: Optional[str]
        cloud_metadata: Optional[CloudMetadata]
        detected_properties: Optional[dict[str, str]]
        display_name: Optional[str]
        dns_fqdn: Optional[str]
        domain_name: Optional[str]
        error_details: Optional[list[ErrorDetail]]
        extensions: Optional[list[MachineExtensionInstanceView]]
        firmware_profile: Optional[FirmwareProfile]
        hardware_profile: Optional[HardwareProfile]
        hardware_resource_id: Optional[str]
        identity_key_store: Optional[Union[str, IdentityKeyStore]]
        last_status_change: Optional[datetime]
        license_profile: Optional[LicenseProfileMachineInstanceView]
        location_data: Optional[LocationData]
        machine_fqdn: Optional[str]
        mssql_discovered: Optional[str]
        network_profile: Optional[NetworkProfile]
        os_edition: Optional[str]
        os_name: Optional[str]
        os_profile: Optional[OSProfile]
        os_sku: Optional[str]
        os_type: Optional[str]
        os_version: Optional[str]
        parent_cluster_resource_id: Optional[str]
        private_link_scope_resource_id: Optional[str]
        provisioning_state: Optional[str]
        service_statuses: Optional[ServiceStatuses]
        status: Optional[Union[str, StatusTypes]]
        storage_profile: Optional[StorageProfile]
        tpm_ek_certificate: Optional[str]
        vm_id: Optional[str]
        vm_uuid: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                agent_upgrade: Optional[AgentUpgrade] = ..., 
                client_public_key: Optional[str] = ..., 
                cloud_metadata: Optional[CloudMetadata] = ..., 
                extensions: Optional[list[MachineExtensionInstanceView]] = ..., 
                hardware_resource_id: Optional[str] = ..., 
                identity_key_store: Optional[Union[str, IdentityKeyStore]] = ..., 
                license_profile: Optional[LicenseProfileMachineInstanceView] = ..., 
                location_data: Optional[LocationData] = ..., 
                mssql_discovered: Optional[str] = ..., 
                os_profile: Optional[OSProfile] = ..., 
                os_type: Optional[str] = ..., 
                parent_cluster_resource_id: Optional[str] = ..., 
                private_link_scope_resource_id: Optional[str] = ..., 
                service_statuses: Optional[ServiceStatuses] = ..., 
                tpm_ek_certificate: Optional[str] = ..., 
                vm_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hybridcompute.models.MachineRunCommand(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[MachineRunCommandProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[MachineRunCommandProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.hybridcompute.models.MachineRunCommandInstanceView(_Model):
        end_time: Optional[datetime]
        error: Optional[str]
        execution_message: Optional[str]
        execution_state: Optional[Union[str, ExecutionState]]
        exit_code: Optional[int]
        output: Optional[str]
        start_time: Optional[datetime]
        statuses: Optional[list[ExtensionsResourceStatus]]

        @overload
        def __init__(
                self, 
                *, 
                end_time: Optional[datetime] = ..., 
                error: Optional[str] = ..., 
                execution_message: Optional[str] = ..., 
                execution_state: Optional[Union[str, ExecutionState]] = ..., 
                exit_code: Optional[int] = ..., 
                output: Optional[str] = ..., 
                start_time: Optional[datetime] = ..., 
                statuses: Optional[list[ExtensionsResourceStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hybridcompute.models.MachineRunCommandProperties(_Model):
        async_execution: Optional[bool]
        error_blob_managed_identity: Optional[RunCommandManagedIdentity]
        error_blob_uri: Optional[str]
        instance_view: Optional[MachineRunCommandInstanceView]
        output_blob_managed_identity: Optional[RunCommandManagedIdentity]
        output_blob_uri: Optional[str]
        parameters: Optional[list[RunCommandInputParameter]]
        protected_parameters: Optional[list[RunCommandInputParameter]]
        provisioning_state: Optional[str]
        run_as_password: Optional[str]
        run_as_user: Optional[str]
        source: Optional[MachineRunCommandScriptSource]
        timeout_in_seconds: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                async_execution: Optional[bool] = ..., 
                error_blob_managed_identity: Optional[RunCommandManagedIdentity] = ..., 
                error_blob_uri: Optional[str] = ..., 
                output_blob_managed_identity: Optional[RunCommandManagedIdentity] = ..., 
                output_blob_uri: Optional[str] = ..., 
                parameters: Optional[list[RunCommandInputParameter]] = ..., 
                protected_parameters: Optional[list[RunCommandInputParameter]] = ..., 
                run_as_password: Optional[str] = ..., 
                run_as_user: Optional[str] = ..., 
                source: Optional[MachineRunCommandScriptSource] = ..., 
                timeout_in_seconds: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hybridcompute.models.MachineRunCommandScriptSource(_Model):
        command_id: Optional[str]
        script: Optional[str]
        script_uri: Optional[str]
        script_uri_managed_identity: Optional[RunCommandManagedIdentity]

        @overload
        def __init__(
                self, 
                *, 
                command_id: Optional[str] = ..., 
                script: Optional[str] = ..., 
                script_uri: Optional[str] = ..., 
                script_uri_managed_identity: Optional[RunCommandManagedIdentity] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hybridcompute.models.MachineUpdate(ResourceUpdate):
        identity: Optional[Identity]
        kind: Optional[Union[str, ArcKindEnum]]
        properties: Optional[MachineUpdateProperties]
        tags: dict[str, str]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[Identity] = ..., 
                kind: Optional[Union[str, ArcKindEnum]] = ..., 
                properties: Optional[MachineUpdateProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.hybridcompute.models.MachineUpdateProperties(_Model):
        agent_upgrade: Optional[AgentUpgrade]
        cloud_metadata: Optional[CloudMetadata]
        identity_key_store: Optional[str]
        location_data: Optional[LocationData]
        os_profile: Optional[OSProfile]
        parent_cluster_resource_id: Optional[str]
        private_link_scope_resource_id: Optional[str]
        tpm_ek_certificate: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                agent_upgrade: Optional[AgentUpgrade] = ..., 
                cloud_metadata: Optional[CloudMetadata] = ..., 
                identity_key_store: Optional[str] = ..., 
                location_data: Optional[LocationData] = ..., 
                os_profile: Optional[OSProfile] = ..., 
                parent_cluster_resource_id: Optional[str] = ..., 
                private_link_scope_resource_id: Optional[str] = ..., 
                tpm_ek_certificate: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hybridcompute.models.NetworkInterface(_Model):
        id: Optional[str]
        ip_addresses: Optional[list[IpAddress]]
        mac_address: Optional[str]
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                mac_address: Optional[str] = ..., 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hybridcompute.models.NetworkProfile(_Model):
        network_interfaces: Optional[list[NetworkInterface]]


    class azure.mgmt.hybridcompute.models.NetworkSecurityPerimeter(_Model):
        id: Optional[str]
        location: Optional[str]
        perimeter_guid: Optional[str]


    class azure.mgmt.hybridcompute.models.NetworkSecurityPerimeterConfiguration(ProxyResource):
        id: str
        name: str
        properties: Optional[NetworkSecurityPerimeterConfigurationProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[NetworkSecurityPerimeterConfigurationProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.hybridcompute.models.NetworkSecurityPerimeterConfigurationProperties(_Model):
        network_security_perimeter: Optional[NetworkSecurityPerimeter]
        profile: Optional[NetworkSecurityPerimeterProfile]
        provisioning_issues: Optional[list[ProvisioningIssue]]
        provisioning_state: Optional[str]
        resource_association: Optional[ResourceAssociation]

        @overload
        def __init__(
                self, 
                *, 
                network_security_perimeter: Optional[NetworkSecurityPerimeter] = ..., 
                profile: Optional[NetworkSecurityPerimeterProfile] = ..., 
                resource_association: Optional[ResourceAssociation] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hybridcompute.models.NetworkSecurityPerimeterConfigurationReconcileResult(_Model):
        location: Optional[str]


    class azure.mgmt.hybridcompute.models.NetworkSecurityPerimeterProfile(_Model):
        access_rules: Optional[list[AccessRule]]
        access_rules_version: Optional[int]
        diagnostic_settings_version: Optional[int]
        enabled_log_categories: Optional[list[str]]
        name: Optional[str]


    class azure.mgmt.hybridcompute.models.OSProfile(_Model):
        computer_name: Optional[str]
        linux_configuration: Optional[OSProfileLinuxConfiguration]
        windows_configuration: Optional[OSProfileWindowsConfiguration]

        @overload
        def __init__(
                self, 
                *, 
                linux_configuration: Optional[OSProfileLinuxConfiguration] = ..., 
                windows_configuration: Optional[OSProfileWindowsConfiguration] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hybridcompute.models.OSProfileLinuxConfiguration(_Model):
        patch_settings: Optional[PatchSettings]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                patch_settings: Optional[PatchSettings] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.hybridcompute.models.OSProfileWindowsConfiguration(_Model):
        patch_settings: Optional[PatchSettings]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                patch_settings: Optional[PatchSettings] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.hybridcompute.models.OperationValue(_Model):
        display: Optional[OperationValueDisplay]
        is_data_action: Optional[bool]
        name: Optional[str]
        origin: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                display: Optional[OperationValueDisplay] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hybridcompute.models.OperationValueDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.hybridcompute.models.OsType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LINUX = "Linux"
        WINDOWS = "Windows"


    class azure.mgmt.hybridcompute.models.PatchModeTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTOMATIC_BY_OS = "AutomaticByOS"
        AUTOMATIC_BY_PLATFORM = "AutomaticByPlatform"
        IMAGE_DEFAULT = "ImageDefault"
        MANUAL = "Manual"


    class azure.mgmt.hybridcompute.models.PatchOperationStartedBy(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PLATFORM = "Platform"
        USER = "User"


    class azure.mgmt.hybridcompute.models.PatchOperationStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPLETED_WITH_WARNINGS = "CompletedWithWarnings"
        FAILED = "Failed"
        IN_PROGRESS = "InProgress"
        SUCCEEDED = "Succeeded"
        UNKNOWN = "Unknown"


    class azure.mgmt.hybridcompute.models.PatchServiceUsed(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APT = "APT"
        UNKNOWN = "Unknown"
        WU = "WU"
        WU_WSUS = "WU_WSUS"
        YUM = "YUM"
        ZYPPER = "Zypper"


    class azure.mgmt.hybridcompute.models.PatchSettings(_Model):
        assessment_mode: Optional[Union[str, AssessmentModeTypes]]
        enable_hotpatching: Optional[bool]
        patch_mode: Optional[Union[str, PatchModeTypes]]
        status: Optional[PatchSettingsStatus]

        @overload
        def __init__(
                self, 
                *, 
                assessment_mode: Optional[Union[str, AssessmentModeTypes]] = ..., 
                enable_hotpatching: Optional[bool] = ..., 
                patch_mode: Optional[Union[str, PatchModeTypes]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hybridcompute.models.PatchSettingsStatus(_Model):
        error: Optional[ErrorDetail]
        hotpatch_enablement_status: Optional[Union[str, HotpatchEnablementStatus]]

        @overload
        def __init__(
                self, 
                *, 
                hotpatch_enablement_status: Optional[Union[str, HotpatchEnablementStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hybridcompute.models.PrivateEndpointConnection(ProxyResource):
        id: str
        name: str
        properties: Optional[PrivateEndpointConnectionProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[PrivateEndpointConnectionProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hybridcompute.models.PrivateEndpointConnectionDataModel(_Model):
        id: Optional[str]
        name: Optional[str]
        properties: Optional[PrivateEndpointConnectionProperties]
        type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[PrivateEndpointConnectionProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hybridcompute.models.PrivateEndpointConnectionProperties(_Model):
        group_ids: Optional[list[str]]
        private_endpoint: Optional[PrivateEndpointProperty]
        private_link_service_connection_state: Optional[PrivateLinkServiceConnectionStateProperty]
        provisioning_state: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                private_endpoint: Optional[PrivateEndpointProperty] = ..., 
                private_link_service_connection_state: Optional[PrivateLinkServiceConnectionStateProperty] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hybridcompute.models.PrivateEndpointProperty(_Model):
        id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hybridcompute.models.PrivateLinkResource(ProxyResource):
        id: str
        name: str
        properties: Optional[PrivateLinkResourceProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[PrivateLinkResourceProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hybridcompute.models.PrivateLinkResourceProperties(_Model):
        group_id: Optional[str]
        required_members: Optional[list[str]]
        required_zone_names: Optional[list[str]]


    class azure.mgmt.hybridcompute.models.PrivateLinkScopeValidationDetails(_Model):
        connection_details: Optional[list[ConnectionDetail]]
        id: Optional[str]
        public_network_access: Optional[Union[str, PublicNetworkAccessType]]

        @overload
        def __init__(
                self, 
                *, 
                connection_details: Optional[list[ConnectionDetail]] = ..., 
                public_network_access: Optional[Union[str, PublicNetworkAccessType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hybridcompute.models.PrivateLinkServiceConnectionStateProperty(_Model):
        actions_required: Optional[str]
        description: str
        status: str

        @overload
        def __init__(
                self, 
                *, 
                description: str, 
                status: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hybridcompute.models.Processor(_Model):
        name: Optional[str]
        number_of_cores: Optional[int]


    class azure.mgmt.hybridcompute.models.ProductFeature(_Model):
        billing_end_date: Optional[datetime]
        billing_start_date: Optional[datetime]
        disenrollment_date: Optional[datetime]
        enrollment_date: Optional[datetime]
        error: Optional[ErrorDetail]
        name: Optional[str]
        subscription_status: Optional[Union[str, LicenseProfileSubscriptionStatus]]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                subscription_status: Optional[Union[str, LicenseProfileSubscriptionStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hybridcompute.models.ProductFeatureUpdate(_Model):
        name: Optional[str]
        subscription_status: Optional[Union[str, LicenseProfileSubscriptionStatusUpdate]]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                subscription_status: Optional[Union[str, LicenseProfileSubscriptionStatusUpdate]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hybridcompute.models.ProductProfileUpdateProperties(_Model):
        product_features: Optional[list[ProductFeatureUpdate]]
        product_type: Optional[Union[str, LicenseProfileProductType]]
        subscription_status: Optional[Union[str, LicenseProfileSubscriptionStatusUpdate]]

        @overload
        def __init__(
                self, 
                *, 
                product_features: Optional[list[ProductFeatureUpdate]] = ..., 
                product_type: Optional[Union[str, LicenseProfileProductType]] = ..., 
                subscription_status: Optional[Union[str, LicenseProfileSubscriptionStatusUpdate]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hybridcompute.models.ProgramYear(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        YEAR1 = "Year 1"
        YEAR2 = "Year 2"
        YEAR3 = "Year 3"


    class azure.mgmt.hybridcompute.models.ProvisioningIssue(_Model):
        name: Optional[str]
        properties: Optional[ProvisioningIssueProperties]


    class azure.mgmt.hybridcompute.models.ProvisioningIssueProperties(_Model):
        description: Optional[str]
        issue_type: Optional[Union[str, ProvisioningIssueType]]
        severity: Optional[Union[str, ProvisioningIssueSeverity]]
        suggested_access_rules: Optional[list[AccessRule]]
        suggested_resource_ids: Optional[list[str]]


    class azure.mgmt.hybridcompute.models.ProvisioningIssueSeverity(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ERROR = "Error"
        WARNING = "Warning"


    class azure.mgmt.hybridcompute.models.ProvisioningIssueType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONFIGURATION_PROPAGATION_FAILURE = "ConfigurationPropagationFailure"
        MISSING_IDENTITY_CONFIGURATION = "MissingIdentityConfiguration"
        MISSING_PERIMETER_CONFIGURATION = "MissingPerimeterConfiguration"
        OTHER = "Other"


    class azure.mgmt.hybridcompute.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETED = "Deleted"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.hybridcompute.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.hybridcompute.models.PublicNetworkAccessType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"
        SECURED_BY_PERIMETER = "SecuredByPerimeter"


    class azure.mgmt.hybridcompute.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.hybridcompute.models.ResourceAssociation(_Model):
        access_mode: Optional[Union[str, AccessMode]]
        name: Optional[str]


    class azure.mgmt.hybridcompute.models.ResourceIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM_ASSIGNED = "SystemAssigned"


    class azure.mgmt.hybridcompute.models.ResourceUpdate(_Model):
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hybridcompute.models.RunCommandInputParameter(_Model):
        name: str
        value: str

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                value: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hybridcompute.models.RunCommandManagedIdentity(_Model):
        client_id: Optional[str]
        object_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                client_id: Optional[str] = ..., 
                object_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hybridcompute.models.ServiceExtension(_Model):
        service_extension_public_network_access: Optional[Union[str, ServiceExtensionPublicNetworkAccess]]
        service_extension_type: Optional[ServiceExtensionType]

        @overload
        def __init__(
                self, 
                *, 
                service_extension_public_network_access: Optional[Union[str, ServiceExtensionPublicNetworkAccess]] = ..., 
                service_extension_type: Optional[ServiceExtensionType] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hybridcompute.models.ServiceExtensionPublicNetworkAccess(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.hybridcompute.models.ServiceStatus(_Model):
        startup_type: Optional[str]
        status: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                startup_type: Optional[str] = ..., 
                status: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hybridcompute.models.ServiceStatuses(_Model):
        extension_service: Optional[ServiceStatus]
        guest_configuration_service: Optional[ServiceStatus]

        @overload
        def __init__(
                self, 
                *, 
                extension_service: Optional[ServiceStatus] = ..., 
                guest_configuration_service: Optional[ServiceStatus] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hybridcompute.models.Settings(ProxyResource):
        id: str
        name: str
        properties: Optional[SettingsProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SettingsProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hybridcompute.models.SettingsGatewayProperties(_Model):
        gateway_resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                gateway_resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hybridcompute.models.SettingsProperties(_Model):
        gateway_properties: Optional[SettingsGatewayProperties]
        tenant_id: Optional[str]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                gateway_properties: Optional[SettingsGatewayProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.hybridcompute.models.SetupExtensionRequest(_Model):
        extensions: Optional[list[MachineExtensionProperties]]

        @overload
        def __init__(
                self, 
                *, 
                extensions: Optional[list[MachineExtensionProperties]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hybridcompute.models.StatusLevelTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ERROR = "Error"
        INFO = "Info"
        WARNING = "Warning"


    class azure.mgmt.hybridcompute.models.StatusTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AWAITING_CONNECTION = "AwaitingConnection"
        CONNECTED = "Connected"
        DISCONNECTED = "Disconnected"
        ERROR = "Error"


    class azure.mgmt.hybridcompute.models.StorageProfile(_Model):
        disks: Optional[list[Disk]]


    class azure.mgmt.hybridcompute.models.Subnet(_Model):
        address_prefix: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                address_prefix: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hybridcompute.models.SystemData(_Model):
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


    class azure.mgmt.hybridcompute.models.TagsResource(_Model):
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hybridcompute.models.TrackedResource(Resource):
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


    class azure.mgmt.hybridcompute.models.VMGuestPatchClassificationLinux(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CRITICAL = "Critical"
        OTHER = "Other"
        SECURITY = "Security"


    class azure.mgmt.hybridcompute.models.VMGuestPatchClassificationWindows(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CRITICAL = "Critical"
        DEFINITION = "Definition"
        FEATURE_PACK = "FeaturePack"
        SECURITY = "Security"
        SERVICE_PACK = "ServicePack"
        TOOLS = "Tools"
        UPDATES = "Updates"
        UPDATE_ROLL_UP = "UpdateRollUp"


    class azure.mgmt.hybridcompute.models.VMGuestPatchRebootSetting(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALWAYS = "Always"
        IF_REQUIRED = "IfRequired"
        NEVER = "Never"


    class azure.mgmt.hybridcompute.models.VMGuestPatchRebootStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPLETED = "Completed"
        FAILED = "Failed"
        NOT_NEEDED = "NotNeeded"
        REQUIRED = "Required"
        STARTED = "Started"
        UNKNOWN = "Unknown"


    class azure.mgmt.hybridcompute.models.VolumeLicenseDetails(_Model):
        invoice_id: Optional[str]
        program_year: Optional[Union[str, ProgramYear]]

        @overload
        def __init__(
                self, 
                *, 
                invoice_id: Optional[str] = ..., 
                program_year: Optional[Union[str, ProgramYear]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hybridcompute.models.WindowsParameters(_Model):
        classifications_to_include: Optional[list[Union[str, VMGuestPatchClassificationWindows]]]
        exclude_kbs_requiring_reboot: Optional[bool]
        kb_numbers_to_exclude: Optional[list[str]]
        kb_numbers_to_include: Optional[list[str]]
        max_patch_publish_date: Optional[datetime]
        patch_name_masks_to_exclude: Optional[list[str]]
        patch_name_masks_to_include: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                classifications_to_include: Optional[list[Union[str, VMGuestPatchClassificationWindows]]] = ..., 
                exclude_kbs_requiring_reboot: Optional[bool] = ..., 
                kb_numbers_to_exclude: Optional[list[str]] = ..., 
                kb_numbers_to_include: Optional[list[str]] = ..., 
                max_patch_publish_date: Optional[datetime] = ..., 
                patch_name_masks_to_exclude: Optional[list[str]] = ..., 
                patch_name_masks_to_include: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


namespace azure.mgmt.hybridcompute.operations

    class azure.mgmt.hybridcompute.operations.ExtensionMetadataOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                location: str, 
                publisher: str, 
                extension_type: str, 
                version: str, 
                **kwargs: Any
            ) -> ExtensionValue: ...

        @distributed_trace
        def list(
                self, 
                location: str, 
                publisher: str, 
                extension_type: str, 
                **kwargs: Any
            ) -> ItemPaged[ExtensionValue]: ...


    class azure.mgmt.hybridcompute.operations.ExtensionMetadataV2Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                location: str, 
                publisher: str, 
                extension_type: str, 
                version: str, 
                **kwargs: Any
            ) -> ExtensionValueV2: ...

        @distributed_trace
        def list(
                self, 
                location: str, 
                publisher: str, 
                extension_type: str, 
                **kwargs: Any
            ) -> ItemPaged[ExtensionValueV2]: ...


    class azure.mgmt.hybridcompute.operations.ExtensionPublisherOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                location: str, 
                **kwargs: Any
            ) -> ItemPaged[ExtensionPublisher]: ...


    class azure.mgmt.hybridcompute.operations.ExtensionTypeOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                location: str, 
                publisher: str, 
                **kwargs: Any
            ) -> ItemPaged[ExtensionType]: ...


    class azure.mgmt.hybridcompute.operations.GatewaysOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                gateway_name: str, 
                parameters: Gateway, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Gateway]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                gateway_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Gateway]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                gateway_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Gateway]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                gateway_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                gateway_name: str, 
                **kwargs: Any
            ) -> Gateway: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Gateway]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[Gateway]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                gateway_name: str, 
                parameters: GatewayUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Gateway: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                gateway_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Gateway: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                gateway_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Gateway: ...


    class azure.mgmt.hybridcompute.operations.LicenseProfilesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                machine_name: str, 
                parameters: LicenseProfile, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[LicenseProfile]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                machine_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[LicenseProfile]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                machine_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[LicenseProfile]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                machine_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                machine_name: str, 
                parameters: LicenseProfileUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[LicenseProfile]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                machine_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[LicenseProfile]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                machine_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[LicenseProfile]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                machine_name: str, 
                **kwargs: Any
            ) -> LicenseProfile: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                machine_name: str, 
                **kwargs: Any
            ) -> ItemPaged[LicenseProfile]: ...


    class azure.mgmt.hybridcompute.operations.LicensesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                license_name: str, 
                parameters: License, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[License]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                license_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[License]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                license_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[License]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                license_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                license_name: str, 
                parameters: LicenseUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[License]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                license_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[License]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                license_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[License]: ...

        @overload
        def begin_validate_license(
                self, 
                parameters: License, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[License]: ...

        @overload
        def begin_validate_license(
                self, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[License]: ...

        @overload
        def begin_validate_license(
                self, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[License]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                license_name: str, 
                **kwargs: Any
            ) -> License: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[License]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[License]: ...


    class azure.mgmt.hybridcompute.operations.MachineExtensionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                machine_name: str, 
                extension_name: str, 
                extension_parameters: MachineExtension, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MachineExtension]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                machine_name: str, 
                extension_name: str, 
                extension_parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MachineExtension]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                machine_name: str, 
                extension_name: str, 
                extension_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MachineExtension]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                machine_name: str, 
                extension_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                machine_name: str, 
                extension_name: str, 
                extension_parameters: MachineExtensionUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MachineExtension]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                machine_name: str, 
                extension_name: str, 
                extension_parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MachineExtension]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                machine_name: str, 
                extension_name: str, 
                extension_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MachineExtension]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                machine_name: str, 
                extension_name: str, 
                **kwargs: Any
            ) -> MachineExtension: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                machine_name: str, 
                *, 
                expand: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[MachineExtension]: ...


    class azure.mgmt.hybridcompute.operations.MachineRunCommandsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                machine_name: str, 
                run_command_name: str, 
                run_command_properties: MachineRunCommand, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MachineRunCommand]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                machine_name: str, 
                run_command_name: str, 
                run_command_properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MachineRunCommand]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                machine_name: str, 
                run_command_name: str, 
                run_command_properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MachineRunCommand]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                machine_name: str, 
                run_command_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                machine_name: str, 
                run_command_name: str, 
                **kwargs: Any
            ) -> MachineRunCommand: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                machine_name: str, 
                *, 
                expand: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[MachineRunCommand]: ...


    class azure.mgmt.hybridcompute.operations.MachinesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_assess_patches(
                self, 
                resource_group_name: str, 
                name: str, 
                **kwargs: Any
            ) -> LROPoller[MachineAssessPatchesResult]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                machine_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_install_patches(
                self, 
                resource_group_name: str, 
                name: str, 
                install_patches_input: MachineInstallPatchesParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MachineInstallPatchesResult]: ...

        @overload
        def begin_install_patches(
                self, 
                resource_group_name: str, 
                name: str, 
                install_patches_input: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MachineInstallPatchesResult]: ...

        @overload
        def begin_install_patches(
                self, 
                resource_group_name: str, 
                name: str, 
                install_patches_input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MachineInstallPatchesResult]: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                machine_name: str, 
                parameters: Machine, 
                *, 
                content_type: str = "application/json", 
                expand: Optional[str] = ..., 
                **kwargs: Any
            ) -> Machine: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                machine_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                expand: Optional[str] = ..., 
                **kwargs: Any
            ) -> Machine: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                machine_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                expand: Optional[str] = ..., 
                **kwargs: Any
            ) -> Machine: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                machine_name: str, 
                *, 
                expand: Optional[Union[str, InstanceViewTypes]] = ..., 
                **kwargs: Any
            ) -> Machine: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                expand: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Machine]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[Machine]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                machine_name: str, 
                parameters: MachineUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Machine: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                machine_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Machine: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                machine_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Machine: ...


    class azure.mgmt.hybridcompute.operations.NetworkProfileOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                machine_name: str, 
                **kwargs: Any
            ) -> NetworkProfile: ...


    class azure.mgmt.hybridcompute.operations.NetworkSecurityPerimeterConfigurationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_reconcile_for_private_link_scope(
                self, 
                resource_group_name: str, 
                scope_name: str, 
                perimeter_name: str, 
                **kwargs: Any
            ) -> LROPoller[NetworkSecurityPerimeterConfigurationReconcileResult]: ...

        @distributed_trace
        def get_by_private_link_scope(
                self, 
                resource_group_name: str, 
                scope_name: str, 
                perimeter_name: str, 
                **kwargs: Any
            ) -> NetworkSecurityPerimeterConfiguration: ...

        @distributed_trace
        def list_by_private_link_scope(
                self, 
                resource_group_name: str, 
                scope_name: str, 
                **kwargs: Any
            ) -> ItemPaged[NetworkSecurityPerimeterConfiguration]: ...


    class azure.mgmt.hybridcompute.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[OperationValue]: ...


    class azure.mgmt.hybridcompute.operations.PrivateEndpointConnectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                scope_name: str, 
                private_endpoint_connection_name: str, 
                parameters: PrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrivateEndpointConnection]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                scope_name: str, 
                private_endpoint_connection_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrivateEndpointConnection]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                scope_name: str, 
                private_endpoint_connection_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrivateEndpointConnection]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                scope_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                scope_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @distributed_trace
        def list_by_private_link_scope(
                self, 
                resource_group_name: str, 
                scope_name: str, 
                **kwargs: Any
            ) -> ItemPaged[PrivateEndpointConnection]: ...


    class azure.mgmt.hybridcompute.operations.PrivateLinkResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                scope_name: str, 
                group_name: str, 
                **kwargs: Any
            ) -> PrivateLinkResource: ...

        @distributed_trace
        def list_by_private_link_scope(
                self, 
                resource_group_name: str, 
                scope_name: str, 
                **kwargs: Any
            ) -> ItemPaged[PrivateLinkResource]: ...


    class azure.mgmt.hybridcompute.operations.PrivateLinkScopesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                scope_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                scope_name: str, 
                parameters: HybridComputePrivateLinkScope, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> HybridComputePrivateLinkScope: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                scope_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> HybridComputePrivateLinkScope: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                scope_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> HybridComputePrivateLinkScope: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                scope_name: str, 
                **kwargs: Any
            ) -> HybridComputePrivateLinkScope: ...

        @distributed_trace
        def get_validation_details(
                self, 
                location: str, 
                private_link_scope_id: str, 
                **kwargs: Any
            ) -> PrivateLinkScopeValidationDetails: ...

        @distributed_trace
        def get_validation_details_for_machine(
                self, 
                resource_group_name: str, 
                machine_name: str, 
                **kwargs: Any
            ) -> PrivateLinkScopeValidationDetails: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[HybridComputePrivateLinkScope]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[HybridComputePrivateLinkScope]: ...

        @overload
        def update_tags(
                self, 
                resource_group_name: str, 
                scope_name: str, 
                private_link_scope_tags: TagsResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> HybridComputePrivateLinkScope: ...

        @overload
        def update_tags(
                self, 
                resource_group_name: str, 
                scope_name: str, 
                private_link_scope_tags: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> HybridComputePrivateLinkScope: ...

        @overload
        def update_tags(
                self, 
                resource_group_name: str, 
                scope_name: str, 
                private_link_scope_tags: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> HybridComputePrivateLinkScope: ...


    class azure.mgmt.hybridcompute.operations.SettingsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                base_provider: str, 
                base_resource_type: str, 
                base_resource_name: str, 
                settings_resource_name: str, 
                **kwargs: Any
            ) -> Settings: ...

        @overload
        def patch(
                self, 
                resource_group_name: str, 
                base_provider: str, 
                base_resource_type: str, 
                base_resource_name: str, 
                settings_resource_name: str, 
                parameters: Settings, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Settings: ...

        @overload
        def patch(
                self, 
                resource_group_name: str, 
                base_provider: str, 
                base_resource_type: str, 
                base_resource_name: str, 
                settings_resource_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Settings: ...

        @overload
        def patch(
                self, 
                resource_group_name: str, 
                base_provider: str, 
                base_resource_type: str, 
                base_resource_name: str, 
                settings_resource_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Settings: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                base_provider: str, 
                base_resource_type: str, 
                base_resource_name: str, 
                settings_resource_name: str, 
                parameters: Settings, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Settings: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                base_provider: str, 
                base_resource_type: str, 
                base_resource_name: str, 
                settings_resource_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Settings: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                base_provider: str, 
                base_resource_type: str, 
                base_resource_name: str, 
                settings_resource_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Settings: ...


```