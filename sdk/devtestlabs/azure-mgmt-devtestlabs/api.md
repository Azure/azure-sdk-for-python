```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.devtestlabs

    class azure.mgmt.devtestlabs.DevTestLabsClient: implements ContextManager 
        arm_templates: ArmTemplatesOperations
        artifact_sources: ArtifactSourcesOperations
        artifacts: ArtifactsOperations
        costs: CostsOperations
        custom_images: CustomImagesOperations
        disks: DisksOperations
        environments: EnvironmentsOperations
        formulas: FormulasOperations
        gallery_images: GalleryImagesOperations
        global_schedules: GlobalSchedulesOperations
        labs: LabsOperations
        notification_channels: NotificationChannelsOperations
        operations: Operations
        policies: PoliciesOperations
        policy_sets: PolicySetsOperations
        provider_operations: ProviderOperationsOperations
        schedules: SchedulesOperations
        secrets: SecretsOperations
        service_fabric_schedules: ServiceFabricSchedulesOperations
        service_fabrics: ServiceFabricsOperations
        service_runners: ServiceRunnersOperations
        users: UsersOperations
        virtual_machine_schedules: VirtualMachineSchedulesOperations
        virtual_machines: VirtualMachinesOperations
        virtual_networks: VirtualNetworksOperations

        def __init__(
                self, 
                credential: TokenCredential, 
                subscription_id: str, 
                base_url: str = "https://management.azure.com", 
                *, 
                api_version: str = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def close(self) -> None: ...


namespace azure.mgmt.devtestlabs.aio

    class azure.mgmt.devtestlabs.aio.DevTestLabsClient: implements AsyncContextManager 
        arm_templates: ArmTemplatesOperations
        artifact_sources: ArtifactSourcesOperations
        artifacts: ArtifactsOperations
        costs: CostsOperations
        custom_images: CustomImagesOperations
        disks: DisksOperations
        environments: EnvironmentsOperations
        formulas: FormulasOperations
        gallery_images: GalleryImagesOperations
        global_schedules: GlobalSchedulesOperations
        labs: LabsOperations
        notification_channels: NotificationChannelsOperations
        operations: Operations
        policies: PoliciesOperations
        policy_sets: PolicySetsOperations
        provider_operations: ProviderOperationsOperations
        schedules: SchedulesOperations
        secrets: SecretsOperations
        service_fabric_schedules: ServiceFabricSchedulesOperations
        service_fabrics: ServiceFabricsOperations
        service_runners: ServiceRunnersOperations
        users: UsersOperations
        virtual_machine_schedules: VirtualMachineSchedulesOperations
        virtual_machines: VirtualMachinesOperations
        virtual_networks: VirtualNetworksOperations

        def __init__(
                self, 
                credential: AsyncTokenCredential, 
                subscription_id: str, 
                base_url: str = "https://management.azure.com", 
                *, 
                api_version: str = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        async def close(self) -> None: ...


namespace azure.mgmt.devtestlabs.aio.operations

    class azure.mgmt.devtestlabs.aio.operations.ArmTemplatesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                artifact_source_name: str, 
                name: str, 
                expand: Optional[str] = None, 
                **kwargs: Any
            ) -> ArmTemplate: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                artifact_source_name: str, 
                expand: Optional[str] = None, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                orderby: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncIterable[ArmTemplate]: ...


    class azure.mgmt.devtestlabs.aio.operations.ArtifactSourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                artifact_source: ArtifactSource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ArtifactSource: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                artifact_source: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ArtifactSource: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                expand: Optional[str] = None, 
                **kwargs: Any
            ) -> ArtifactSource: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                expand: Optional[str] = None, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                orderby: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncIterable[ArtifactSource]: ...

        @distributed_trace_async
        async def update(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                tags: Optional[Dict[str, str]] = None, 
                **kwargs: Any
            ) -> ArtifactSource: ...


    class azure.mgmt.devtestlabs.aio.operations.ArtifactsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def generate_arm_template(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                artifact_source_name: str, 
                name: str, 
                generate_arm_template_request: GenerateArmTemplateRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ArmTemplateInfo: ...

        @overload
        async def generate_arm_template(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                artifact_source_name: str, 
                name: str, 
                generate_arm_template_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ArmTemplateInfo: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                artifact_source_name: str, 
                name: str, 
                expand: Optional[str] = None, 
                **kwargs: Any
            ) -> Artifact: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                artifact_source_name: str, 
                expand: Optional[str] = None, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                orderby: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncIterable[Artifact]: ...


    class azure.mgmt.devtestlabs.aio.operations.CostsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                lab_cost: LabCost, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LabCost: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                lab_cost: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LabCost: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                expand: Optional[str] = None, 
                **kwargs: Any
            ) -> LabCost: ...


    class azure.mgmt.devtestlabs.aio.operations.CustomImagesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                custom_image: CustomImage, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CustomImage]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                custom_image: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CustomImage]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                expand: Optional[str] = None, 
                **kwargs: Any
            ) -> CustomImage: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                expand: Optional[str] = None, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                orderby: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncIterable[CustomImage]: ...

        @distributed_trace_async
        async def update(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                tags: Optional[Dict[str, str]] = None, 
                **kwargs: Any
            ) -> CustomImage: ...


    class azure.mgmt.devtestlabs.aio.operations.DisksOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_attach(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                user_name: str, 
                name: str, 
                leased_by_lab_vm_id: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                user_name: str, 
                name: str, 
                disk: Disk, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Disk]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                user_name: str, 
                name: str, 
                disk: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Disk]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                user_name: str, 
                name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_detach(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                user_name: str, 
                name: str, 
                leased_by_lab_vm_id: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                user_name: str, 
                name: str, 
                expand: Optional[str] = None, 
                **kwargs: Any
            ) -> Disk: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                user_name: str, 
                expand: Optional[str] = None, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                orderby: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncIterable[Disk]: ...

        @distributed_trace_async
        async def update(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                user_name: str, 
                name: str, 
                tags: Optional[Dict[str, str]] = None, 
                **kwargs: Any
            ) -> Disk: ...


    class azure.mgmt.devtestlabs.aio.operations.EnvironmentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                user_name: str, 
                name: str, 
                dtl_environment: DtlEnvironment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DtlEnvironment]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                user_name: str, 
                name: str, 
                dtl_environment: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DtlEnvironment]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                user_name: str, 
                name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                user_name: str, 
                name: str, 
                expand: Optional[str] = None, 
                **kwargs: Any
            ) -> DtlEnvironment: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                user_name: str, 
                expand: Optional[str] = None, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                orderby: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncIterable[DtlEnvironment]: ...

        @distributed_trace_async
        async def update(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                user_name: str, 
                name: str, 
                tags: Optional[Dict[str, str]] = None, 
                **kwargs: Any
            ) -> DtlEnvironment: ...


    class azure.mgmt.devtestlabs.aio.operations.FormulasOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                formula: Formula, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Formula]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                formula: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Formula]: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                expand: Optional[str] = None, 
                **kwargs: Any
            ) -> Formula: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                expand: Optional[str] = None, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                orderby: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncIterable[Formula]: ...

        @distributed_trace_async
        async def update(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                tags: Optional[Dict[str, str]] = None, 
                **kwargs: Any
            ) -> Formula: ...


    class azure.mgmt.devtestlabs.aio.operations.GalleryImagesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                expand: Optional[str] = None, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                orderby: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncIterable[GalleryImage]: ...


    class azure.mgmt.devtestlabs.aio.operations.GlobalSchedulesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_execute(
                self, 
                resource_group_name: str, 
                name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_retarget(
                self, 
                resource_group_name: str, 
                name: str, 
                current_resource_id: Optional[str] = None, 
                target_resource_id: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                name: str, 
                schedule: Schedule, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Schedule: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                name: str, 
                schedule: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Schedule: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                name: str, 
                expand: Optional[str] = None, 
                **kwargs: Any
            ) -> Schedule: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                expand: Optional[str] = None, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                orderby: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncIterable[Schedule]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                expand: Optional[str] = None, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                orderby: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncIterable[Schedule]: ...

        @distributed_trace_async
        async def update(
                self, 
                resource_group_name: str, 
                name: str, 
                tags: Optional[Dict[str, str]] = None, 
                **kwargs: Any
            ) -> Schedule: ...


    class azure.mgmt.devtestlabs.aio.operations.LabsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_claim_any_vm(
                self, 
                resource_group_name: str, 
                name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_create_environment(
                self, 
                resource_group_name: str, 
                name: str, 
                lab_virtual_machine_creation_parameter: LabVirtualMachineCreationParameter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_create_environment(
                self, 
                resource_group_name: str, 
                name: str, 
                lab_virtual_machine_creation_parameter: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                name: str, 
                lab: Lab, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Lab]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                name: str, 
                lab: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Lab]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_export_resource_usage(
                self, 
                resource_group_name: str, 
                name: str, 
                blob_storage_absolute_sas_uri: Optional[str] = None, 
                usage_start_date: Optional[datetime] = None, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_import_virtual_machine(
                self, 
                resource_group_name: str, 
                name: str, 
                source_virtual_machine_resource_id: Optional[str] = None, 
                destination_virtual_machine_name: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def generate_upload_uri(
                self, 
                resource_group_name: str, 
                name: str, 
                blob_name: Optional[str] = None, 
                **kwargs: Any
            ) -> GenerateUploadUriResponse: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                name: str, 
                expand: Optional[str] = None, 
                **kwargs: Any
            ) -> Lab: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                expand: Optional[str] = None, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                orderby: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncIterable[Lab]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                expand: Optional[str] = None, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                orderby: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncIterable[Lab]: ...

        @distributed_trace
        def list_vhds(
                self, 
                resource_group_name: str, 
                name: str, 
                **kwargs: Any
            ) -> AsyncIterable[LabVhd]: ...

        @distributed_trace_async
        async def update(
                self, 
                resource_group_name: str, 
                name: str, 
                tags: Optional[Dict[str, str]] = None, 
                **kwargs: Any
            ) -> Lab: ...


    class azure.mgmt.devtestlabs.aio.operations.NotificationChannelsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                notification_channel: NotificationChannel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> NotificationChannel: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                notification_channel: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> NotificationChannel: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                expand: Optional[str] = None, 
                **kwargs: Any
            ) -> NotificationChannel: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                expand: Optional[str] = None, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                orderby: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncIterable[NotificationChannel]: ...

        @distributed_trace_async
        async def notify(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                event_name: Optional[Union[str, NotificationChannelEventType]] = None, 
                json_payload: Optional[str] = None, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def update(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                tags: Optional[Dict[str, str]] = None, 
                **kwargs: Any
            ) -> NotificationChannel: ...


    class azure.mgmt.devtestlabs.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                location_name: str, 
                name: str, 
                **kwargs: Any
            ) -> OperationResult: ...


    class azure.mgmt.devtestlabs.aio.operations.PoliciesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                policy_set_name: str, 
                name: str, 
                policy: Policy, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Policy: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                policy_set_name: str, 
                name: str, 
                policy: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Policy: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                policy_set_name: str, 
                name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                policy_set_name: str, 
                name: str, 
                expand: Optional[str] = None, 
                **kwargs: Any
            ) -> Policy: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                policy_set_name: str, 
                expand: Optional[str] = None, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                orderby: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncIterable[Policy]: ...

        @distributed_trace_async
        async def update(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                policy_set_name: str, 
                name: str, 
                tags: Optional[Dict[str, str]] = None, 
                **kwargs: Any
            ) -> Policy: ...


    class azure.mgmt.devtestlabs.aio.operations.PolicySetsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def evaluate_policies(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                policies: Optional[List[EvaluatePoliciesProperties]] = None, 
                **kwargs: Any
            ) -> EvaluatePoliciesResponse: ...


    class azure.mgmt.devtestlabs.aio.operations.ProviderOperationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncIterable[OperationMetadata]: ...


    class azure.mgmt.devtestlabs.aio.operations.SchedulesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_execute(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                schedule: Schedule, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Schedule: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                schedule: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Schedule: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                expand: Optional[str] = None, 
                **kwargs: Any
            ) -> Schedule: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                expand: Optional[str] = None, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                orderby: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncIterable[Schedule]: ...

        @distributed_trace
        def list_applicable(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                **kwargs: Any
            ) -> AsyncIterable[Schedule]: ...

        @distributed_trace_async
        async def update(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                tags: Optional[Dict[str, str]] = None, 
                **kwargs: Any
            ) -> Schedule: ...


    class azure.mgmt.devtestlabs.aio.operations.SecretsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                user_name: str, 
                name: str, 
                secret: Secret, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Secret]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                user_name: str, 
                name: str, 
                secret: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Secret]: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                user_name: str, 
                name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                user_name: str, 
                name: str, 
                expand: Optional[str] = None, 
                **kwargs: Any
            ) -> Secret: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                user_name: str, 
                expand: Optional[str] = None, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                orderby: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncIterable[Secret]: ...

        @distributed_trace_async
        async def update(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                user_name: str, 
                name: str, 
                tags: Optional[Dict[str, str]] = None, 
                **kwargs: Any
            ) -> Secret: ...


    class azure.mgmt.devtestlabs.aio.operations.ServiceFabricSchedulesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_execute(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                user_name: str, 
                service_fabric_name: str, 
                name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                user_name: str, 
                service_fabric_name: str, 
                name: str, 
                schedule: Schedule, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Schedule: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                user_name: str, 
                service_fabric_name: str, 
                name: str, 
                schedule: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Schedule: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                user_name: str, 
                service_fabric_name: str, 
                name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                user_name: str, 
                service_fabric_name: str, 
                name: str, 
                expand: Optional[str] = None, 
                **kwargs: Any
            ) -> Schedule: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                user_name: str, 
                service_fabric_name: str, 
                expand: Optional[str] = None, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                orderby: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncIterable[Schedule]: ...

        @distributed_trace_async
        async def update(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                user_name: str, 
                service_fabric_name: str, 
                name: str, 
                tags: Optional[Dict[str, str]] = None, 
                **kwargs: Any
            ) -> Schedule: ...


    class azure.mgmt.devtestlabs.aio.operations.ServiceFabricsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                user_name: str, 
                name: str, 
                service_fabric: ServiceFabric, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ServiceFabric]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                user_name: str, 
                name: str, 
                service_fabric: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ServiceFabric]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                user_name: str, 
                name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_start(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                user_name: str, 
                name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_stop(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                user_name: str, 
                name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                user_name: str, 
                name: str, 
                expand: Optional[str] = None, 
                **kwargs: Any
            ) -> ServiceFabric: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                user_name: str, 
                expand: Optional[str] = None, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                orderby: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncIterable[ServiceFabric]: ...

        @distributed_trace_async
        async def list_applicable_schedules(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                user_name: str, 
                name: str, 
                **kwargs: Any
            ) -> ApplicableSchedule: ...

        @distributed_trace_async
        async def update(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                user_name: str, 
                name: str, 
                tags: Optional[Dict[str, str]] = None, 
                **kwargs: Any
            ) -> ServiceFabric: ...


    class azure.mgmt.devtestlabs.aio.operations.ServiceRunnersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                service_runner: ServiceRunner, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ServiceRunner: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                service_runner: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ServiceRunner: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                **kwargs: Any
            ) -> ServiceRunner: ...


    class azure.mgmt.devtestlabs.aio.operations.UsersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                user: User, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[User]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                user: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[User]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                expand: Optional[str] = None, 
                **kwargs: Any
            ) -> User: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                expand: Optional[str] = None, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                orderby: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncIterable[User]: ...

        @distributed_trace_async
        async def update(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                tags: Optional[Dict[str, str]] = None, 
                **kwargs: Any
            ) -> User: ...


    class azure.mgmt.devtestlabs.aio.operations.VirtualMachineSchedulesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_execute(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                virtual_machine_name: str, 
                name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                virtual_machine_name: str, 
                name: str, 
                schedule: Schedule, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Schedule: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                virtual_machine_name: str, 
                name: str, 
                schedule: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Schedule: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                virtual_machine_name: str, 
                name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                virtual_machine_name: str, 
                name: str, 
                expand: Optional[str] = None, 
                **kwargs: Any
            ) -> Schedule: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                virtual_machine_name: str, 
                expand: Optional[str] = None, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                orderby: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncIterable[Schedule]: ...

        @distributed_trace_async
        async def update(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                virtual_machine_name: str, 
                name: str, 
                tags: Optional[Dict[str, str]] = None, 
                **kwargs: Any
            ) -> Schedule: ...


    class azure.mgmt.devtestlabs.aio.operations.VirtualMachinesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_add_data_disk(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                data_disk_properties: DataDiskProperties, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_add_data_disk(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                data_disk_properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_apply_artifacts(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                artifacts: Optional[List[ArtifactInstallProperties]] = None, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_claim(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                lab_virtual_machine: LabVirtualMachine, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[LabVirtualMachine]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                lab_virtual_machine: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[LabVirtualMachine]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_detach_data_disk(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                existing_lab_disk_id: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_redeploy(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_resize(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                size: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_restart(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_start(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_stop(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_transfer_disks(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_un_claim(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                expand: Optional[str] = None, 
                **kwargs: Any
            ) -> LabVirtualMachine: ...

        @distributed_trace_async
        async def get_rdp_file_contents(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                **kwargs: Any
            ) -> RdpConnection: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                expand: Optional[str] = None, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                orderby: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncIterable[LabVirtualMachine]: ...

        @distributed_trace_async
        async def list_applicable_schedules(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                **kwargs: Any
            ) -> ApplicableSchedule: ...

        @distributed_trace_async
        async def update(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                tags: Optional[Dict[str, str]] = None, 
                **kwargs: Any
            ) -> LabVirtualMachine: ...


    class azure.mgmt.devtestlabs.aio.operations.VirtualNetworksOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                virtual_network: VirtualNetwork, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualNetwork]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                virtual_network: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualNetwork]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                expand: Optional[str] = None, 
                **kwargs: Any
            ) -> VirtualNetwork: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                expand: Optional[str] = None, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                orderby: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncIterable[VirtualNetwork]: ...

        @distributed_trace_async
        async def update(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                tags: Optional[Dict[str, str]] = None, 
                **kwargs: Any
            ) -> VirtualNetwork: ...


namespace azure.mgmt.devtestlabs.models

    class azure.mgmt.devtestlabs.models.ApplicableSchedule(Resource):
        id: str
        lab_vms_shutdown: Schedule
        lab_vms_startup: Schedule
        location: str
        name: str
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                lab_vms_shutdown: Optional[Schedule] = ..., 
                lab_vms_startup: Optional[Schedule] = ..., 
                location: Optional[str] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.ApplicableScheduleFragment(UpdateResource):
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.ApplyArtifactsRequest(Model):
        artifacts: list[ArtifactInstallProperties]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                artifacts: Optional[List[ArtifactInstallProperties]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.ArmTemplate(Resource):
        contents: JSON
        created_date: datetime
        description: str
        display_name: str
        enabled: bool
        icon: str
        id: str
        location: str
        name: str
        parameters_value_files_info: list[ParametersValueFileInfo]
        publisher: str
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.ArmTemplateInfo(Model):
        parameters: JSON
        template: JSON

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                parameters: Optional[JSON] = ..., 
                template: Optional[JSON] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.ArmTemplateList(Model):
        next_link: str
        value: list[ArmTemplate]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[ArmTemplate]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.ArmTemplateParameterProperties(Model):
        name: str
        value: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                value: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.Artifact(Resource):
        created_date: datetime
        description: str
        file_path: str
        icon: str
        id: str
        location: str
        name: str
        parameters: JSON
        publisher: str
        tags: dict[str, str]
        target_os_type: str
        title: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.ArtifactDeploymentStatusProperties(Model):
        artifacts_applied: int
        deployment_status: str
        total_artifacts: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                artifacts_applied: Optional[int] = ..., 
                deployment_status: Optional[str] = ..., 
                total_artifacts: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.ArtifactInstallProperties(Model):
        artifact_id: str
        artifact_title: str
        deployment_status_message: str
        install_time: datetime
        parameters: list[ArtifactParameterProperties]
        status: str
        vm_extension_status_message: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                artifact_id: Optional[str] = ..., 
                artifact_title: Optional[str] = ..., 
                deployment_status_message: Optional[str] = ..., 
                install_time: Optional[datetime] = ..., 
                parameters: Optional[List[ArtifactParameterProperties]] = ..., 
                status: Optional[str] = ..., 
                vm_extension_status_message: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.ArtifactList(Model):
        next_link: str
        value: list[Artifact]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[Artifact]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.ArtifactParameterProperties(Model):
        name: str
        value: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                value: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.ArtifactSource(Resource):
        arm_template_folder_path: str
        branch_ref: str
        created_date: datetime
        display_name: str
        folder_path: str
        id: str
        location: str
        name: str
        provisioning_state: str
        security_token: str
        source_type: Union[str, SourceControlType]
        status: Union[str, EnableStatus]
        tags: dict[str, str]
        type: str
        unique_identifier: str
        uri: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                arm_template_folder_path: Optional[str] = ..., 
                branch_ref: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                folder_path: Optional[str] = ..., 
                location: Optional[str] = ..., 
                security_token: Optional[str] = ..., 
                source_type: Optional[Union[str, SourceControlType]] = ..., 
                status: Optional[Union[str, EnableStatus]] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                uri: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.ArtifactSourceFragment(UpdateResource):
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.ArtifactSourceList(Model):
        next_link: str
        value: list[ArtifactSource]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[ArtifactSource]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.AttachDiskProperties(Model):
        leased_by_lab_vm_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                leased_by_lab_vm_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.AttachNewDataDiskOptions(Model):
        disk_name: str
        disk_size_gi_b: int
        disk_type: Union[str, StorageType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                disk_name: Optional[str] = ..., 
                disk_size_gi_b: Optional[int] = ..., 
                disk_type: Optional[Union[str, StorageType]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.BulkCreationParameters(Model):
        instance_count: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                instance_count: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.CloudErrorBody(Model):
        code: str
        details: list[CloudErrorBody]
        message: str
        target: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                details: Optional[List[CloudErrorBody]] = ..., 
                message: Optional[str] = ..., 
                target: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.ComputeDataDisk(Model):
        disk_size_gi_b: int
        disk_uri: str
        managed_disk_id: str
        name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                disk_size_gi_b: Optional[int] = ..., 
                disk_uri: Optional[str] = ..., 
                managed_disk_id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.ComputeVmInstanceViewStatus(Model):
        code: str
        display_status: str
        message: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                display_status: Optional[str] = ..., 
                message: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.ComputeVmProperties(Model):
        data_disk_ids: list[str]
        data_disks: list[ComputeDataDisk]
        network_interface_id: str
        os_disk_id: str
        os_type: str
        statuses: list[ComputeVmInstanceViewStatus]
        vm_size: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                data_disk_ids: Optional[List[str]] = ..., 
                data_disks: Optional[List[ComputeDataDisk]] = ..., 
                network_interface_id: Optional[str] = ..., 
                os_disk_id: Optional[str] = ..., 
                os_type: Optional[str] = ..., 
                statuses: Optional[List[ComputeVmInstanceViewStatus]] = ..., 
                vm_size: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.CostThresholdProperties(Model):
        display_on_chart: Union[str, CostThresholdStatus]
        notification_sent: str
        percentage_threshold: PercentageCostThresholdProperties
        send_notification_when_exceeded: Union[str, CostThresholdStatus]
        threshold_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                display_on_chart: Optional[Union[str, CostThresholdStatus]] = ..., 
                notification_sent: Optional[str] = ..., 
                percentage_threshold: Optional[PercentageCostThresholdProperties] = ..., 
                send_notification_when_exceeded: Optional[Union[str, CostThresholdStatus]] = ..., 
                threshold_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.CostThresholdStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.devtestlabs.models.CostType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PROJECTED = "Projected"
        REPORTED = "Reported"
        UNAVAILABLE = "Unavailable"


    class azure.mgmt.devtestlabs.models.CustomImage(Resource):
        author: str
        creation_date: datetime
        custom_image_plan: CustomImagePropertiesFromPlan
        data_disk_storage_info: list[DataDiskStorageTypeInfo]
        description: str
        id: str
        is_plan_authorized: bool
        location: str
        managed_image_id: str
        managed_snapshot_id: str
        name: str
        provisioning_state: str
        tags: dict[str, str]
        type: str
        unique_identifier: str
        vhd: CustomImagePropertiesCustom
        vm: CustomImagePropertiesFromVm

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                author: Optional[str] = ..., 
                custom_image_plan: Optional[CustomImagePropertiesFromPlan] = ..., 
                data_disk_storage_info: Optional[List[DataDiskStorageTypeInfo]] = ..., 
                description: Optional[str] = ..., 
                is_plan_authorized: Optional[bool] = ..., 
                location: Optional[str] = ..., 
                managed_image_id: Optional[str] = ..., 
                managed_snapshot_id: Optional[str] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                vhd: Optional[CustomImagePropertiesCustom] = ..., 
                vm: Optional[CustomImagePropertiesFromVm] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.CustomImageFragment(UpdateResource):
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.CustomImageList(Model):
        next_link: str
        value: list[CustomImage]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[CustomImage]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.CustomImageOsType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LINUX = "Linux"
        NONE = "None"
        WINDOWS = "Windows"


    class azure.mgmt.devtestlabs.models.CustomImagePropertiesCustom(Model):
        image_name: str
        os_type: Union[str, CustomImageOsType]
        sys_prep: bool

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                image_name: Optional[str] = ..., 
                os_type: Union[str, CustomImageOsType], 
                sys_prep: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.CustomImagePropertiesFromPlan(Model):
        id: str
        offer: str
        publisher: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                offer: Optional[str] = ..., 
                publisher: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.CustomImagePropertiesFromVm(Model):
        linux_os_info: LinuxOsInfo
        source_vm_id: str
        windows_os_info: WindowsOsInfo

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                linux_os_info: Optional[LinuxOsInfo] = ..., 
                source_vm_id: Optional[str] = ..., 
                windows_os_info: Optional[WindowsOsInfo] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.DataDiskProperties(Model):
        attach_new_data_disk_options: AttachNewDataDiskOptions
        existing_lab_disk_id: str
        host_caching: Union[str, HostCachingOptions]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                attach_new_data_disk_options: Optional[AttachNewDataDiskOptions] = ..., 
                existing_lab_disk_id: Optional[str] = ..., 
                host_caching: Optional[Union[str, HostCachingOptions]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.DataDiskStorageTypeInfo(Model):
        lun: str
        storage_type: Union[str, StorageType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                lun: Optional[str] = ..., 
                storage_type: Optional[Union[str, StorageType]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.DayDetails(Model):
        time: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                time: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.DetachDataDiskProperties(Model):
        existing_lab_disk_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                existing_lab_disk_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.DetachDiskProperties(Model):
        leased_by_lab_vm_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                leased_by_lab_vm_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.Disk(Resource):
        created_date: datetime
        disk_blob_name: str
        disk_size_gi_b: int
        disk_type: Union[str, StorageType]
        disk_uri: str
        host_caching: str
        id: str
        leased_by_lab_vm_id: str
        location: str
        managed_disk_id: str
        name: str
        provisioning_state: str
        storage_account_id: str
        tags: dict[str, str]
        type: str
        unique_identifier: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                disk_blob_name: Optional[str] = ..., 
                disk_size_gi_b: Optional[int] = ..., 
                disk_type: Optional[Union[str, StorageType]] = ..., 
                disk_uri: Optional[str] = ..., 
                host_caching: Optional[str] = ..., 
                leased_by_lab_vm_id: Optional[str] = ..., 
                location: Optional[str] = ..., 
                managed_disk_id: Optional[str] = ..., 
                storage_account_id: Optional[str] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.DiskFragment(UpdateResource):
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.DiskList(Model):
        next_link: str
        value: list[Disk]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[Disk]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.DtlEnvironment(Resource):
        arm_template_display_name: str
        created_by_user: str
        deployment_properties: EnvironmentDeploymentProperties
        id: str
        location: str
        name: str
        provisioning_state: str
        resource_group_id: str
        tags: dict[str, str]
        type: str
        unique_identifier: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                arm_template_display_name: Optional[str] = ..., 
                deployment_properties: Optional[EnvironmentDeploymentProperties] = ..., 
                location: Optional[str] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.DtlEnvironmentFragment(UpdateResource):
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.DtlEnvironmentList(Model):
        next_link: str
        value: list[DtlEnvironment]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[DtlEnvironment]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.EnableStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.devtestlabs.models.EnvironmentDeploymentProperties(Model):
        arm_template_id: str
        parameters: list[ArmTemplateParameterProperties]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                arm_template_id: Optional[str] = ..., 
                parameters: Optional[List[ArmTemplateParameterProperties]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.EnvironmentPermission(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONTRIBUTOR = "Contributor"
        READER = "Reader"


    class azure.mgmt.devtestlabs.models.EvaluatePoliciesProperties(Model):
        fact_data: str
        fact_name: str
        user_object_id: str
        value_offset: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                fact_data: Optional[str] = ..., 
                fact_name: Optional[str] = ..., 
                user_object_id: Optional[str] = ..., 
                value_offset: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.EvaluatePoliciesRequest(Model):
        policies: list[EvaluatePoliciesProperties]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                policies: Optional[List[EvaluatePoliciesProperties]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.EvaluatePoliciesResponse(Model):
        results: list[PolicySetResult]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                results: Optional[List[PolicySetResult]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.Event(Model):
        event_name: Union[str, NotificationChannelEventType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                event_name: Optional[Union[str, NotificationChannelEventType]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.ExportResourceUsageParameters(Model):
        blob_storage_absolute_sas_uri: str
        usage_start_date: datetime

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                blob_storage_absolute_sas_uri: Optional[str] = ..., 
                usage_start_date: Optional[datetime] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.ExternalSubnet(Model):
        id: str
        name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.FileUploadOptions(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        UPLOAD_FILES_AND_GENERATE_SAS_TOKENS = "UploadFilesAndGenerateSasTokens"


    class azure.mgmt.devtestlabs.models.Formula(Resource):
        author: str
        creation_date: datetime
        description: str
        formula_content: LabVirtualMachineCreationParameter
        id: str
        location: str
        name: str
        os_type: str
        provisioning_state: str
        tags: dict[str, str]
        type: str
        unique_identifier: str
        vm: FormulaPropertiesFromVm

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                formula_content: Optional[LabVirtualMachineCreationParameter] = ..., 
                location: Optional[str] = ..., 
                os_type: Optional[str] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                vm: Optional[FormulaPropertiesFromVm] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.FormulaFragment(UpdateResource):
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.FormulaList(Model):
        next_link: str
        value: list[Formula]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[Formula]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.FormulaPropertiesFromVm(Model):
        lab_vm_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                lab_vm_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.GalleryImage(Resource):
        author: str
        created_date: datetime
        description: str
        enabled: bool
        icon: str
        id: str
        image_reference: GalleryImageReference
        is_plan_authorized: bool
        location: str
        name: str
        plan_id: str
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                author: Optional[str] = ..., 
                description: Optional[str] = ..., 
                enabled: Optional[bool] = ..., 
                icon: Optional[str] = ..., 
                image_reference: Optional[GalleryImageReference] = ..., 
                is_plan_authorized: Optional[bool] = ..., 
                location: Optional[str] = ..., 
                plan_id: Optional[str] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.GalleryImageList(Model):
        next_link: str
        value: list[GalleryImage]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[GalleryImage]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.GalleryImageReference(Model):
        offer: str
        os_type: str
        publisher: str
        sku: str
        version: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                offer: Optional[str] = ..., 
                os_type: Optional[str] = ..., 
                publisher: Optional[str] = ..., 
                sku: Optional[str] = ..., 
                version: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.GenerateArmTemplateRequest(Model):
        file_upload_options: Union[str, FileUploadOptions]
        location: str
        parameters: list[ParameterInfo]
        virtual_machine_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                file_upload_options: Optional[Union[str, FileUploadOptions]] = ..., 
                location: Optional[str] = ..., 
                parameters: Optional[List[ParameterInfo]] = ..., 
                virtual_machine_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.GenerateUploadUriParameter(Model):
        blob_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                blob_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.GenerateUploadUriResponse(Model):
        upload_uri: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                upload_uri: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.HostCachingOptions(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        READ_ONLY = "ReadOnly"
        READ_WRITE = "ReadWrite"


    class azure.mgmt.devtestlabs.models.HourDetails(Model):
        minute: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                minute: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.HttpStatusCode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        AMBIGUOUS = "Ambiguous"
        BAD_GATEWAY = "BadGateway"
        BAD_REQUEST = "BadRequest"
        CONFLICT = "Conflict"
        CONTINUE = "Continue"
        CONTINUE_ENUM = "Continue"
        CREATED = "Created"
        EXPECTATION_FAILED = "ExpectationFailed"
        FORBIDDEN = "Forbidden"
        FOUND = "Found"
        GATEWAY_TIMEOUT = "GatewayTimeout"
        GONE = "Gone"
        HTTP_VERSION_NOT_SUPPORTED = "HttpVersionNotSupported"
        INTERNAL_SERVER_ERROR = "InternalServerError"
        LENGTH_REQUIRED = "LengthRequired"
        METHOD_NOT_ALLOWED = "MethodNotAllowed"
        MOVED = "Moved"
        MOVED_PERMANENTLY = "MovedPermanently"
        MULTIPLE_CHOICES = "MultipleChoices"
        NON_AUTHORITATIVE_INFORMATION = "NonAuthoritativeInformation"
        NOT_ACCEPTABLE = "NotAcceptable"
        NOT_FOUND = "NotFound"
        NOT_IMPLEMENTED = "NotImplemented"
        NOT_MODIFIED = "NotModified"
        NO_CONTENT = "NoContent"
        OK = "OK"
        PARTIAL_CONTENT = "PartialContent"
        PAYMENT_REQUIRED = "PaymentRequired"
        PRECONDITION_FAILED = "PreconditionFailed"
        PROXY_AUTHENTICATION_REQUIRED = "ProxyAuthenticationRequired"
        REDIRECT = "Redirect"
        REDIRECT_KEEP_VERB = "RedirectKeepVerb"
        REDIRECT_METHOD = "RedirectMethod"
        REQUESTED_RANGE_NOT_SATISFIABLE = "RequestedRangeNotSatisfiable"
        REQUEST_ENTITY_TOO_LARGE = "RequestEntityTooLarge"
        REQUEST_TIMEOUT = "RequestTimeout"
        REQUEST_URI_TOO_LONG = "RequestUriTooLong"
        RESET_CONTENT = "ResetContent"
        SEE_OTHER = "SeeOther"
        SERVICE_UNAVAILABLE = "ServiceUnavailable"
        SWITCHING_PROTOCOLS = "SwitchingProtocols"
        TEMPORARY_REDIRECT = "TemporaryRedirect"
        UNAUTHORIZED = "Unauthorized"
        UNSUPPORTED_MEDIA_TYPE = "UnsupportedMediaType"
        UNUSED = "Unused"
        UPGRADE_REQUIRED = "UpgradeRequired"
        USE_PROXY = "UseProxy"


    class azure.mgmt.devtestlabs.models.IdentityProperties(Model):
        client_secret_url: str
        principal_id: str
        tenant_id: str
        type: Union[str, ManagedIdentityType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                client_secret_url: Optional[str] = ..., 
                principal_id: Optional[str] = ..., 
                tenant_id: Optional[str] = ..., 
                type: Optional[Union[str, ManagedIdentityType]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.ImportLabVirtualMachineRequest(Model):
        destination_virtual_machine_name: str
        source_virtual_machine_resource_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                destination_virtual_machine_name: Optional[str] = ..., 
                source_virtual_machine_resource_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.InboundNatRule(Model):
        backend_port: int
        frontend_port: int
        transport_protocol: Union[str, TransportProtocol]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                backend_port: Optional[int] = ..., 
                frontend_port: Optional[int] = ..., 
                transport_protocol: Optional[Union[str, TransportProtocol]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.Lab(Resource):
        announcement: LabAnnouncementProperties
        artifacts_storage_account: str
        created_date: datetime
        default_premium_storage_account: str
        default_storage_account: str
        environment_permission: Union[str, EnvironmentPermission]
        extended_properties: dict[str, str]
        id: str
        lab_storage_type: Union[str, StorageType]
        load_balancer_id: str
        location: str
        mandatory_artifacts_resource_ids_linux: list[str]
        mandatory_artifacts_resource_ids_windows: list[str]
        name: str
        network_security_group_id: str
        premium_data_disk_storage_account: str
        premium_data_disks: Union[str, PremiumDataDisk]
        provisioning_state: str
        public_ip_id: str
        support: LabSupportProperties
        tags: dict[str, str]
        type: str
        unique_identifier: str
        vault_name: str
        vm_creation_resource_group: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                announcement: Optional[LabAnnouncementProperties] = ..., 
                environment_permission: Optional[Union[str, EnvironmentPermission]] = ..., 
                extended_properties: Optional[Dict[str, str]] = ..., 
                lab_storage_type: Optional[Union[str, StorageType]] = ..., 
                location: Optional[str] = ..., 
                mandatory_artifacts_resource_ids_linux: Optional[List[str]] = ..., 
                mandatory_artifacts_resource_ids_windows: Optional[List[str]] = ..., 
                premium_data_disks: Optional[Union[str, PremiumDataDisk]] = ..., 
                support: Optional[LabSupportProperties] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.LabAnnouncementProperties(Model):
        enabled: Union[str, EnableStatus]
        expiration_date: datetime
        expired: bool
        markdown: str
        provisioning_state: str
        title: str
        unique_identifier: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                enabled: Optional[Union[str, EnableStatus]] = ..., 
                expiration_date: Optional[datetime] = ..., 
                expired: Optional[bool] = ..., 
                markdown: Optional[str] = ..., 
                title: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.LabCost(Resource):
        created_date: datetime
        currency_code: str
        end_date_time: datetime
        id: str
        lab_cost_details: list[LabCostDetailsProperties]
        lab_cost_summary: LabCostSummaryProperties
        location: str
        name: str
        provisioning_state: str
        resource_costs: list[LabResourceCostProperties]
        start_date_time: datetime
        tags: dict[str, str]
        target_cost: TargetCostProperties
        type: str
        unique_identifier: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                created_date: Optional[datetime] = ..., 
                currency_code: Optional[str] = ..., 
                end_date_time: Optional[datetime] = ..., 
                location: Optional[str] = ..., 
                start_date_time: Optional[datetime] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                target_cost: Optional[TargetCostProperties] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.LabCostDetailsProperties(Model):
        cost: float
        cost_type: Union[str, CostType]
        date: datetime

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                cost: Optional[float] = ..., 
                cost_type: Optional[Union[str, CostType]] = ..., 
                date: Optional[datetime] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.LabCostSummaryProperties(Model):
        estimated_lab_cost: float

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                estimated_lab_cost: Optional[float] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.LabFragment(UpdateResource):
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.LabList(Model):
        next_link: str
        value: list[Lab]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[Lab]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.LabResourceCostProperties(Model):
        external_resource_id: str
        resource_cost: float
        resource_id: str
        resource_owner: str
        resource_pricing_tier: str
        resource_status: str
        resource_type: str
        resource_u_id: str
        resourcename: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                external_resource_id: Optional[str] = ..., 
                resource_cost: Optional[float] = ..., 
                resource_id: Optional[str] = ..., 
                resource_owner: Optional[str] = ..., 
                resource_pricing_tier: Optional[str] = ..., 
                resource_status: Optional[str] = ..., 
                resource_type: Optional[str] = ..., 
                resource_u_id: Optional[str] = ..., 
                resourcename: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.LabSupportProperties(Model):
        enabled: Union[str, EnableStatus]
        markdown: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                enabled: Optional[Union[str, EnableStatus]] = ..., 
                markdown: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.LabVhd(Model):
        id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.LabVhdList(Model):
        next_link: str
        value: list[LabVhd]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[LabVhd]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.LabVirtualMachine(Resource):
        allow_claim: bool
        applicable_schedule: ApplicableSchedule
        artifact_deployment_status: ArtifactDeploymentStatusProperties
        artifacts: list[ArtifactInstallProperties]
        compute_id: str
        compute_vm: ComputeVmProperties
        created_by_user: str
        created_by_user_id: str
        created_date: datetime
        custom_image_id: str
        data_disk_parameters: list[DataDiskProperties]
        disallow_public_ip_address: bool
        environment_id: str
        expiration_date: datetime
        fqdn: str
        gallery_image_reference: GalleryImageReference
        id: str
        is_authentication_with_ssh_key: bool
        lab_subnet_name: str
        lab_virtual_network_id: str
        last_known_power_state: str
        location: str
        name: str
        network_interface: NetworkInterfaceProperties
        notes: str
        os_type: str
        owner_object_id: str
        owner_user_principal_name: str
        password: str
        plan_id: str
        provisioning_state: str
        schedule_parameters: list[ScheduleCreationParameter]
        size: str
        ssh_key: str
        storage_type: str
        tags: dict[str, str]
        type: str
        unique_identifier: str
        user_name: str
        virtual_machine_creation_source: Union[str, VirtualMachineCreationSource]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                allow_claim: bool = False, 
                artifacts: Optional[List[ArtifactInstallProperties]] = ..., 
                created_date: Optional[datetime] = ..., 
                custom_image_id: Optional[str] = ..., 
                data_disk_parameters: Optional[List[DataDiskProperties]] = ..., 
                disallow_public_ip_address: bool = False, 
                environment_id: Optional[str] = ..., 
                expiration_date: Optional[datetime] = ..., 
                gallery_image_reference: Optional[GalleryImageReference] = ..., 
                is_authentication_with_ssh_key: Optional[bool] = ..., 
                lab_subnet_name: Optional[str] = ..., 
                lab_virtual_network_id: Optional[str] = ..., 
                location: Optional[str] = ..., 
                network_interface: Optional[NetworkInterfaceProperties] = ..., 
                notes: Optional[str] = ..., 
                owner_object_id: str = "dynamicValue", 
                owner_user_principal_name: Optional[str] = ..., 
                password: Optional[str] = ..., 
                plan_id: Optional[str] = ..., 
                schedule_parameters: Optional[List[ScheduleCreationParameter]] = ..., 
                size: Optional[str] = ..., 
                ssh_key: Optional[str] = ..., 
                storage_type: str = "labStorageType", 
                tags: Optional[Dict[str, str]] = ..., 
                user_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.LabVirtualMachineCreationParameter(Model):
        allow_claim: bool
        artifacts: list[ArtifactInstallProperties]
        bulk_creation_parameters: BulkCreationParameters
        created_date: datetime
        custom_image_id: str
        data_disk_parameters: list[DataDiskProperties]
        disallow_public_ip_address: bool
        environment_id: str
        expiration_date: datetime
        gallery_image_reference: GalleryImageReference
        is_authentication_with_ssh_key: bool
        lab_subnet_name: str
        lab_virtual_network_id: str
        location: str
        name: str
        network_interface: NetworkInterfaceProperties
        notes: str
        owner_object_id: str
        owner_user_principal_name: str
        password: str
        plan_id: str
        schedule_parameters: list[ScheduleCreationParameter]
        size: str
        ssh_key: str
        storage_type: str
        tags: dict[str, str]
        user_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                allow_claim: bool = False, 
                artifacts: Optional[List[ArtifactInstallProperties]] = ..., 
                bulk_creation_parameters: Optional[BulkCreationParameters] = ..., 
                created_date: Optional[datetime] = ..., 
                custom_image_id: Optional[str] = ..., 
                data_disk_parameters: Optional[List[DataDiskProperties]] = ..., 
                disallow_public_ip_address: bool = False, 
                environment_id: Optional[str] = ..., 
                expiration_date: Optional[datetime] = ..., 
                gallery_image_reference: Optional[GalleryImageReference] = ..., 
                is_authentication_with_ssh_key: Optional[bool] = ..., 
                lab_subnet_name: Optional[str] = ..., 
                lab_virtual_network_id: Optional[str] = ..., 
                location: Optional[str] = ..., 
                name: Optional[str] = ..., 
                network_interface: Optional[NetworkInterfaceProperties] = ..., 
                notes: Optional[str] = ..., 
                owner_object_id: str = "dynamicValue", 
                owner_user_principal_name: Optional[str] = ..., 
                password: Optional[str] = ..., 
                plan_id: Optional[str] = ..., 
                schedule_parameters: Optional[List[ScheduleCreationParameter]] = ..., 
                size: Optional[str] = ..., 
                ssh_key: Optional[str] = ..., 
                storage_type: str = "labStorageType", 
                tags: Optional[Dict[str, str]] = ..., 
                user_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.LabVirtualMachineFragment(UpdateResource):
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.LabVirtualMachineList(Model):
        next_link: str
        value: list[LabVirtualMachine]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[LabVirtualMachine]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.LinuxOsInfo(Model):
        linux_os_state: Union[str, LinuxOsState]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                linux_os_state: Optional[Union[str, LinuxOsState]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.LinuxOsState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEPROVISION_APPLIED = "DeprovisionApplied"
        DEPROVISION_REQUESTED = "DeprovisionRequested"
        NON_DEPROVISIONED = "NonDeprovisioned"


    class azure.mgmt.devtestlabs.models.ManagedIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        SYSTEM_ASSIGNED_USER_ASSIGNED = "SystemAssigned,UserAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.devtestlabs.models.NetworkInterfaceProperties(Model):
        dns_name: str
        private_ip_address: str
        public_ip_address: str
        public_ip_address_id: str
        rdp_authority: str
        shared_public_ip_address_configuration: SharedPublicIpAddressConfiguration
        ssh_authority: str
        subnet_id: str
        virtual_network_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                dns_name: Optional[str] = ..., 
                private_ip_address: Optional[str] = ..., 
                public_ip_address: Optional[str] = ..., 
                public_ip_address_id: Optional[str] = ..., 
                rdp_authority: Optional[str] = ..., 
                shared_public_ip_address_configuration: Optional[SharedPublicIpAddressConfiguration] = ..., 
                ssh_authority: Optional[str] = ..., 
                subnet_id: Optional[str] = ..., 
                virtual_network_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.NotificationChannel(Resource):
        created_date: datetime
        description: str
        email_recipient: str
        events: list[Event]
        id: str
        location: str
        name: str
        notification_locale: str
        provisioning_state: str
        tags: dict[str, str]
        type: str
        unique_identifier: str
        web_hook_url: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                email_recipient: Optional[str] = ..., 
                events: Optional[List[Event]] = ..., 
                location: Optional[str] = ..., 
                notification_locale: Optional[str] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                web_hook_url: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.NotificationChannelEventType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTO_SHUTDOWN = "AutoShutdown"
        COST = "Cost"


    class azure.mgmt.devtestlabs.models.NotificationChannelFragment(UpdateResource):
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.NotificationChannelList(Model):
        next_link: str
        value: list[NotificationChannel]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[NotificationChannel]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.NotificationSettings(Model):
        email_recipient: str
        notification_locale: str
        status: Union[str, EnableStatus]
        time_in_minutes: int
        webhook_url: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                email_recipient: Optional[str] = ..., 
                notification_locale: Optional[str] = ..., 
                status: Optional[Union[str, EnableStatus]] = ..., 
                time_in_minutes: Optional[int] = ..., 
                webhook_url: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.NotifyParameters(Model):
        event_name: Union[str, NotificationChannelEventType]
        json_payload: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                event_name: Optional[Union[str, NotificationChannelEventType]] = ..., 
                json_payload: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.OperationError(Model):
        code: str
        message: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                message: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.OperationMetadata(Model):
        display: OperationMetadataDisplay
        name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                display: Optional[OperationMetadataDisplay] = ..., 
                name: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.OperationMetadataDisplay(Model):
        description: str
        operation: str
        provider: str
        resource: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                operation: Optional[str] = ..., 
                provider: Optional[str] = ..., 
                resource: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.OperationResult(Model):
        error: OperationError
        status: str
        status_code: Union[str, HttpStatusCode]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                error: Optional[OperationError] = ..., 
                status: Optional[str] = ..., 
                status_code: Optional[Union[str, HttpStatusCode]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.ParameterInfo(Model):
        name: str
        value: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                value: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.ParametersValueFileInfo(Model):
        file_name: str
        parameters_value_info: JSON

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                file_name: Optional[str] = ..., 
                parameters_value_info: Optional[JSON] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.PercentageCostThresholdProperties(Model):
        threshold_value: float

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                threshold_value: Optional[float] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.Policy(Resource):
        created_date: datetime
        description: str
        evaluator_type: Union[str, PolicyEvaluatorType]
        fact_data: str
        fact_name: Union[str, PolicyFactName]
        id: str
        location: str
        name: str
        provisioning_state: str
        status: Union[str, PolicyStatus]
        tags: dict[str, str]
        threshold: str
        type: str
        unique_identifier: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                evaluator_type: Optional[Union[str, PolicyEvaluatorType]] = ..., 
                fact_data: Optional[str] = ..., 
                fact_name: Optional[Union[str, PolicyFactName]] = ..., 
                location: Optional[str] = ..., 
                status: Optional[Union[str, PolicyStatus]] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                threshold: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.PolicyEvaluatorType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALLOWED_VALUES_POLICY = "AllowedValuesPolicy"
        MAX_VALUE_POLICY = "MaxValuePolicy"


    class azure.mgmt.devtestlabs.models.PolicyFactName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ENVIRONMENT_TEMPLATE = "EnvironmentTemplate"
        GALLERY_IMAGE = "GalleryImage"
        LAB_PREMIUM_VM_COUNT = "LabPremiumVmCount"
        LAB_TARGET_COST = "LabTargetCost"
        LAB_VM_COUNT = "LabVmCount"
        LAB_VM_SIZE = "LabVmSize"
        SCHEDULE_EDIT_PERMISSION = "ScheduleEditPermission"
        USER_OWNED_LAB_PREMIUM_VM_COUNT = "UserOwnedLabPremiumVmCount"
        USER_OWNED_LAB_VM_COUNT = "UserOwnedLabVmCount"
        USER_OWNED_LAB_VM_COUNT_IN_SUBNET = "UserOwnedLabVmCountInSubnet"


    class azure.mgmt.devtestlabs.models.PolicyFragment(UpdateResource):
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.PolicyList(Model):
        next_link: str
        value: list[Policy]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[Policy]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.PolicySetResult(Model):
        has_error: bool
        policy_violations: list[PolicyViolation]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                has_error: Optional[bool] = ..., 
                policy_violations: Optional[List[PolicyViolation]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.PolicyStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.devtestlabs.models.PolicyViolation(Model):
        code: str
        message: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                message: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.Port(Model):
        backend_port: int
        transport_protocol: Union[str, TransportProtocol]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                backend_port: Optional[int] = ..., 
                transport_protocol: Optional[Union[str, TransportProtocol]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.PremiumDataDisk(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.devtestlabs.models.ProviderOperationResult(Model):
        next_link: str
        value: list[OperationMetadata]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[OperationMetadata]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.RdpConnection(Model):
        contents: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                contents: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.ReportingCycleType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CALENDAR_MONTH = "CalendarMonth"
        CUSTOM = "Custom"


    class azure.mgmt.devtestlabs.models.ResizeLabVirtualMachineProperties(Model):
        size: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                size: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.Resource(Model):
        id: str
        location: str
        name: str
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.RetargetScheduleProperties(Model):
        current_resource_id: str
        target_resource_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                current_resource_id: Optional[str] = ..., 
                target_resource_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.Schedule(Resource):
        created_date: datetime
        daily_recurrence: DayDetails
        hourly_recurrence: HourDetails
        id: str
        location: str
        name: str
        notification_settings: NotificationSettings
        provisioning_state: str
        status: Union[str, EnableStatus]
        tags: dict[str, str]
        target_resource_id: str
        task_type: str
        time_zone_id: str
        type: str
        unique_identifier: str
        weekly_recurrence: WeekDetails

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                daily_recurrence: Optional[DayDetails] = ..., 
                hourly_recurrence: Optional[HourDetails] = ..., 
                location: Optional[str] = ..., 
                notification_settings: Optional[NotificationSettings] = ..., 
                status: Optional[Union[str, EnableStatus]] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                target_resource_id: Optional[str] = ..., 
                task_type: Optional[str] = ..., 
                time_zone_id: Optional[str] = ..., 
                weekly_recurrence: Optional[WeekDetails] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.ScheduleCreationParameter(Model):
        daily_recurrence: DayDetails
        hourly_recurrence: HourDetails
        location: str
        name: str
        notification_settings: NotificationSettings
        status: Union[str, EnableStatus]
        tags: dict[str, str]
        target_resource_id: str
        task_type: str
        time_zone_id: str
        weekly_recurrence: WeekDetails

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                daily_recurrence: Optional[DayDetails] = ..., 
                hourly_recurrence: Optional[HourDetails] = ..., 
                name: Optional[str] = ..., 
                notification_settings: Optional[NotificationSettings] = ..., 
                status: Optional[Union[str, EnableStatus]] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                target_resource_id: Optional[str] = ..., 
                task_type: Optional[str] = ..., 
                time_zone_id: Optional[str] = ..., 
                weekly_recurrence: Optional[WeekDetails] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.ScheduleFragment(UpdateResource):
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.ScheduleList(Model):
        next_link: str
        value: list[Schedule]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[Schedule]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.Secret(Resource):
        id: str
        location: str
        name: str
        provisioning_state: str
        tags: dict[str, str]
        type: str
        unique_identifier: str
        value: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                value: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.SecretFragment(UpdateResource):
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.SecretList(Model):
        next_link: str
        value: list[Secret]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[Secret]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.ServiceFabric(Resource):
        applicable_schedule: ApplicableSchedule
        environment_id: str
        external_service_fabric_id: str
        id: str
        location: str
        name: str
        provisioning_state: str
        tags: dict[str, str]
        type: str
        unique_identifier: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                environment_id: Optional[str] = ..., 
                external_service_fabric_id: Optional[str] = ..., 
                location: Optional[str] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.ServiceFabricFragment(UpdateResource):
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.ServiceFabricList(Model):
        next_link: str
        value: list[ServiceFabric]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[ServiceFabric]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.ServiceRunner(Resource):
        id: str
        identity: IdentityProperties
        location: str
        name: str
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                identity: Optional[IdentityProperties] = ..., 
                location: Optional[str] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.ServiceRunnerList(Model):
        next_link: str
        value: list[ServiceRunner]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[ServiceRunner]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.SharedPublicIpAddressConfiguration(Model):
        inbound_nat_rules: list[InboundNatRule]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                inbound_nat_rules: Optional[List[InboundNatRule]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.ShutdownNotificationContent(Model):
        delay_url120: str
        delay_url60: str
        event_type: str
        guid: str
        lab_name: str
        minutes_until_shutdown: str
        owner: str
        resource_group_name: str
        skip_url: str
        subscription_id: str
        text: str
        vm_name: str
        vm_url: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                delay_url120: Optional[str] = ..., 
                delay_url60: Optional[str] = ..., 
                event_type: Optional[str] = ..., 
                guid: Optional[str] = ..., 
                lab_name: Optional[str] = ..., 
                minutes_until_shutdown: Optional[str] = ..., 
                owner: Optional[str] = ..., 
                resource_group_name: Optional[str] = ..., 
                skip_url: Optional[str] = ..., 
                subscription_id: Optional[str] = ..., 
                text: Optional[str] = ..., 
                vm_name: Optional[str] = ..., 
                vm_url: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.SourceControlType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        GIT_HUB = "GitHub"
        STORAGE_ACCOUNT = "StorageAccount"
        VSO_GIT = "VsoGit"


    class azure.mgmt.devtestlabs.models.StorageType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PREMIUM = "Premium"
        STANDARD = "Standard"
        STANDARD_SSD = "StandardSSD"


    class azure.mgmt.devtestlabs.models.Subnet(Model):
        allow_public_ip: Union[str, UsagePermissionType]
        lab_subnet_name: str
        resource_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                allow_public_ip: Optional[Union[str, UsagePermissionType]] = ..., 
                lab_subnet_name: Optional[str] = ..., 
                resource_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.SubnetOverride(Model):
        lab_subnet_name: str
        resource_id: str
        shared_public_ip_address_configuration: SubnetSharedPublicIpAddressConfiguration
        use_in_vm_creation_permission: Union[str, UsagePermissionType]
        use_public_ip_address_permission: Union[str, UsagePermissionType]
        virtual_network_pool_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                lab_subnet_name: Optional[str] = ..., 
                resource_id: Optional[str] = ..., 
                shared_public_ip_address_configuration: Optional[SubnetSharedPublicIpAddressConfiguration] = ..., 
                use_in_vm_creation_permission: Optional[Union[str, UsagePermissionType]] = ..., 
                use_public_ip_address_permission: Optional[Union[str, UsagePermissionType]] = ..., 
                virtual_network_pool_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.SubnetSharedPublicIpAddressConfiguration(Model):
        allowed_ports: list[Port]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                allowed_ports: Optional[List[Port]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.TargetCostProperties(Model):
        cost_thresholds: list[CostThresholdProperties]
        cycle_end_date_time: datetime
        cycle_start_date_time: datetime
        cycle_type: Union[str, ReportingCycleType]
        status: Union[str, TargetCostStatus]
        target: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                cost_thresholds: Optional[List[CostThresholdProperties]] = ..., 
                cycle_end_date_time: Optional[datetime] = ..., 
                cycle_start_date_time: Optional[datetime] = ..., 
                cycle_type: Optional[Union[str, ReportingCycleType]] = ..., 
                status: Optional[Union[str, TargetCostStatus]] = ..., 
                target: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.TargetCostStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.devtestlabs.models.TransportProtocol(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        TCP = "Tcp"
        UDP = "Udp"


    class azure.mgmt.devtestlabs.models.UpdateResource(Model):
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.UsagePermissionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALLOW = "Allow"
        DEFAULT = "Default"
        DENY = "Deny"


    class azure.mgmt.devtestlabs.models.User(Resource):
        created_date: datetime
        id: str
        identity: UserIdentity
        location: str
        name: str
        provisioning_state: str
        secret_store: UserSecretStore
        tags: dict[str, str]
        type: str
        unique_identifier: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                identity: Optional[UserIdentity] = ..., 
                location: Optional[str] = ..., 
                secret_store: Optional[UserSecretStore] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.UserFragment(UpdateResource):
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.UserIdentity(Model):
        app_id: str
        object_id: str
        principal_id: str
        principal_name: str
        tenant_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                app_id: Optional[str] = ..., 
                object_id: Optional[str] = ..., 
                principal_id: Optional[str] = ..., 
                principal_name: Optional[str] = ..., 
                tenant_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.UserList(Model):
        next_link: str
        value: list[User]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[User]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.UserSecretStore(Model):
        key_vault_id: str
        key_vault_uri: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                key_vault_id: Optional[str] = ..., 
                key_vault_uri: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.VirtualMachineCreationSource(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FROM_CUSTOM_IMAGE = "FromCustomImage"
        FROM_GALLERY_IMAGE = "FromGalleryImage"
        FROM_SHARED_GALLERY_IMAGE = "FromSharedGalleryImage"


    class azure.mgmt.devtestlabs.models.VirtualNetwork(Resource):
        allowed_subnets: list[Subnet]
        created_date: datetime
        description: str
        external_provider_resource_id: str
        external_subnets: list[ExternalSubnet]
        id: str
        location: str
        name: str
        provisioning_state: str
        subnet_overrides: list[SubnetOverride]
        tags: dict[str, str]
        type: str
        unique_identifier: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                allowed_subnets: Optional[List[Subnet]] = ..., 
                description: Optional[str] = ..., 
                external_provider_resource_id: Optional[str] = ..., 
                location: Optional[str] = ..., 
                subnet_overrides: Optional[List[SubnetOverride]] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.VirtualNetworkFragment(UpdateResource):
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.VirtualNetworkList(Model):
        next_link: str
        value: list[VirtualNetwork]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[VirtualNetwork]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.WeekDetails(Model):
        time: str
        weekdays: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                time: Optional[str] = ..., 
                weekdays: Optional[List[str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.WindowsOsInfo(Model):
        windows_os_state: Union[str, WindowsOsState]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                windows_os_state: Optional[Union[str, WindowsOsState]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devtestlabs.models.WindowsOsState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NON_SYSPREPPED = "NonSysprepped"
        SYSPREP_APPLIED = "SysprepApplied"
        SYSPREP_REQUESTED = "SysprepRequested"


namespace azure.mgmt.devtestlabs.operations

    class azure.mgmt.devtestlabs.operations.ArmTemplatesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                artifact_source_name: str, 
                name: str, 
                expand: Optional[str] = None, 
                **kwargs: Any
            ) -> ArmTemplate: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                artifact_source_name: str, 
                expand: Optional[str] = None, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                orderby: Optional[str] = None, 
                **kwargs: Any
            ) -> Iterable[ArmTemplate]: ...


    class azure.mgmt.devtestlabs.operations.ArtifactSourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                artifact_source: ArtifactSource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ArtifactSource: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                artifact_source: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ArtifactSource: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                expand: Optional[str] = None, 
                **kwargs: Any
            ) -> ArtifactSource: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                expand: Optional[str] = None, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                orderby: Optional[str] = None, 
                **kwargs: Any
            ) -> Iterable[ArtifactSource]: ...

        @distributed_trace
        def update(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                tags: Optional[Dict[str, str]] = None, 
                **kwargs: Any
            ) -> ArtifactSource: ...


    class azure.mgmt.devtestlabs.operations.ArtifactsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def generate_arm_template(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                artifact_source_name: str, 
                name: str, 
                generate_arm_template_request: GenerateArmTemplateRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ArmTemplateInfo: ...

        @overload
        def generate_arm_template(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                artifact_source_name: str, 
                name: str, 
                generate_arm_template_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ArmTemplateInfo: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                artifact_source_name: str, 
                name: str, 
                expand: Optional[str] = None, 
                **kwargs: Any
            ) -> Artifact: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                artifact_source_name: str, 
                expand: Optional[str] = None, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                orderby: Optional[str] = None, 
                **kwargs: Any
            ) -> Iterable[Artifact]: ...


    class azure.mgmt.devtestlabs.operations.CostsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                lab_cost: LabCost, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LabCost: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                lab_cost: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LabCost: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                expand: Optional[str] = None, 
                **kwargs: Any
            ) -> LabCost: ...


    class azure.mgmt.devtestlabs.operations.CustomImagesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                custom_image: CustomImage, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CustomImage]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                custom_image: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CustomImage]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                expand: Optional[str] = None, 
                **kwargs: Any
            ) -> CustomImage: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                expand: Optional[str] = None, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                orderby: Optional[str] = None, 
                **kwargs: Any
            ) -> Iterable[CustomImage]: ...

        @distributed_trace
        def update(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                tags: Optional[Dict[str, str]] = None, 
                **kwargs: Any
            ) -> CustomImage: ...


    class azure.mgmt.devtestlabs.operations.DisksOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def begin_attach(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                user_name: str, 
                name: str, 
                leased_by_lab_vm_id: Optional[str] = None, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                user_name: str, 
                name: str, 
                disk: Disk, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Disk]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                user_name: str, 
                name: str, 
                disk: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Disk]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                user_name: str, 
                name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_detach(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                user_name: str, 
                name: str, 
                leased_by_lab_vm_id: Optional[str] = None, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                user_name: str, 
                name: str, 
                expand: Optional[str] = None, 
                **kwargs: Any
            ) -> Disk: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                user_name: str, 
                expand: Optional[str] = None, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                orderby: Optional[str] = None, 
                **kwargs: Any
            ) -> Iterable[Disk]: ...

        @distributed_trace
        def update(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                user_name: str, 
                name: str, 
                tags: Optional[Dict[str, str]] = None, 
                **kwargs: Any
            ) -> Disk: ...


    class azure.mgmt.devtestlabs.operations.EnvironmentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                user_name: str, 
                name: str, 
                dtl_environment: DtlEnvironment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DtlEnvironment]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                user_name: str, 
                name: str, 
                dtl_environment: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DtlEnvironment]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                user_name: str, 
                name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                user_name: str, 
                name: str, 
                expand: Optional[str] = None, 
                **kwargs: Any
            ) -> DtlEnvironment: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                user_name: str, 
                expand: Optional[str] = None, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                orderby: Optional[str] = None, 
                **kwargs: Any
            ) -> Iterable[DtlEnvironment]: ...

        @distributed_trace
        def update(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                user_name: str, 
                name: str, 
                tags: Optional[Dict[str, str]] = None, 
                **kwargs: Any
            ) -> DtlEnvironment: ...


    class azure.mgmt.devtestlabs.operations.FormulasOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                formula: Formula, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Formula]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                formula: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Formula]: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                expand: Optional[str] = None, 
                **kwargs: Any
            ) -> Formula: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                expand: Optional[str] = None, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                orderby: Optional[str] = None, 
                **kwargs: Any
            ) -> Iterable[Formula]: ...

        @distributed_trace
        def update(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                tags: Optional[Dict[str, str]] = None, 
                **kwargs: Any
            ) -> Formula: ...


    class azure.mgmt.devtestlabs.operations.GalleryImagesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                expand: Optional[str] = None, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                orderby: Optional[str] = None, 
                **kwargs: Any
            ) -> Iterable[GalleryImage]: ...


    class azure.mgmt.devtestlabs.operations.GlobalSchedulesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def begin_execute(
                self, 
                resource_group_name: str, 
                name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_retarget(
                self, 
                resource_group_name: str, 
                name: str, 
                current_resource_id: Optional[str] = None, 
                target_resource_id: Optional[str] = None, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                name: str, 
                schedule: Schedule, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Schedule: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                name: str, 
                schedule: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Schedule: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                name: str, 
                expand: Optional[str] = None, 
                **kwargs: Any
            ) -> Schedule: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                expand: Optional[str] = None, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                orderby: Optional[str] = None, 
                **kwargs: Any
            ) -> Iterable[Schedule]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                expand: Optional[str] = None, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                orderby: Optional[str] = None, 
                **kwargs: Any
            ) -> Iterable[Schedule]: ...

        @distributed_trace
        def update(
                self, 
                resource_group_name: str, 
                name: str, 
                tags: Optional[Dict[str, str]] = None, 
                **kwargs: Any
            ) -> Schedule: ...


    class azure.mgmt.devtestlabs.operations.LabsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def begin_claim_any_vm(
                self, 
                resource_group_name: str, 
                name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_create_environment(
                self, 
                resource_group_name: str, 
                name: str, 
                lab_virtual_machine_creation_parameter: LabVirtualMachineCreationParameter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_create_environment(
                self, 
                resource_group_name: str, 
                name: str, 
                lab_virtual_machine_creation_parameter: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                name: str, 
                lab: Lab, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Lab]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                name: str, 
                lab: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Lab]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_export_resource_usage(
                self, 
                resource_group_name: str, 
                name: str, 
                blob_storage_absolute_sas_uri: Optional[str] = None, 
                usage_start_date: Optional[datetime] = None, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_import_virtual_machine(
                self, 
                resource_group_name: str, 
                name: str, 
                source_virtual_machine_resource_id: Optional[str] = None, 
                destination_virtual_machine_name: Optional[str] = None, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def generate_upload_uri(
                self, 
                resource_group_name: str, 
                name: str, 
                blob_name: Optional[str] = None, 
                **kwargs: Any
            ) -> GenerateUploadUriResponse: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                name: str, 
                expand: Optional[str] = None, 
                **kwargs: Any
            ) -> Lab: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                expand: Optional[str] = None, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                orderby: Optional[str] = None, 
                **kwargs: Any
            ) -> Iterable[Lab]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                expand: Optional[str] = None, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                orderby: Optional[str] = None, 
                **kwargs: Any
            ) -> Iterable[Lab]: ...

        @distributed_trace
        def list_vhds(
                self, 
                resource_group_name: str, 
                name: str, 
                **kwargs: Any
            ) -> Iterable[LabVhd]: ...

        @distributed_trace
        def update(
                self, 
                resource_group_name: str, 
                name: str, 
                tags: Optional[Dict[str, str]] = None, 
                **kwargs: Any
            ) -> Lab: ...


    class azure.mgmt.devtestlabs.operations.NotificationChannelsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                notification_channel: NotificationChannel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> NotificationChannel: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                notification_channel: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> NotificationChannel: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                expand: Optional[str] = None, 
                **kwargs: Any
            ) -> NotificationChannel: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                expand: Optional[str] = None, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                orderby: Optional[str] = None, 
                **kwargs: Any
            ) -> Iterable[NotificationChannel]: ...

        @distributed_trace
        def notify(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                event_name: Optional[Union[str, NotificationChannelEventType]] = None, 
                json_payload: Optional[str] = None, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def update(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                tags: Optional[Dict[str, str]] = None, 
                **kwargs: Any
            ) -> NotificationChannel: ...


    class azure.mgmt.devtestlabs.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get(
                self, 
                location_name: str, 
                name: str, 
                **kwargs: Any
            ) -> OperationResult: ...


    class azure.mgmt.devtestlabs.operations.PoliciesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                policy_set_name: str, 
                name: str, 
                policy: Policy, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Policy: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                policy_set_name: str, 
                name: str, 
                policy: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Policy: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                policy_set_name: str, 
                name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                policy_set_name: str, 
                name: str, 
                expand: Optional[str] = None, 
                **kwargs: Any
            ) -> Policy: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                policy_set_name: str, 
                expand: Optional[str] = None, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                orderby: Optional[str] = None, 
                **kwargs: Any
            ) -> Iterable[Policy]: ...

        @distributed_trace
        def update(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                policy_set_name: str, 
                name: str, 
                tags: Optional[Dict[str, str]] = None, 
                **kwargs: Any
            ) -> Policy: ...


    class azure.mgmt.devtestlabs.operations.PolicySetsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def evaluate_policies(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                policies: Optional[List[EvaluatePoliciesProperties]] = None, 
                **kwargs: Any
            ) -> EvaluatePoliciesResponse: ...


    class azure.mgmt.devtestlabs.operations.ProviderOperationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def list(self, **kwargs: Any) -> Iterable[OperationMetadata]: ...


    class azure.mgmt.devtestlabs.operations.SchedulesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def begin_execute(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                schedule: Schedule, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Schedule: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                schedule: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Schedule: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                expand: Optional[str] = None, 
                **kwargs: Any
            ) -> Schedule: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                expand: Optional[str] = None, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                orderby: Optional[str] = None, 
                **kwargs: Any
            ) -> Iterable[Schedule]: ...

        @distributed_trace
        def list_applicable(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                **kwargs: Any
            ) -> Iterable[Schedule]: ...

        @distributed_trace
        def update(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                tags: Optional[Dict[str, str]] = None, 
                **kwargs: Any
            ) -> Schedule: ...


    class azure.mgmt.devtestlabs.operations.SecretsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                user_name: str, 
                name: str, 
                secret: Secret, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Secret]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                user_name: str, 
                name: str, 
                secret: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Secret]: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                user_name: str, 
                name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                user_name: str, 
                name: str, 
                expand: Optional[str] = None, 
                **kwargs: Any
            ) -> Secret: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                user_name: str, 
                expand: Optional[str] = None, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                orderby: Optional[str] = None, 
                **kwargs: Any
            ) -> Iterable[Secret]: ...

        @distributed_trace
        def update(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                user_name: str, 
                name: str, 
                tags: Optional[Dict[str, str]] = None, 
                **kwargs: Any
            ) -> Secret: ...


    class azure.mgmt.devtestlabs.operations.ServiceFabricSchedulesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def begin_execute(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                user_name: str, 
                service_fabric_name: str, 
                name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                user_name: str, 
                service_fabric_name: str, 
                name: str, 
                schedule: Schedule, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Schedule: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                user_name: str, 
                service_fabric_name: str, 
                name: str, 
                schedule: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Schedule: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                user_name: str, 
                service_fabric_name: str, 
                name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                user_name: str, 
                service_fabric_name: str, 
                name: str, 
                expand: Optional[str] = None, 
                **kwargs: Any
            ) -> Schedule: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                user_name: str, 
                service_fabric_name: str, 
                expand: Optional[str] = None, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                orderby: Optional[str] = None, 
                **kwargs: Any
            ) -> Iterable[Schedule]: ...

        @distributed_trace
        def update(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                user_name: str, 
                service_fabric_name: str, 
                name: str, 
                tags: Optional[Dict[str, str]] = None, 
                **kwargs: Any
            ) -> Schedule: ...


    class azure.mgmt.devtestlabs.operations.ServiceFabricsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                user_name: str, 
                name: str, 
                service_fabric: ServiceFabric, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ServiceFabric]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                user_name: str, 
                name: str, 
                service_fabric: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ServiceFabric]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                user_name: str, 
                name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_start(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                user_name: str, 
                name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_stop(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                user_name: str, 
                name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                user_name: str, 
                name: str, 
                expand: Optional[str] = None, 
                **kwargs: Any
            ) -> ServiceFabric: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                user_name: str, 
                expand: Optional[str] = None, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                orderby: Optional[str] = None, 
                **kwargs: Any
            ) -> Iterable[ServiceFabric]: ...

        @distributed_trace
        def list_applicable_schedules(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                user_name: str, 
                name: str, 
                **kwargs: Any
            ) -> ApplicableSchedule: ...

        @distributed_trace
        def update(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                user_name: str, 
                name: str, 
                tags: Optional[Dict[str, str]] = None, 
                **kwargs: Any
            ) -> ServiceFabric: ...


    class azure.mgmt.devtestlabs.operations.ServiceRunnersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                service_runner: ServiceRunner, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ServiceRunner: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                service_runner: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ServiceRunner: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                **kwargs: Any
            ) -> ServiceRunner: ...


    class azure.mgmt.devtestlabs.operations.UsersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                user: User, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[User]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                user: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[User]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                expand: Optional[str] = None, 
                **kwargs: Any
            ) -> User: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                expand: Optional[str] = None, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                orderby: Optional[str] = None, 
                **kwargs: Any
            ) -> Iterable[User]: ...

        @distributed_trace
        def update(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                tags: Optional[Dict[str, str]] = None, 
                **kwargs: Any
            ) -> User: ...


    class azure.mgmt.devtestlabs.operations.VirtualMachineSchedulesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def begin_execute(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                virtual_machine_name: str, 
                name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                virtual_machine_name: str, 
                name: str, 
                schedule: Schedule, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Schedule: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                virtual_machine_name: str, 
                name: str, 
                schedule: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Schedule: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                virtual_machine_name: str, 
                name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                virtual_machine_name: str, 
                name: str, 
                expand: Optional[str] = None, 
                **kwargs: Any
            ) -> Schedule: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                virtual_machine_name: str, 
                expand: Optional[str] = None, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                orderby: Optional[str] = None, 
                **kwargs: Any
            ) -> Iterable[Schedule]: ...

        @distributed_trace
        def update(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                virtual_machine_name: str, 
                name: str, 
                tags: Optional[Dict[str, str]] = None, 
                **kwargs: Any
            ) -> Schedule: ...


    class azure.mgmt.devtestlabs.operations.VirtualMachinesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_add_data_disk(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                data_disk_properties: DataDiskProperties, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_add_data_disk(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                data_disk_properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_apply_artifacts(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                artifacts: Optional[List[ArtifactInstallProperties]] = None, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_claim(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                lab_virtual_machine: LabVirtualMachine, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[LabVirtualMachine]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                lab_virtual_machine: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[LabVirtualMachine]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_detach_data_disk(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                existing_lab_disk_id: Optional[str] = None, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_redeploy(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_resize(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                size: Optional[str] = None, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_restart(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_start(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_stop(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_transfer_disks(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_un_claim(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                expand: Optional[str] = None, 
                **kwargs: Any
            ) -> LabVirtualMachine: ...

        @distributed_trace
        def get_rdp_file_contents(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                **kwargs: Any
            ) -> RdpConnection: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                expand: Optional[str] = None, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                orderby: Optional[str] = None, 
                **kwargs: Any
            ) -> Iterable[LabVirtualMachine]: ...

        @distributed_trace
        def list_applicable_schedules(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                **kwargs: Any
            ) -> ApplicableSchedule: ...

        @distributed_trace
        def update(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                tags: Optional[Dict[str, str]] = None, 
                **kwargs: Any
            ) -> LabVirtualMachine: ...


    class azure.mgmt.devtestlabs.operations.VirtualNetworksOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                virtual_network: VirtualNetwork, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VirtualNetwork]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                virtual_network: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VirtualNetwork]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                expand: Optional[str] = None, 
                **kwargs: Any
            ) -> VirtualNetwork: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                expand: Optional[str] = None, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                orderby: Optional[str] = None, 
                **kwargs: Any
            ) -> Iterable[VirtualNetwork]: ...

        @distributed_trace
        def update(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                name: str, 
                tags: Optional[Dict[str, str]] = None, 
                **kwargs: Any
            ) -> VirtualNetwork: ...


```