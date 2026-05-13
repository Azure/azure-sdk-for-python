```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.sitemanager

    class azure.mgmt.sitemanager.SiteManagerMgmtClient: implements ContextManager 
        sites: SitesOperations
        sites_by_service_group: SitesByServiceGroupOperations
        sites_by_subscription: SitesBySubscriptionOperations

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


namespace azure.mgmt.sitemanager.aio

    class azure.mgmt.sitemanager.aio.SiteManagerMgmtClient: implements AsyncContextManager 
        sites: SitesOperations
        sites_by_service_group: SitesByServiceGroupOperations
        sites_by_subscription: SitesBySubscriptionOperations

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


namespace azure.mgmt.sitemanager.aio.operations

    class azure.mgmt.sitemanager.aio.operations.SitesByServiceGroupOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                servicegroup_name: str, 
                site_name: str, 
                resource: Site, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Site]: ...

        @overload
        async def begin_create_or_update(
                self, 
                servicegroup_name: str, 
                site_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Site]: ...

        @overload
        async def begin_create_or_update(
                self, 
                servicegroup_name: str, 
                site_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Site]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-03-01-preview', params_added_on={'2025-03-01-preview': ['api_version', 'servicegroup_name', 'site_name']}, api_versions_list=['2025-03-01-preview', '2025-06-01'])
        async def delete(
                self, 
                servicegroup_name: str, 
                site_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-03-01-preview', params_added_on={'2025-03-01-preview': ['api_version', 'servicegroup_name', 'site_name', 'accept']}, api_versions_list=['2025-03-01-preview', '2025-06-01'])
        async def get(
                self, 
                servicegroup_name: str, 
                site_name: str, 
                **kwargs: Any
            ) -> Site: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-03-01-preview', params_added_on={'2025-03-01-preview': ['api_version', 'servicegroup_name', 'accept']}, api_versions_list=['2025-03-01-preview', '2025-06-01'])
        def list_by_service_group(
                self, 
                servicegroup_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Site]: ...

        @overload
        async def update(
                self, 
                servicegroup_name: str, 
                site_name: str, 
                properties: SiteUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Site: ...

        @overload
        async def update(
                self, 
                servicegroup_name: str, 
                site_name: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Site: ...

        @overload
        async def update(
                self, 
                servicegroup_name: str, 
                site_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Site: ...


    class azure.mgmt.sitemanager.aio.operations.SitesBySubscriptionOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                site_name: str, 
                resource: Site, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Site]: ...

        @overload
        async def begin_create_or_update(
                self, 
                site_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Site]: ...

        @overload
        async def begin_create_or_update(
                self, 
                site_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Site]: ...

        @distributed_trace_async
        async def delete(
                self, 
                site_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                site_name: str, 
                **kwargs: Any
            ) -> Site: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Site]: ...

        @overload
        async def update(
                self, 
                site_name: str, 
                properties: SiteUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Site: ...

        @overload
        async def update(
                self, 
                site_name: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Site: ...

        @overload
        async def update(
                self, 
                site_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Site: ...


    class azure.mgmt.sitemanager.aio.operations.SitesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                site_name: str, 
                resource: Site, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Site]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                site_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Site]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                site_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Site]: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                site_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                site_name: str, 
                **kwargs: Any
            ) -> Site: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Site]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                site_name: str, 
                properties: SiteUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Site: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                site_name: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Site: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                site_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Site: ...


namespace azure.mgmt.sitemanager.models

    class azure.mgmt.sitemanager.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.sitemanager.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.sitemanager.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.sitemanager.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.sitemanager.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.sitemanager.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.sitemanager.models.ResourceProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.sitemanager.models.Site(ProxyResource):
        id: str
        name: str
        properties: Optional[SiteProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SiteProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.sitemanager.models.SiteAddressProperties(_Model):
        city: Optional[str]
        country: Optional[str]
        postal_code: Optional[str]
        state_or_province: Optional[str]
        street_address1: Optional[str]
        street_address2: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                city: Optional[str] = ..., 
                country: Optional[str] = ..., 
                postal_code: Optional[str] = ..., 
                state_or_province: Optional[str] = ..., 
                street_address1: Optional[str] = ..., 
                street_address2: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.sitemanager.models.SiteProperties(_Model):
        description: Optional[str]
        display_name: Optional[str]
        labels: Optional[dict[str, str]]
        provisioning_state: Optional[Union[str, ResourceProvisioningState]]
        site_address: Optional[SiteAddressProperties]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                labels: Optional[dict[str, str]] = ..., 
                site_address: Optional[SiteAddressProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.sitemanager.models.SiteUpdate(_Model):
        properties: Optional[SiteUpdateProperties]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SiteUpdateProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.sitemanager.models.SiteUpdateProperties(_Model):
        description: Optional[str]
        display_name: Optional[str]
        labels: Optional[dict[str, str]]
        site_address: Optional[SiteAddressProperties]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                labels: Optional[dict[str, str]] = ..., 
                site_address: Optional[SiteAddressProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.sitemanager.models.SystemData(_Model):
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


namespace azure.mgmt.sitemanager.operations

    class azure.mgmt.sitemanager.operations.SitesByServiceGroupOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                servicegroup_name: str, 
                site_name: str, 
                resource: Site, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Site]: ...

        @overload
        def begin_create_or_update(
                self, 
                servicegroup_name: str, 
                site_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Site]: ...

        @overload
        def begin_create_or_update(
                self, 
                servicegroup_name: str, 
                site_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Site]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-03-01-preview', params_added_on={'2025-03-01-preview': ['api_version', 'servicegroup_name', 'site_name']}, api_versions_list=['2025-03-01-preview', '2025-06-01'])
        def delete(
                self, 
                servicegroup_name: str, 
                site_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-03-01-preview', params_added_on={'2025-03-01-preview': ['api_version', 'servicegroup_name', 'site_name', 'accept']}, api_versions_list=['2025-03-01-preview', '2025-06-01'])
        def get(
                self, 
                servicegroup_name: str, 
                site_name: str, 
                **kwargs: Any
            ) -> Site: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-03-01-preview', params_added_on={'2025-03-01-preview': ['api_version', 'servicegroup_name', 'accept']}, api_versions_list=['2025-03-01-preview', '2025-06-01'])
        def list_by_service_group(
                self, 
                servicegroup_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Site]: ...

        @overload
        def update(
                self, 
                servicegroup_name: str, 
                site_name: str, 
                properties: SiteUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Site: ...

        @overload
        def update(
                self, 
                servicegroup_name: str, 
                site_name: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Site: ...

        @overload
        def update(
                self, 
                servicegroup_name: str, 
                site_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Site: ...


    class azure.mgmt.sitemanager.operations.SitesBySubscriptionOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                site_name: str, 
                resource: Site, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Site]: ...

        @overload
        def begin_create_or_update(
                self, 
                site_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Site]: ...

        @overload
        def begin_create_or_update(
                self, 
                site_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Site]: ...

        @distributed_trace
        def delete(
                self, 
                site_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                site_name: str, 
                **kwargs: Any
            ) -> Site: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Site]: ...

        @overload
        def update(
                self, 
                site_name: str, 
                properties: SiteUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Site: ...

        @overload
        def update(
                self, 
                site_name: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Site: ...

        @overload
        def update(
                self, 
                site_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Site: ...


    class azure.mgmt.sitemanager.operations.SitesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                site_name: str, 
                resource: Site, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Site]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                site_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Site]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                site_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Site]: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                site_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                site_name: str, 
                **kwargs: Any
            ) -> Site: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Site]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                site_name: str, 
                properties: SiteUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Site: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                site_name: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Site: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                site_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Site: ...


```