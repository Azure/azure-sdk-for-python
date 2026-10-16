```py
namespace azure.mgmt.applicationinsights

    class azure.mgmt.applicationinsights.ApplicationInsightsManagementClient: implements ContextManager 
        analytics_items: AnalyticsItemsOperations
        annotations: AnnotationsOperations
        api_keys: APIKeysOperations
        component_available_features: ComponentAvailableFeaturesOperations
        component_current_billing_features: ComponentCurrentBillingFeaturesOperations
        component_feature_capabilities: ComponentFeatureCapabilitiesOperations
        component_linked_storage_accounts: ComponentLinkedStorageAccountsOperations
        component_quota_status: ComponentQuotaStatusOperations
        components: ComponentsOperations
        deleted_workbooks: DeletedWorkbooksOperations
        export_configurations: ExportConfigurationsOperations
        favorites: FavoritesOperations
        live_token: LiveTokenOperations
        operations: Operations
        proactive_detection_configurations: ProactiveDetectionConfigurationsOperations
        web_test_locations: WebTestLocationsOperations
        web_tests: WebTestsOperations
        work_item_configurations: WorkItemConfigurationsOperations
        workbook_templates: WorkbookTemplatesOperations
        workbooks: WorkbooksOperations

        def __init__(
                self, 
                credential: TokenCredential, 
                subscription_id: str, 
                base_url: Optional[str] = None, 
                *, 
                cloud_setting: Optional[AzureClouds] = ..., 
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


namespace azure.mgmt.applicationinsights.aio

    class azure.mgmt.applicationinsights.aio.ApplicationInsightsManagementClient: implements AsyncContextManager 
        analytics_items: AnalyticsItemsOperations
        annotations: AnnotationsOperations
        api_keys: APIKeysOperations
        component_available_features: ComponentAvailableFeaturesOperations
        component_current_billing_features: ComponentCurrentBillingFeaturesOperations
        component_feature_capabilities: ComponentFeatureCapabilitiesOperations
        component_linked_storage_accounts: ComponentLinkedStorageAccountsOperations
        component_quota_status: ComponentQuotaStatusOperations
        components: ComponentsOperations
        deleted_workbooks: DeletedWorkbooksOperations
        export_configurations: ExportConfigurationsOperations
        favorites: FavoritesOperations
        live_token: LiveTokenOperations
        operations: Operations
        proactive_detection_configurations: ProactiveDetectionConfigurationsOperations
        web_test_locations: WebTestLocationsOperations
        web_tests: WebTestsOperations
        work_item_configurations: WorkItemConfigurationsOperations
        workbook_templates: WorkbookTemplatesOperations
        workbooks: WorkbooksOperations

        def __init__(
                self, 
                credential: AsyncTokenCredential, 
                subscription_id: str, 
                base_url: Optional[str] = None, 
                *, 
                cloud_setting: Optional[AzureClouds] = ..., 
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


namespace azure.mgmt.applicationinsights.aio.operations

    class azure.mgmt.applicationinsights.aio.operations.APIKeysOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                api_key_properties: APIKeyRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApplicationInsightsComponentAPIKey: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                api_key_properties: APIKeyRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApplicationInsightsComponentAPIKey: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                api_key_properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApplicationInsightsComponentAPIKey: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                key_id: str, 
                **kwargs: Any
            ) -> ApplicationInsightsComponentAPIKey: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                key_id: str, 
                **kwargs: Any
            ) -> ApplicationInsightsComponentAPIKey: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ApplicationInsightsComponentAPIKey]: ...


    class azure.mgmt.applicationinsights.aio.operations.AnalyticsItemsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                scope_path: Union[str, ItemScopePath], 
                *, 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                scope_path: Union[str, ItemScopePath], 
                *, 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                **kwargs: Any
            ) -> ApplicationInsightsComponentAnalyticsItem: ...

        @distributed_trace_async
        async def list(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                scope_path: Union[str, ItemScopePath], 
                *, 
                include_content: Optional[bool] = ..., 
                scope: Optional[Union[str, ItemScope]] = ..., 
                type: Optional[Union[str, ItemTypeParameter]] = ..., 
                **kwargs: Any
            ) -> List[ApplicationInsightsComponentAnalyticsItem]: ...

        @overload
        async def put(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                scope_path: Union[str, ItemScopePath], 
                item_properties: ApplicationInsightsComponentAnalyticsItem, 
                *, 
                content_type: str = "application/json", 
                override_item: Optional[bool] = ..., 
                **kwargs: Any
            ) -> ApplicationInsightsComponentAnalyticsItem: ...

        @overload
        async def put(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                scope_path: Union[str, ItemScopePath], 
                item_properties: ApplicationInsightsComponentAnalyticsItem, 
                *, 
                content_type: str = "application/json", 
                override_item: Optional[bool] = ..., 
                **kwargs: Any
            ) -> ApplicationInsightsComponentAnalyticsItem: ...

        @overload
        async def put(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                scope_path: Union[str, ItemScopePath], 
                item_properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                override_item: Optional[bool] = ..., 
                **kwargs: Any
            ) -> ApplicationInsightsComponentAnalyticsItem: ...


    class azure.mgmt.applicationinsights.aio.operations.AnnotationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                annotation_properties: Annotation, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> List[Annotation]: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                annotation_properties: Annotation, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> List[Annotation]: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                annotation_properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> List[Annotation]: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                annotation_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                annotation_id: str, 
                **kwargs: Any
            ) -> List[Annotation]: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                *, 
                end: str, 
                start: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Annotation]: ...


    class azure.mgmt.applicationinsights.aio.operations.ComponentAvailableFeaturesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> ApplicationInsightsComponentAvailableFeatures: ...


    class azure.mgmt.applicationinsights.aio.operations.ComponentCurrentBillingFeaturesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> ApplicationInsightsComponentBillingFeatures: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                billing_features_properties: ApplicationInsightsComponentBillingFeatures, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApplicationInsightsComponentBillingFeatures: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                billing_features_properties: ApplicationInsightsComponentBillingFeatures, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApplicationInsightsComponentBillingFeatures: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                billing_features_properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApplicationInsightsComponentBillingFeatures: ...


    class azure.mgmt.applicationinsights.aio.operations.ComponentFeatureCapabilitiesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> ApplicationInsightsComponentFeatureCapabilities: ...


    class azure.mgmt.applicationinsights.aio.operations.ComponentLinkedStorageAccountsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_and_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                storage_type: Union[str, StorageType], 
                linked_storage_accounts_properties: ComponentLinkedStorageAccounts, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ComponentLinkedStorageAccounts: ...

        @overload
        async def create_and_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                storage_type: Union[str, StorageType], 
                linked_storage_accounts_properties: ComponentLinkedStorageAccounts, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ComponentLinkedStorageAccounts: ...

        @overload
        async def create_and_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                storage_type: Union[str, StorageType], 
                linked_storage_accounts_properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ComponentLinkedStorageAccounts: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                storage_type: Union[str, StorageType], 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                storage_type: Union[str, StorageType], 
                **kwargs: Any
            ) -> ComponentLinkedStorageAccounts: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                storage_type: Union[str, StorageType], 
                linked_storage_accounts_properties: ComponentLinkedStorageAccountsPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ComponentLinkedStorageAccounts: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                storage_type: Union[str, StorageType], 
                linked_storage_accounts_properties: ComponentLinkedStorageAccountsPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ComponentLinkedStorageAccounts: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                storage_type: Union[str, StorageType], 
                linked_storage_accounts_properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ComponentLinkedStorageAccounts: ...


    class azure.mgmt.applicationinsights.aio.operations.ComponentQuotaStatusOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> ApplicationInsightsComponentQuotaStatus: ...


    class azure.mgmt.applicationinsights.aio.operations.ComponentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                insight_properties: ApplicationInsightsComponent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApplicationInsightsComponent: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                insight_properties: ApplicationInsightsComponent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApplicationInsightsComponent: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                insight_properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApplicationInsightsComponent: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> ApplicationInsightsComponent: ...

        @distributed_trace_async
        async def get_purge_status(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                purge_id: str, 
                **kwargs: Any
            ) -> ComponentPurgeStatusResponse: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[ApplicationInsightsComponent]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ApplicationInsightsComponent]: ...

        @overload
        async def purge(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                body: ComponentPurgeBody, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ComponentPurgeResponse: ...

        @overload
        async def purge(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                body: ComponentPurgeBody, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ComponentPurgeResponse: ...

        @overload
        async def purge(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ComponentPurgeResponse: ...

        @overload
        async def update_tags(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                component_tags: TagsResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApplicationInsightsComponent: ...

        @overload
        async def update_tags(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                component_tags: TagsResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApplicationInsightsComponent: ...

        @overload
        async def update_tags(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                component_tags: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApplicationInsightsComponent: ...


    class azure.mgmt.applicationinsights.aio.operations.DeletedWorkbooksOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                category: Optional[Union[str, CategoryType]] = ..., 
                tags: Optional[List[str]] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[DeletedWorkbook]: ...


    class azure.mgmt.applicationinsights.aio.operations.ExportConfigurationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                export_properties: ApplicationInsightsComponentExportRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> List[ApplicationInsightsComponentExportConfiguration]: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                export_properties: ApplicationInsightsComponentExportRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> List[ApplicationInsightsComponentExportConfiguration]: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                export_properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> List[ApplicationInsightsComponentExportConfiguration]: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                export_id: str, 
                **kwargs: Any
            ) -> ApplicationInsightsComponentExportConfiguration: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                export_id: str, 
                **kwargs: Any
            ) -> ApplicationInsightsComponentExportConfiguration: ...

        @distributed_trace_async
        async def list(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> List[ApplicationInsightsComponentExportConfiguration]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                export_id: str, 
                export_properties: ApplicationInsightsComponentExportRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApplicationInsightsComponentExportConfiguration: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                export_id: str, 
                export_properties: ApplicationInsightsComponentExportRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApplicationInsightsComponentExportConfiguration: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                export_id: str, 
                export_properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApplicationInsightsComponentExportConfiguration: ...


    class azure.mgmt.applicationinsights.aio.operations.FavoritesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def add(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                favorite_id: str, 
                favorite_properties: ApplicationInsightsComponentFavorite, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApplicationInsightsComponentFavorite: ...

        @overload
        async def add(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                favorite_id: str, 
                favorite_properties: ApplicationInsightsComponentFavorite, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApplicationInsightsComponentFavorite: ...

        @overload
        async def add(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                favorite_id: str, 
                favorite_properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApplicationInsightsComponentFavorite: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                favorite_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                favorite_id: str, 
                **kwargs: Any
            ) -> ApplicationInsightsComponentFavorite: ...

        @distributed_trace_async
        async def list(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                *, 
                can_fetch_content: Optional[bool] = ..., 
                favorite_type: Optional[Union[str, FavoriteType]] = ..., 
                source_type: Optional[Union[str, FavoriteSourceType]] = ..., 
                tags: Optional[List[str]] = ..., 
                **kwargs: Any
            ) -> List[ApplicationInsightsComponentFavorite]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                favorite_id: str, 
                favorite_properties: ApplicationInsightsComponentFavorite, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApplicationInsightsComponentFavorite: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                favorite_id: str, 
                favorite_properties: ApplicationInsightsComponentFavorite, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApplicationInsightsComponentFavorite: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                favorite_id: str, 
                favorite_properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApplicationInsightsComponentFavorite: ...


    class azure.mgmt.applicationinsights.aio.operations.LiveTokenOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_uri: str, 
                **kwargs: Any
            ) -> LiveTokenResponse: ...


    class azure.mgmt.applicationinsights.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


    class azure.mgmt.applicationinsights.aio.operations.ProactiveDetectionConfigurationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                configuration_id: str, 
                **kwargs: Any
            ) -> ApplicationInsightsComponentProactiveDetectionConfiguration: ...

        @distributed_trace_async
        async def list(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> List[ApplicationInsightsComponentProactiveDetectionConfiguration]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                configuration_id: str, 
                proactive_detection_properties: ApplicationInsightsComponentProactiveDetectionConfiguration, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApplicationInsightsComponentProactiveDetectionConfiguration: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                configuration_id: str, 
                proactive_detection_properties: ApplicationInsightsComponentProactiveDetectionConfiguration, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApplicationInsightsComponentProactiveDetectionConfiguration: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                configuration_id: str, 
                proactive_detection_properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApplicationInsightsComponentProactiveDetectionConfiguration: ...


    class azure.mgmt.applicationinsights.aio.operations.WebTestLocationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ApplicationInsightsComponentWebTestLocation]: ...


    class azure.mgmt.applicationinsights.aio.operations.WebTestsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                web_test_name: str, 
                web_test_definition: WebTest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> WebTest: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                web_test_name: str, 
                web_test_definition: WebTest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> WebTest: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                web_test_name: str, 
                web_test_definition: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> WebTest: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                web_test_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                web_test_name: str, 
                **kwargs: Any
            ) -> WebTest: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[WebTest]: ...

        @distributed_trace
        def list_by_component(
                self, 
                component_name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[WebTest]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[WebTest]: ...

        @overload
        async def update_tags(
                self, 
                resource_group_name: str, 
                web_test_name: str, 
                web_test_tags: TagsResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> WebTest: ...

        @overload
        async def update_tags(
                self, 
                resource_group_name: str, 
                web_test_name: str, 
                web_test_tags: TagsResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> WebTest: ...

        @overload
        async def update_tags(
                self, 
                resource_group_name: str, 
                web_test_name: str, 
                web_test_tags: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> WebTest: ...


    class azure.mgmt.applicationinsights.aio.operations.WorkItemConfigurationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                work_item_configuration_properties: WorkItemCreateConfiguration, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> WorkItemConfiguration: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                work_item_configuration_properties: WorkItemCreateConfiguration, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> WorkItemConfiguration: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                work_item_configuration_properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> WorkItemConfiguration: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                work_item_config_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get_default(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> WorkItemConfiguration: ...

        @distributed_trace_async
        async def get_item(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                work_item_config_id: str, 
                **kwargs: Any
            ) -> WorkItemConfiguration: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[WorkItemConfiguration]: ...

        @overload
        async def update_item(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                work_item_config_id: str, 
                work_item_configuration_properties: WorkItemCreateConfiguration, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> WorkItemConfiguration: ...

        @overload
        async def update_item(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                work_item_config_id: str, 
                work_item_configuration_properties: WorkItemCreateConfiguration, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> WorkItemConfiguration: ...

        @overload
        async def update_item(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                work_item_config_id: str, 
                work_item_configuration_properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> WorkItemConfiguration: ...


    class azure.mgmt.applicationinsights.aio.operations.WorkbookTemplatesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                workbook_template_properties: WorkbookTemplate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> WorkbookTemplate: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                workbook_template_properties: WorkbookTemplate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> WorkbookTemplate: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                workbook_template_properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> WorkbookTemplate: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> WorkbookTemplate: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[WorkbookTemplate]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                workbook_template_update_parameters: Optional[WorkbookTemplateUpdateParameters] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> WorkbookTemplate: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                workbook_template_update_parameters: Optional[WorkbookTemplateUpdateParameters] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> WorkbookTemplate: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                workbook_template_update_parameters: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> WorkbookTemplate: ...


    class azure.mgmt.applicationinsights.aio.operations.WorkbooksOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                workbook_properties: Workbook, 
                *, 
                content_type: str = "application/json", 
                source_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> Workbook: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                workbook_properties: Workbook, 
                *, 
                content_type: str = "application/json", 
                source_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> Workbook: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                workbook_properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                source_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> Workbook: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                *, 
                can_fetch_content: Optional[bool] = ..., 
                **kwargs: Any
            ) -> Workbook: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                can_fetch_content: Optional[bool] = ..., 
                category: Union[str, CategoryType], 
                source_id: Optional[str] = ..., 
                tags: Optional[List[str]] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Workbook]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                can_fetch_content: Optional[bool] = ..., 
                category: Union[str, CategoryType], 
                tags: Optional[List[str]] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Workbook]: ...

        @distributed_trace_async
        async def revision_get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                revision_id: str, 
                **kwargs: Any
            ) -> Workbook: ...

        @distributed_trace
        def revisions_list(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Workbook]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                workbook_update_parameters: Optional[WorkbookUpdateParameters] = None, 
                *, 
                content_type: str = "application/json", 
                source_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> Workbook: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                workbook_update_parameters: Optional[WorkbookUpdateParameters] = None, 
                *, 
                content_type: str = "application/json", 
                source_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> Workbook: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                workbook_update_parameters: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                source_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> Workbook: ...


namespace azure.mgmt.applicationinsights.models

    class azure.mgmt.applicationinsights.models.APIKeyRequest(_Model):
        linked_read_properties: Optional[list[str]]
        linked_write_properties: Optional[list[str]]
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                linked_read_properties: Optional[list[str]] = ..., 
                linked_write_properties: Optional[list[str]] = ..., 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.applicationinsights.models.Annotation(_Model):
        annotation_name: Optional[str]
        category: Optional[str]
        event_time: Optional[datetime]
        id: Optional[str]
        properties: Optional[str]
        related_annotation: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                annotation_name: Optional[str] = ..., 
                category: Optional[str] = ..., 
                event_time: Optional[datetime] = ..., 
                id: Optional[str] = ..., 
                properties: Optional[str] = ..., 
                related_annotation: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.applicationinsights.models.AnnotationError(_Model):
        code: Optional[str]
        innererror: Optional[InnerError]
        message: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                innererror: Optional[InnerError] = ..., 
                message: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.applicationinsights.models.ApplicationInsightsComponent(ComponentsResource):
        etag: Optional[str]
        id: str
        kind: str
        location: str
        name: str
        properties: Optional[ApplicationInsightsComponentProperties]
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                kind: str, 
                location: str, 
                properties: Optional[ApplicationInsightsComponentProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.applicationinsights.models.ApplicationInsightsComponentAPIKey(_Model):
        api_key: Optional[str]
        created_date: Optional[str]
        id: Optional[str]
        linked_read_properties: Optional[list[str]]
        linked_write_properties: Optional[list[str]]
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                created_date: Optional[str] = ..., 
                linked_read_properties: Optional[list[str]] = ..., 
                linked_write_properties: Optional[list[str]] = ..., 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.applicationinsights.models.ApplicationInsightsComponentAnalyticsItem(_Model):
        content: Optional[str]
        id: Optional[str]
        name: Optional[str]
        properties: Optional[ApplicationInsightsComponentAnalyticsItemProperties]
        scope: Optional[Union[str, ItemScope]]
        time_created: Optional[str]
        time_modified: Optional[str]
        type: Optional[Union[str, ItemType]]
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                content: Optional[str] = ..., 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                properties: Optional[ApplicationInsightsComponentAnalyticsItemProperties] = ..., 
                scope: Optional[Union[str, ItemScope]] = ..., 
                type: Optional[Union[str, ItemType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.applicationinsights.models.ApplicationInsightsComponentAnalyticsItemProperties(_Model):
        function_alias: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                function_alias: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.applicationinsights.models.ApplicationInsightsComponentAvailableFeatures(_Model):
        result: Optional[list[ApplicationInsightsComponentFeature]]


    class azure.mgmt.applicationinsights.models.ApplicationInsightsComponentBillingFeatures(_Model):
        current_billing_features: Optional[list[str]]
        data_volume_cap: Optional[ApplicationInsightsComponentDataVolumeCap]

        @overload
        def __init__(
                self, 
                *, 
                current_billing_features: Optional[list[str]] = ..., 
                data_volume_cap: Optional[ApplicationInsightsComponentDataVolumeCap] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.applicationinsights.models.ApplicationInsightsComponentDataVolumeCap(_Model):
        cap: Optional[float]
        max_history_cap: Optional[float]
        reset_time: Optional[int]
        stop_send_notification_when_hit_cap: Optional[bool]
        stop_send_notification_when_hit_threshold: Optional[bool]
        warning_threshold: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                cap: Optional[float] = ..., 
                stop_send_notification_when_hit_cap: Optional[bool] = ..., 
                stop_send_notification_when_hit_threshold: Optional[bool] = ..., 
                warning_threshold: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.applicationinsights.models.ApplicationInsightsComponentExportConfiguration(_Model):
        application_name: Optional[str]
        container_name: Optional[str]
        destination_account_id: Optional[str]
        destination_storage_location_id: Optional[str]
        destination_storage_subscription_id: Optional[str]
        destination_type: Optional[str]
        export_id: Optional[str]
        export_status: Optional[str]
        instrumentation_key: Optional[str]
        is_user_enabled: Optional[str]
        last_gap_time: Optional[str]
        last_success_time: Optional[str]
        last_user_update: Optional[str]
        notification_queue_enabled: Optional[str]
        permanent_error_reason: Optional[str]
        record_types: Optional[str]
        resource_group: Optional[str]
        storage_name: Optional[str]
        subscription_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                notification_queue_enabled: Optional[str] = ..., 
                record_types: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.applicationinsights.models.ApplicationInsightsComponentExportRequest(_Model):
        destination_account_id: Optional[str]
        destination_address: Optional[str]
        destination_storage_location_id: Optional[str]
        destination_storage_subscription_id: Optional[str]
        destination_type: Optional[str]
        is_enabled: Optional[str]
        notification_queue_enabled: Optional[str]
        notification_queue_uri: Optional[str]
        record_types: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                destination_account_id: Optional[str] = ..., 
                destination_address: Optional[str] = ..., 
                destination_storage_location_id: Optional[str] = ..., 
                destination_storage_subscription_id: Optional[str] = ..., 
                destination_type: Optional[str] = ..., 
                is_enabled: Optional[str] = ..., 
                notification_queue_enabled: Optional[str] = ..., 
                notification_queue_uri: Optional[str] = ..., 
                record_types: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.applicationinsights.models.ApplicationInsightsComponentFavorite(_Model):
        category: Optional[str]
        config: Optional[str]
        favorite_id: Optional[str]
        favorite_type: Optional[Union[str, FavoriteType]]
        is_generated_from_template: Optional[bool]
        name: Optional[str]
        source_type: Optional[str]
        tags: Optional[list[str]]
        time_modified: Optional[str]
        user_id: Optional[str]
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                category: Optional[str] = ..., 
                config: Optional[str] = ..., 
                favorite_type: Optional[Union[str, FavoriteType]] = ..., 
                is_generated_from_template: Optional[bool] = ..., 
                name: Optional[str] = ..., 
                source_type: Optional[str] = ..., 
                tags: Optional[list[str]] = ..., 
                version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.applicationinsights.models.ApplicationInsightsComponentFeature(_Model):
        capabilities: Optional[list[ApplicationInsightsComponentFeatureCapability]]
        feature_name: Optional[str]
        is_hidden: Optional[bool]
        is_main_feature: Optional[bool]
        meter_id: Optional[str]
        meter_rate_frequency: Optional[str]
        resouce_id: Optional[str]
        supported_addon_features: Optional[str]
        title: Optional[str]


    class azure.mgmt.applicationinsights.models.ApplicationInsightsComponentFeatureCapabilities(_Model):
        analytics_integration: Optional[bool]
        api_access_level: Optional[str]
        application_map: Optional[bool]
        burst_throttle_policy: Optional[str]
        daily_cap: Optional[float]
        daily_cap_reset_time: Optional[float]
        live_stream_metrics: Optional[bool]
        metadata_class: Optional[str]
        multiple_step_web_test: Optional[bool]
        open_schema: Optional[bool]
        power_bi_integration: Optional[bool]
        proactive_detection: Optional[bool]
        support_export_data: Optional[bool]
        throttle_rate: Optional[float]
        tracking_type: Optional[str]
        work_item_integration: Optional[bool]


    class azure.mgmt.applicationinsights.models.ApplicationInsightsComponentFeatureCapability(_Model):
        description: Optional[str]
        meter_id: Optional[str]
        meter_rate_frequency: Optional[str]
        name: Optional[str]
        unit: Optional[str]
        value: Optional[str]


    class azure.mgmt.applicationinsights.models.ApplicationInsightsComponentProactiveDetectionConfiguration(_Model):
        custom_emails: Optional[list[str]]
        enabled: Optional[bool]
        last_updated_time: Optional[str]
        name: Optional[str]
        rule_definitions: Optional[ApplicationInsightsComponentProactiveDetectionConfigurationRuleDefinitions]
        send_emails_to_subscription_owners: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                custom_emails: Optional[list[str]] = ..., 
                enabled: Optional[bool] = ..., 
                last_updated_time: Optional[str] = ..., 
                name: Optional[str] = ..., 
                rule_definitions: Optional[ApplicationInsightsComponentProactiveDetectionConfigurationRuleDefinitions] = ..., 
                send_emails_to_subscription_owners: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.applicationinsights.models.ApplicationInsightsComponentProactiveDetectionConfigurationRuleDefinitions(_Model):
        description: Optional[str]
        display_name: Optional[str]
        help_url: Optional[str]
        is_enabled_by_default: Optional[bool]
        is_hidden: Optional[bool]
        is_in_preview: Optional[bool]
        name: Optional[str]
        supports_email_notifications: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                help_url: Optional[str] = ..., 
                is_enabled_by_default: Optional[bool] = ..., 
                is_hidden: Optional[bool] = ..., 
                is_in_preview: Optional[bool] = ..., 
                name: Optional[str] = ..., 
                supports_email_notifications: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.applicationinsights.models.ApplicationInsightsComponentProperties(_Model):
        app_id: Optional[str]
        application_id: Optional[str]
        application_type: Union[str, ApplicationType]
        azure_monitor_workspace_ingestion_mode: Optional[Union[str, AzureMonitorWorkspaceIngestionMode]]
        azure_monitor_workspace_resource_id: Optional[str]
        connection_string: Optional[str]
        creation_date: Optional[datetime]
        data_collection_rule_resource_id: Optional[str]
        disable_ip_masking: Optional[bool]
        disable_local_auth: Optional[bool]
        flow_type: Optional[Union[str, FlowType]]
        force_customer_storage_for_profiler: Optional[bool]
        hockey_app_id: Optional[str]
        hockey_app_token: Optional[str]
        immediate_purge_data_on30_days: Optional[bool]
        ingestion_mode: Optional[Union[str, IngestionMode]]
        instrumentation_key: Optional[str]
        la_migration_date: Optional[datetime]
        name: Optional[str]
        otlp_logs_endpoint: Optional[str]
        otlp_metrics_endpoint: Optional[str]
        otlp_traces_endpoint: Optional[str]
        private_link_scoped_resources: Optional[list[PrivateLinkScopedResource]]
        provisioning_state: Optional[str]
        public_network_access_for_ingestion: Optional[Union[str, PublicNetworkAccessType]]
        public_network_access_for_query: Optional[Union[str, PublicNetworkAccessType]]
        request_source: Optional[Union[str, RequestSource]]
        retention_in_days: Optional[int]
        sampling_percentage: Optional[float]
        tenant_id: Optional[str]
        workspace_resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                application_type: Union[str, ApplicationType], 
                azure_monitor_workspace_ingestion_mode: Optional[Union[str, AzureMonitorWorkspaceIngestionMode]] = ..., 
                azure_monitor_workspace_resource_id: Optional[str] = ..., 
                disable_ip_masking: Optional[bool] = ..., 
                disable_local_auth: Optional[bool] = ..., 
                flow_type: Optional[Union[str, FlowType]] = ..., 
                force_customer_storage_for_profiler: Optional[bool] = ..., 
                hockey_app_id: Optional[str] = ..., 
                immediate_purge_data_on30_days: Optional[bool] = ..., 
                ingestion_mode: Optional[Union[str, IngestionMode]] = ..., 
                public_network_access_for_ingestion: Optional[Union[str, PublicNetworkAccessType]] = ..., 
                public_network_access_for_query: Optional[Union[str, PublicNetworkAccessType]] = ..., 
                request_source: Optional[Union[str, RequestSource]] = ..., 
                retention_in_days: Optional[int] = ..., 
                sampling_percentage: Optional[float] = ..., 
                workspace_resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.applicationinsights.models.ApplicationInsightsComponentQuotaStatus(_Model):
        app_id: Optional[str]
        expiration_time: Optional[str]
        should_be_throttled: Optional[bool]


    class azure.mgmt.applicationinsights.models.ApplicationInsightsComponentWebTestLocation(_Model):
        display_name: Optional[str]
        tag: Optional[str]


    class azure.mgmt.applicationinsights.models.ApplicationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        OTHER = "other"
        WEB = "web"


    class azure.mgmt.applicationinsights.models.AzureMonitorWorkspaceIngestionMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"
        NOT_OPTED_IN = "NotOptedIn"


    class azure.mgmt.applicationinsights.models.CategoryType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PERFORMANCE = "performance"
        RETENTION = "retention"
        TSG = "TSG"
        WORKBOOK = "workbook"


    class azure.mgmt.applicationinsights.models.ComponentLinkedStorageAccounts(ProxyResource):
        id: str
        name: str
        properties: Optional[LinkedStorageAccountsProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[LinkedStorageAccountsProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.applicationinsights.models.ComponentLinkedStorageAccountsPatch(_Model):
        properties: Optional[LinkedStorageAccountsProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[LinkedStorageAccountsProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.applicationinsights.models.ComponentPurgeBody(_Model):
        filters: list[ComponentPurgeBodyFilters]
        table: str

        @overload
        def __init__(
                self, 
                *, 
                filters: list[ComponentPurgeBodyFilters], 
                table: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.applicationinsights.models.ComponentPurgeBodyFilters(_Model):
        column: Optional[str]
        key: Optional[str]
        operator: Optional[str]
        value: Optional[Any]

        @overload
        def __init__(
                self, 
                *, 
                column: Optional[str] = ..., 
                key: Optional[str] = ..., 
                operator: Optional[str] = ..., 
                value: Optional[Any] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.applicationinsights.models.ComponentPurgeResponse(_Model):
        operation_id: str

        @overload
        def __init__(
                self, 
                *, 
                operation_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.applicationinsights.models.ComponentPurgeStatusResponse(_Model):
        status: Union[str, PurgeState]

        @overload
        def __init__(
                self, 
                *, 
                status: Union[str, PurgeState]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.applicationinsights.models.ComponentsResource(_Model):
        id: Optional[str]
        location: str
        name: Optional[str]
        tags: Optional[dict[str, str]]
        type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.applicationinsights.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.applicationinsights.models.DeletedWorkbook(DeletedWorkbookResource):
        etag: str
        id: str
        kind: Union[str, WorkbookSharedTypeKind]
        location: str
        name: str
        properties: Optional[DeletedWorkbookProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                kind: Optional[Union[str, WorkbookSharedTypeKind]] = ..., 
                location: str, 
                properties: Optional[DeletedWorkbookProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.applicationinsights.models.DeletedWorkbookError(_Model):
        error: Optional[DeletedWorkbookErrorDefinition]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[DeletedWorkbookErrorDefinition] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.applicationinsights.models.DeletedWorkbookErrorDefinition(_Model):
        code: Optional[str]
        innererror: Optional[DeletedWorkbookInnerErrorTrace]
        message: Optional[str]


    class azure.mgmt.applicationinsights.models.DeletedWorkbookInnerErrorTrace(_Model):
        trace: Optional[list[str]]


    class azure.mgmt.applicationinsights.models.DeletedWorkbookProperties(_Model):
        category: str
        description: Optional[str]
        display_name: str
        revision: Optional[str]
        serialized_data: str
        source_id: Optional[str]
        storage_uri: Optional[str]
        tags: Optional[list[str]]
        time_modified: Optional[datetime]
        user_id: Optional[str]
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                category: str, 
                description: Optional[str] = ..., 
                display_name: str, 
                serialized_data: str, 
                source_id: Optional[str] = ..., 
                storage_uri: Optional[str] = ..., 
                tags: Optional[list[str]] = ..., 
                version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.applicationinsights.models.DeletedWorkbookResource(TrackedResource):
        etag: Optional[str]
        id: str
        kind: Optional[Union[str, WorkbookSharedTypeKind]]
        location: str
        name: str
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                kind: Optional[Union[str, WorkbookSharedTypeKind]] = ..., 
                location: str, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.applicationinsights.models.ErrorFieldContract(_Model):
        code: Optional[str]
        message: Optional[str]
        target: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                message: Optional[str] = ..., 
                target: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.applicationinsights.models.ErrorResponse(_Model):
        code: Optional[str]
        details: Optional[list[ErrorFieldContract]]
        message: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                details: Optional[list[ErrorFieldContract]] = ..., 
                message: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.applicationinsights.models.ErrorResponseComponents(_Model):
        error: Optional[ErrorResponseComponentsError]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorResponseComponentsError] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.applicationinsights.models.ErrorResponseComponentsError(_Model):
        code: Optional[str]
        message: Optional[str]


    class azure.mgmt.applicationinsights.models.ErrorResponseLinkedStorage(_Model):
        error: Optional[ErrorResponseLinkedStorageError]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorResponseLinkedStorageError] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.applicationinsights.models.ErrorResponseLinkedStorageError(_Model):
        code: Optional[str]
        message: Optional[str]


    class azure.mgmt.applicationinsights.models.FavoriteSourceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EVENTS = "events"
        FUNNEL = "funnel"
        IMPACT = "impact"
        NOTEBOOK = "notebook"
        RETENTION = "retention"
        SEGMENTATION = "segmentation"
        SESSIONS = "sessions"
        USERFLOWS = "userflows"


    class azure.mgmt.applicationinsights.models.FavoriteType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SHARED = "shared"
        USER = "user"


    class azure.mgmt.applicationinsights.models.FlowType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BLUEFIELD = "Bluefield"


    class azure.mgmt.applicationinsights.models.HeaderField(_Model):
        header_field_name: Optional[str]
        header_field_value: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                header_field_name: Optional[str] = ..., 
                header_field_value: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.applicationinsights.models.IngestionMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION_INSIGHTS = "ApplicationInsights"
        APPLICATION_INSIGHTS_WITH_DIAGNOSTIC_SETTINGS = "ApplicationInsightsWithDiagnosticSettings"
        LOG_ANALYTICS = "LogAnalytics"


    class azure.mgmt.applicationinsights.models.InnerError(_Model):
        diagnosticcontext: Optional[str]
        time: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                diagnosticcontext: Optional[str] = ..., 
                time: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.applicationinsights.models.ItemScope(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SHARED = "shared"
        USER = "user"


    class azure.mgmt.applicationinsights.models.ItemScopePath(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ANALYTICS_ITEMS = "analyticsItems"
        MYANALYTICS_ITEMS = "myanalyticsItems"


    class azure.mgmt.applicationinsights.models.ItemType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FUNCTION = "function"
        NONE = "none"
        QUERY = "query"
        RECENT = "recent"


    class azure.mgmt.applicationinsights.models.ItemTypeParameter(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FOLDER = "folder"
        FUNCTION = "function"
        NONE = "none"
        QUERY = "query"
        RECENT = "recent"


    class azure.mgmt.applicationinsights.models.LinkedStorageAccountsProperties(_Model):
        linked_storage_account: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                linked_storage_account: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.applicationinsights.models.LiveTokenResponse(_Model):
        live_token: Optional[str]


    class azure.mgmt.applicationinsights.models.ManagedServiceIdentity(_Model):
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


    class azure.mgmt.applicationinsights.models.ManagedServiceIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        SYSTEM_ASSIGNED_USER_ASSIGNED = "SystemAssigned,UserAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.applicationinsights.models.Operation(_Model):
        display: Optional[OperationDisplay]
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                display: Optional[OperationDisplay] = ..., 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.applicationinsights.models.OperationDisplay(_Model):
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                operation: Optional[str] = ..., 
                provider: Optional[str] = ..., 
                resource: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.applicationinsights.models.PrivateLinkScopedResource(_Model):
        resource_id: Optional[str]
        scope_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                resource_id: Optional[str] = ..., 
                scope_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.applicationinsights.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.applicationinsights.models.PublicNetworkAccessType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.applicationinsights.models.PurgeState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPLETED = "completed"
        PENDING = "pending"


    class azure.mgmt.applicationinsights.models.RequestSource(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        REST = "rest"


    class azure.mgmt.applicationinsights.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.applicationinsights.models.StorageType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SERVICE_PROFILER = "ServiceProfiler"


    class azure.mgmt.applicationinsights.models.SystemData(_Model):
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


    class azure.mgmt.applicationinsights.models.TagsResource(_Model):
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.applicationinsights.models.TrackedResource(Resource):
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


    class azure.mgmt.applicationinsights.models.UserAssignedIdentity(_Model):
        client_id: Optional[str]
        principal_id: Optional[str]


    class azure.mgmt.applicationinsights.models.WebTest(WebtestsResource):
        id: str
        kind: Optional[Union[str, WebTestKind]]
        location: str
        name: str
        properties: Optional[WebTestProperties]
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                kind: Optional[Union[str, WebTestKind]] = ..., 
                location: str, 
                properties: Optional[WebTestProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.applicationinsights.models.WebTestGeolocation(_Model):
        location: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                location: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.applicationinsights.models.WebTestKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MULTISTEP = "multistep"
        PING = "ping"
        STANDARD = "standard"


    class azure.mgmt.applicationinsights.models.WebTestProperties(_Model):
        configuration: Optional[WebTestPropertiesConfiguration]
        description: Optional[str]
        enabled: Optional[bool]
        frequency: Optional[int]
        locations: list[WebTestGeolocation]
        provisioning_state: Optional[str]
        request: Optional[WebTestPropertiesRequest]
        retry_enabled: Optional[bool]
        synthetic_monitor_id: str
        timeout: Optional[int]
        validation_rules: Optional[WebTestPropertiesValidationRules]
        web_test_kind: Union[str, WebTestKind]
        web_test_name: str

        @overload
        def __init__(
                self, 
                *, 
                configuration: Optional[WebTestPropertiesConfiguration] = ..., 
                description: Optional[str] = ..., 
                enabled: Optional[bool] = ..., 
                frequency: Optional[int] = ..., 
                locations: list[WebTestGeolocation], 
                request: Optional[WebTestPropertiesRequest] = ..., 
                retry_enabled: Optional[bool] = ..., 
                synthetic_monitor_id: str, 
                timeout: Optional[int] = ..., 
                validation_rules: Optional[WebTestPropertiesValidationRules] = ..., 
                web_test_kind: Union[str, WebTestKind], 
                web_test_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.applicationinsights.models.WebTestPropertiesConfiguration(_Model):
        web_test: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                web_test: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.applicationinsights.models.WebTestPropertiesRequest(_Model):
        follow_redirects: Optional[bool]
        headers: Optional[list[HeaderField]]
        http_verb: Optional[str]
        parse_dependent_requests: Optional[bool]
        request_body: Optional[str]
        request_url: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                follow_redirects: Optional[bool] = ..., 
                headers: Optional[list[HeaderField]] = ..., 
                http_verb: Optional[str] = ..., 
                parse_dependent_requests: Optional[bool] = ..., 
                request_body: Optional[str] = ..., 
                request_url: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.applicationinsights.models.WebTestPropertiesValidationRules(_Model):
        content_validation: Optional[WebTestPropertiesValidationRulesContentValidation]
        expected_http_status_code: Optional[int]
        ignore_http_status_code: Optional[bool]
        ssl_cert_remaining_lifetime_check: Optional[int]
        ssl_check: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                content_validation: Optional[WebTestPropertiesValidationRulesContentValidation] = ..., 
                expected_http_status_code: Optional[int] = ..., 
                ignore_http_status_code: Optional[bool] = ..., 
                ssl_cert_remaining_lifetime_check: Optional[int] = ..., 
                ssl_check: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.applicationinsights.models.WebTestPropertiesValidationRulesContentValidation(_Model):
        content_match: Optional[str]
        ignore_case: Optional[bool]
        pass_if_text_found: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                content_match: Optional[str] = ..., 
                ignore_case: Optional[bool] = ..., 
                pass_if_text_found: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.applicationinsights.models.WebtestsResource(_Model):
        id: Optional[str]
        location: str
        name: Optional[str]
        tags: Optional[dict[str, str]]
        type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.applicationinsights.models.WorkItemConfiguration(_Model):
        config_display_name: Optional[str]
        config_properties: Optional[str]
        connector_id: Optional[str]
        id: Optional[str]
        is_default: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                config_display_name: Optional[str] = ..., 
                config_properties: Optional[str] = ..., 
                connector_id: Optional[str] = ..., 
                id: Optional[str] = ..., 
                is_default: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.applicationinsights.models.WorkItemConfigurationError(_Model):
        code: Optional[str]
        innererror: Optional[InnerError]
        message: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                innererror: Optional[InnerError] = ..., 
                message: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.applicationinsights.models.WorkItemCreateConfiguration(_Model):
        connector_data_configuration: Optional[str]
        connector_id: Optional[str]
        validate_only: Optional[bool]
        work_item_properties: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                connector_data_configuration: Optional[str] = ..., 
                connector_id: Optional[str] = ..., 
                validate_only: Optional[bool] = ..., 
                work_item_properties: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.applicationinsights.models.Workbook(TrackedResource):
        etag: Optional[str]
        id: str
        identity: Optional[WorkbookResourceIdentity]
        kind: Optional[Union[str, WorkbookSharedTypeKind]]
        location: str
        name: str
        properties: Optional[WorkbookProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                identity: Optional[WorkbookResourceIdentity] = ..., 
                kind: Optional[Union[str, WorkbookSharedTypeKind]] = ..., 
                location: str, 
                properties: Optional[WorkbookProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.applicationinsights.models.WorkbookError(_Model):
        error: Optional[WorkbookErrorDefinition]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[WorkbookErrorDefinition] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.applicationinsights.models.WorkbookErrorDefinition(_Model):
        code: Optional[str]
        innererror: Optional[WorkbookInnerErrorTrace]
        message: Optional[str]


    class azure.mgmt.applicationinsights.models.WorkbookInnerErrorTrace(_Model):
        trace: Optional[list[str]]


    class azure.mgmt.applicationinsights.models.WorkbookProperties(_Model):
        category: str
        description: Optional[str]
        display_name: str
        revision: Optional[str]
        serialized_data: str
        source_id: Optional[str]
        storage_uri: Optional[str]
        tags: Optional[list[str]]
        time_modified: Optional[datetime]
        user_id: Optional[str]
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                category: str, 
                description: Optional[str] = ..., 
                display_name: str, 
                serialized_data: str, 
                source_id: Optional[str] = ..., 
                storage_uri: Optional[str] = ..., 
                tags: Optional[list[str]] = ..., 
                version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.applicationinsights.models.WorkbookPropertiesUpdateParameters(_Model):
        category: Optional[str]
        description: Optional[str]
        display_name: Optional[str]
        revision: Optional[str]
        serialized_data: Optional[str]
        tags: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                category: Optional[str] = ..., 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                revision: Optional[str] = ..., 
                serialized_data: Optional[str] = ..., 
                tags: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.applicationinsights.models.WorkbookResourceIdentity(ManagedServiceIdentity):
        principal_id: str
        tenant_id: str
        type: Union[str, ManagedServiceIdentityType]
        user_assigned_identities: dict[str, UserAssignedIdentity]

        @overload
        def __init__(
                self, 
                *, 
                type: Union[str, ManagedServiceIdentityType], 
                user_assigned_identities: Optional[dict[str, UserAssignedIdentity]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.applicationinsights.models.WorkbookSharedTypeKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SHARED = "shared"


    class azure.mgmt.applicationinsights.models.WorkbookTemplate(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[WorkbookTemplateProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[WorkbookTemplateProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.applicationinsights.models.WorkbookTemplateError(_Model):
        error: Optional[WorkbookTemplateErrorBody]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[WorkbookTemplateErrorBody] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.applicationinsights.models.WorkbookTemplateErrorBody(_Model):
        code: Optional[str]
        details: Optional[list[WorkbookTemplateErrorFieldContract]]
        message: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                details: Optional[list[WorkbookTemplateErrorFieldContract]] = ..., 
                message: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.applicationinsights.models.WorkbookTemplateErrorFieldContract(_Model):
        code: Optional[str]
        message: Optional[str]
        target: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                message: Optional[str] = ..., 
                target: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.applicationinsights.models.WorkbookTemplateGallery(_Model):
        category: Optional[str]
        name: Optional[str]
        order: Optional[int]
        resource_type: Optional[str]
        type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                category: Optional[str] = ..., 
                name: Optional[str] = ..., 
                order: Optional[int] = ..., 
                resource_type: Optional[str] = ..., 
                type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.applicationinsights.models.WorkbookTemplateLocalizedGallery(_Model):
        galleries: Optional[list[WorkbookTemplateGallery]]
        template_data: Optional[Any]

        @overload
        def __init__(
                self, 
                *, 
                galleries: Optional[list[WorkbookTemplateGallery]] = ..., 
                template_data: Optional[Any] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.applicationinsights.models.WorkbookTemplateProperties(_Model):
        author: Optional[str]
        galleries: list[WorkbookTemplateGallery]
        localized: Optional[dict[str, list[WorkbookTemplateLocalizedGallery]]]
        priority: Optional[int]
        template_data: Any

        @overload
        def __init__(
                self, 
                *, 
                author: Optional[str] = ..., 
                galleries: list[WorkbookTemplateGallery], 
                localized: Optional[dict[str, list[WorkbookTemplateLocalizedGallery]]] = ..., 
                priority: Optional[int] = ..., 
                template_data: Any
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.applicationinsights.models.WorkbookTemplateUpdateParameters(_Model):
        properties: Optional[WorkbookTemplateProperties]
        tags: Optional[dict[str, str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[WorkbookTemplateProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.applicationinsights.models.WorkbookUpdateParameters(_Model):
        kind: Optional[Union[str, WorkbookUpdateSharedTypeKind]]
        properties: Optional[WorkbookPropertiesUpdateParameters]
        tags: Optional[dict[str, str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                kind: Optional[Union[str, WorkbookUpdateSharedTypeKind]] = ..., 
                properties: Optional[WorkbookPropertiesUpdateParameters] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.applicationinsights.models.WorkbookUpdateSharedTypeKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SHARED = "shared"


namespace azure.mgmt.applicationinsights.operations

    class azure.mgmt.applicationinsights.operations.APIKeysOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                api_key_properties: APIKeyRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApplicationInsightsComponentAPIKey: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                api_key_properties: APIKeyRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApplicationInsightsComponentAPIKey: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                api_key_properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApplicationInsightsComponentAPIKey: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                key_id: str, 
                **kwargs: Any
            ) -> ApplicationInsightsComponentAPIKey: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                key_id: str, 
                **kwargs: Any
            ) -> ApplicationInsightsComponentAPIKey: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ApplicationInsightsComponentAPIKey]: ...


    class azure.mgmt.applicationinsights.operations.AnalyticsItemsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                scope_path: Union[str, ItemScopePath], 
                *, 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                scope_path: Union[str, ItemScopePath], 
                *, 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                **kwargs: Any
            ) -> ApplicationInsightsComponentAnalyticsItem: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                scope_path: Union[str, ItemScopePath], 
                *, 
                include_content: Optional[bool] = ..., 
                scope: Optional[Union[str, ItemScope]] = ..., 
                type: Optional[Union[str, ItemTypeParameter]] = ..., 
                **kwargs: Any
            ) -> List[ApplicationInsightsComponentAnalyticsItem]: ...

        @overload
        def put(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                scope_path: Union[str, ItemScopePath], 
                item_properties: ApplicationInsightsComponentAnalyticsItem, 
                *, 
                content_type: str = "application/json", 
                override_item: Optional[bool] = ..., 
                **kwargs: Any
            ) -> ApplicationInsightsComponentAnalyticsItem: ...

        @overload
        def put(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                scope_path: Union[str, ItemScopePath], 
                item_properties: ApplicationInsightsComponentAnalyticsItem, 
                *, 
                content_type: str = "application/json", 
                override_item: Optional[bool] = ..., 
                **kwargs: Any
            ) -> ApplicationInsightsComponentAnalyticsItem: ...

        @overload
        def put(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                scope_path: Union[str, ItemScopePath], 
                item_properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                override_item: Optional[bool] = ..., 
                **kwargs: Any
            ) -> ApplicationInsightsComponentAnalyticsItem: ...


    class azure.mgmt.applicationinsights.operations.AnnotationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                annotation_properties: Annotation, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> List[Annotation]: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                annotation_properties: Annotation, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> List[Annotation]: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                annotation_properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> List[Annotation]: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                annotation_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                annotation_id: str, 
                **kwargs: Any
            ) -> List[Annotation]: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                *, 
                end: str, 
                start: str, 
                **kwargs: Any
            ) -> ItemPaged[Annotation]: ...


    class azure.mgmt.applicationinsights.operations.ComponentAvailableFeaturesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> ApplicationInsightsComponentAvailableFeatures: ...


    class azure.mgmt.applicationinsights.operations.ComponentCurrentBillingFeaturesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> ApplicationInsightsComponentBillingFeatures: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                billing_features_properties: ApplicationInsightsComponentBillingFeatures, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApplicationInsightsComponentBillingFeatures: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                billing_features_properties: ApplicationInsightsComponentBillingFeatures, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApplicationInsightsComponentBillingFeatures: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                billing_features_properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApplicationInsightsComponentBillingFeatures: ...


    class azure.mgmt.applicationinsights.operations.ComponentFeatureCapabilitiesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> ApplicationInsightsComponentFeatureCapabilities: ...


    class azure.mgmt.applicationinsights.operations.ComponentLinkedStorageAccountsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_and_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                storage_type: Union[str, StorageType], 
                linked_storage_accounts_properties: ComponentLinkedStorageAccounts, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ComponentLinkedStorageAccounts: ...

        @overload
        def create_and_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                storage_type: Union[str, StorageType], 
                linked_storage_accounts_properties: ComponentLinkedStorageAccounts, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ComponentLinkedStorageAccounts: ...

        @overload
        def create_and_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                storage_type: Union[str, StorageType], 
                linked_storage_accounts_properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ComponentLinkedStorageAccounts: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                storage_type: Union[str, StorageType], 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                storage_type: Union[str, StorageType], 
                **kwargs: Any
            ) -> ComponentLinkedStorageAccounts: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                storage_type: Union[str, StorageType], 
                linked_storage_accounts_properties: ComponentLinkedStorageAccountsPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ComponentLinkedStorageAccounts: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                storage_type: Union[str, StorageType], 
                linked_storage_accounts_properties: ComponentLinkedStorageAccountsPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ComponentLinkedStorageAccounts: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                storage_type: Union[str, StorageType], 
                linked_storage_accounts_properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ComponentLinkedStorageAccounts: ...


    class azure.mgmt.applicationinsights.operations.ComponentQuotaStatusOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> ApplicationInsightsComponentQuotaStatus: ...


    class azure.mgmt.applicationinsights.operations.ComponentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                insight_properties: ApplicationInsightsComponent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApplicationInsightsComponent: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                insight_properties: ApplicationInsightsComponent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApplicationInsightsComponent: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                insight_properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApplicationInsightsComponent: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> ApplicationInsightsComponent: ...

        @distributed_trace
        def get_purge_status(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                purge_id: str, 
                **kwargs: Any
            ) -> ComponentPurgeStatusResponse: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[ApplicationInsightsComponent]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ApplicationInsightsComponent]: ...

        @overload
        def purge(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                body: ComponentPurgeBody, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ComponentPurgeResponse: ...

        @overload
        def purge(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                body: ComponentPurgeBody, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ComponentPurgeResponse: ...

        @overload
        def purge(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ComponentPurgeResponse: ...

        @overload
        def update_tags(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                component_tags: TagsResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApplicationInsightsComponent: ...

        @overload
        def update_tags(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                component_tags: TagsResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApplicationInsightsComponent: ...

        @overload
        def update_tags(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                component_tags: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApplicationInsightsComponent: ...


    class azure.mgmt.applicationinsights.operations.DeletedWorkbooksOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                category: Optional[Union[str, CategoryType]] = ..., 
                tags: Optional[List[str]] = ..., 
                **kwargs: Any
            ) -> ItemPaged[DeletedWorkbook]: ...


    class azure.mgmt.applicationinsights.operations.ExportConfigurationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                export_properties: ApplicationInsightsComponentExportRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> List[ApplicationInsightsComponentExportConfiguration]: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                export_properties: ApplicationInsightsComponentExportRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> List[ApplicationInsightsComponentExportConfiguration]: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                export_properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> List[ApplicationInsightsComponentExportConfiguration]: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                export_id: str, 
                **kwargs: Any
            ) -> ApplicationInsightsComponentExportConfiguration: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                export_id: str, 
                **kwargs: Any
            ) -> ApplicationInsightsComponentExportConfiguration: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> List[ApplicationInsightsComponentExportConfiguration]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                export_id: str, 
                export_properties: ApplicationInsightsComponentExportRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApplicationInsightsComponentExportConfiguration: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                export_id: str, 
                export_properties: ApplicationInsightsComponentExportRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApplicationInsightsComponentExportConfiguration: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                export_id: str, 
                export_properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApplicationInsightsComponentExportConfiguration: ...


    class azure.mgmt.applicationinsights.operations.FavoritesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def add(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                favorite_id: str, 
                favorite_properties: ApplicationInsightsComponentFavorite, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApplicationInsightsComponentFavorite: ...

        @overload
        def add(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                favorite_id: str, 
                favorite_properties: ApplicationInsightsComponentFavorite, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApplicationInsightsComponentFavorite: ...

        @overload
        def add(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                favorite_id: str, 
                favorite_properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApplicationInsightsComponentFavorite: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                favorite_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                favorite_id: str, 
                **kwargs: Any
            ) -> ApplicationInsightsComponentFavorite: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                *, 
                can_fetch_content: Optional[bool] = ..., 
                favorite_type: Optional[Union[str, FavoriteType]] = ..., 
                source_type: Optional[Union[str, FavoriteSourceType]] = ..., 
                tags: Optional[List[str]] = ..., 
                **kwargs: Any
            ) -> List[ApplicationInsightsComponentFavorite]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                favorite_id: str, 
                favorite_properties: ApplicationInsightsComponentFavorite, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApplicationInsightsComponentFavorite: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                favorite_id: str, 
                favorite_properties: ApplicationInsightsComponentFavorite, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApplicationInsightsComponentFavorite: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                favorite_id: str, 
                favorite_properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApplicationInsightsComponentFavorite: ...


    class azure.mgmt.applicationinsights.operations.LiveTokenOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_uri: str, 
                **kwargs: Any
            ) -> LiveTokenResponse: ...


    class azure.mgmt.applicationinsights.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


    class azure.mgmt.applicationinsights.operations.ProactiveDetectionConfigurationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                configuration_id: str, 
                **kwargs: Any
            ) -> ApplicationInsightsComponentProactiveDetectionConfiguration: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> List[ApplicationInsightsComponentProactiveDetectionConfiguration]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                configuration_id: str, 
                proactive_detection_properties: ApplicationInsightsComponentProactiveDetectionConfiguration, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApplicationInsightsComponentProactiveDetectionConfiguration: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                configuration_id: str, 
                proactive_detection_properties: ApplicationInsightsComponentProactiveDetectionConfiguration, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApplicationInsightsComponentProactiveDetectionConfiguration: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                configuration_id: str, 
                proactive_detection_properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApplicationInsightsComponentProactiveDetectionConfiguration: ...


    class azure.mgmt.applicationinsights.operations.WebTestLocationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ApplicationInsightsComponentWebTestLocation]: ...


    class azure.mgmt.applicationinsights.operations.WebTestsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                web_test_name: str, 
                web_test_definition: WebTest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> WebTest: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                web_test_name: str, 
                web_test_definition: WebTest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> WebTest: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                web_test_name: str, 
                web_test_definition: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> WebTest: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                web_test_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                web_test_name: str, 
                **kwargs: Any
            ) -> WebTest: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[WebTest]: ...

        @distributed_trace
        def list_by_component(
                self, 
                component_name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[WebTest]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[WebTest]: ...

        @overload
        def update_tags(
                self, 
                resource_group_name: str, 
                web_test_name: str, 
                web_test_tags: TagsResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> WebTest: ...

        @overload
        def update_tags(
                self, 
                resource_group_name: str, 
                web_test_name: str, 
                web_test_tags: TagsResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> WebTest: ...

        @overload
        def update_tags(
                self, 
                resource_group_name: str, 
                web_test_name: str, 
                web_test_tags: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> WebTest: ...


    class azure.mgmt.applicationinsights.operations.WorkItemConfigurationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                work_item_configuration_properties: WorkItemCreateConfiguration, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> WorkItemConfiguration: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                work_item_configuration_properties: WorkItemCreateConfiguration, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> WorkItemConfiguration: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                work_item_configuration_properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> WorkItemConfiguration: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                work_item_config_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get_default(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> WorkItemConfiguration: ...

        @distributed_trace
        def get_item(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                work_item_config_id: str, 
                **kwargs: Any
            ) -> WorkItemConfiguration: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> ItemPaged[WorkItemConfiguration]: ...

        @overload
        def update_item(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                work_item_config_id: str, 
                work_item_configuration_properties: WorkItemCreateConfiguration, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> WorkItemConfiguration: ...

        @overload
        def update_item(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                work_item_config_id: str, 
                work_item_configuration_properties: WorkItemCreateConfiguration, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> WorkItemConfiguration: ...

        @overload
        def update_item(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                work_item_config_id: str, 
                work_item_configuration_properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> WorkItemConfiguration: ...


    class azure.mgmt.applicationinsights.operations.WorkbookTemplatesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                workbook_template_properties: WorkbookTemplate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> WorkbookTemplate: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                workbook_template_properties: WorkbookTemplate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> WorkbookTemplate: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                workbook_template_properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> WorkbookTemplate: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> WorkbookTemplate: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[WorkbookTemplate]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                workbook_template_update_parameters: Optional[WorkbookTemplateUpdateParameters] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> WorkbookTemplate: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                workbook_template_update_parameters: Optional[WorkbookTemplateUpdateParameters] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> WorkbookTemplate: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                workbook_template_update_parameters: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> WorkbookTemplate: ...


    class azure.mgmt.applicationinsights.operations.WorkbooksOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                workbook_properties: Workbook, 
                *, 
                content_type: str = "application/json", 
                source_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> Workbook: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                workbook_properties: Workbook, 
                *, 
                content_type: str = "application/json", 
                source_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> Workbook: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                workbook_properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                source_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> Workbook: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                *, 
                can_fetch_content: Optional[bool] = ..., 
                **kwargs: Any
            ) -> Workbook: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                can_fetch_content: Optional[bool] = ..., 
                category: Union[str, CategoryType], 
                source_id: Optional[str] = ..., 
                tags: Optional[List[str]] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Workbook]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                can_fetch_content: Optional[bool] = ..., 
                category: Union[str, CategoryType], 
                tags: Optional[List[str]] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Workbook]: ...

        @distributed_trace
        def revision_get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                revision_id: str, 
                **kwargs: Any
            ) -> Workbook: ...

        @distributed_trace
        def revisions_list(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Workbook]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                workbook_update_parameters: Optional[WorkbookUpdateParameters] = None, 
                *, 
                content_type: str = "application/json", 
                source_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> Workbook: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                workbook_update_parameters: Optional[WorkbookUpdateParameters] = None, 
                *, 
                content_type: str = "application/json", 
                source_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> Workbook: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                workbook_update_parameters: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                source_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> Workbook: ...


namespace azure.mgmt.applicationinsights.types

    class azure.mgmt.applicationinsights.types.APIKeyRequest(TypedDict, total=False):
        key "name": str
        linkedReadProperties: list[str]
        linkedWriteProperties: list[str]
        name: str


    class azure.mgmt.applicationinsights.types.Annotation(TypedDict, total=False):
        key "AnnotationName": str
        key "Category": str
        key "EventTime": str
        key "Id": str
        key "Properties": str
        key "RelatedAnnotation": str
        AnnotationName: str
        Category: str
        EventTime: str
        Id: str
        Properties: str
        RelatedAnnotation: str


    class azure.mgmt.applicationinsights.types.ApplicationInsightsComponent(ComponentsResource):
        key "etag": str
        key "id": str
        key "kind": Required[str]
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('ApplicationInsightsComponentProperties', module='types')
        key "type": str
        etag: str
        id: str
        kind: str
        location: str
        name: str
        properties: ApplicationInsightsComponentProperties
        tags: dict[str, str]
        type: str


    class azure.mgmt.applicationinsights.types.ApplicationInsightsComponentAnalyticsItem(TypedDict, total=False):
        key "Content": str
        key "Id": str
        key "Name": str
        key "Properties": ForwardRef('ApplicationInsightsComponentAnalyticsItemProperties', module='types')
        key "Scope": Union[str, ItemScope]
        key "TimeCreated": str
        key "TimeModified": str
        key "Type": Union[str, ItemType]
        key "Version": str
        Content: str
        Id: str
        Name: str
        Properties: ApplicationInsightsComponentAnalyticsItemProperties
        Scope: Union[str, ItemScope]
        TimeCreated: str
        TimeModified: str
        Type: Union[str, ItemType]
        Version: str


    class azure.mgmt.applicationinsights.types.ApplicationInsightsComponentAnalyticsItemProperties(TypedDict, total=False):
        key "functionAlias": str
        functionAlias: str


    class azure.mgmt.applicationinsights.types.ApplicationInsightsComponentBillingFeatures(TypedDict, total=False):
        key "DataVolumeCap": ForwardRef('ApplicationInsightsComponentDataVolumeCap', module='types')
        CurrentBillingFeatures: list[str]
        DataVolumeCap: ApplicationInsightsComponentDataVolumeCap


    class azure.mgmt.applicationinsights.types.ApplicationInsightsComponentDataVolumeCap(TypedDict, total=False):
        key "Cap": float
        key "MaxHistoryCap": float
        key "ResetTime": int
        key "StopSendNotificationWhenHitCap": bool
        key "StopSendNotificationWhenHitThreshold": bool
        key "WarningThreshold": int
        Cap: float
        MaxHistoryCap: float
        ResetTime: int
        StopSendNotificationWhenHitCap: bool
        StopSendNotificationWhenHitThreshold: bool
        WarningThreshold: int


    class azure.mgmt.applicationinsights.types.ApplicationInsightsComponentExportRequest(TypedDict, total=False):
        key "DestinationAccountId": str
        key "DestinationAddress": str
        key "DestinationStorageLocationId": str
        key "DestinationStorageSubscriptionId": str
        key "DestinationType": str
        key "IsEnabled": str
        key "NotificationQueueEnabled": str
        key "NotificationQueueUri": str
        key "RecordTypes": str
        DestinationAccountId: str
        DestinationAddress: str
        DestinationStorageLocationId: str
        DestinationStorageSubscriptionId: str
        DestinationType: str
        IsEnabled: str
        NotificationQueueEnabled: str
        NotificationQueueUri: str
        RecordTypes: str


    class azure.mgmt.applicationinsights.types.ApplicationInsightsComponentFavorite(TypedDict, total=False):
        key "Category": str
        key "Config": str
        key "FavoriteId": str
        key "FavoriteType": Union[str, FavoriteType]
        key "IsGeneratedFromTemplate": bool
        key "Name": str
        key "SourceType": str
        key "TimeModified": str
        key "UserId": str
        key "Version": str
        Category: str
        Config: str
        FavoriteId: str
        FavoriteType: Union[str, FavoriteType]
        IsGeneratedFromTemplate: bool
        Name: str
        SourceType: str
        Tags: list[str]
        TimeModified: str
        UserId: str
        Version: str


    class azure.mgmt.applicationinsights.types.ApplicationInsightsComponentProactiveDetectionConfiguration(TypedDict, total=False):
        key "enabled": bool
        key "lastUpdatedTime": str
        key "name": str
        key "ruleDefinitions": ForwardRef('ApplicationInsightsComponentProactiveDetectionConfigurationRuleDefinitions', module='types')
        key "sendEmailsToSubscriptionOwners": bool
        customEmails: list[str]
        enabled: bool
        lastUpdatedTime: str
        name: str
        ruleDefinitions: ApplicationInsightsComponentProactiveDetectionConfigurationRuleDefinitions
        sendEmailsToSubscriptionOwners: bool


    class azure.mgmt.applicationinsights.types.ApplicationInsightsComponentProactiveDetectionConfigurationRuleDefinitions(TypedDict, total=False):
        key "Description": str
        key "DisplayName": str
        key "HelpUrl": str
        key "IsEnabledByDefault": bool
        key "IsHidden": bool
        key "IsInPreview": bool
        key "Name": str
        key "SupportsEmailNotifications": bool
        Description: str
        DisplayName: str
        HelpUrl: str
        IsEnabledByDefault: bool
        IsHidden: bool
        IsInPreview: bool
        Name: str
        SupportsEmailNotifications: bool


    class azure.mgmt.applicationinsights.types.ApplicationInsightsComponentProperties(TypedDict, total=False):
        key "AppId": str
        key "ApplicationId": str
        key "Application_Type": Required[Union[str, ApplicationType]]
        key "AzureMonitorWorkspaceIngestionMode": Union[str, AzureMonitorWorkspaceIngestionMode]
        key "AzureMonitorWorkspaceResourceId": str
        key "ConnectionString": str
        key "CreationDate": str
        key "DataCollectionRuleResourceId": str
        key "DisableIpMasking": bool
        key "DisableLocalAuth": bool
        key "Flow_Type": Union[str, FlowType]
        key "ForceCustomerStorageForProfiler": bool
        key "HockeyAppId": str
        key "HockeyAppToken": str
        key "ImmediatePurgeDataOn30Days": bool
        key "IngestionMode": Union[str, IngestionMode]
        key "InstrumentationKey": str
        key "LaMigrationDate": str
        key "Name": str
        key "OTLPLogsEndpoint": str
        key "OTLPMetricsEndpoint": str
        key "OTLPTracesEndpoint": str
        key "Request_Source": Union[str, RequestSource]
        key "RetentionInDays": int
        key "SamplingPercentage": float
        key "TenantId": str
        key "WorkspaceResourceId": str
        key "provisioningState": str
        key "publicNetworkAccessForIngestion": Union[str, PublicNetworkAccessType]
        key "publicNetworkAccessForQuery": Union[str, PublicNetworkAccessType]
        AppId: str
        ApplicationId: str
        Application_Type: Union[str, ApplicationType]
        AzureMonitorWorkspaceIngestionMode: Union[str, AzureMonitorWorkspaceIngestionMode]
        AzureMonitorWorkspaceResourceId: str
        ConnectionString: str
        CreationDate: str
        DataCollectionRuleResourceId: str
        DisableIpMasking: bool
        DisableLocalAuth: bool
        Flow_Type: Union[str, FlowType]
        ForceCustomerStorageForProfiler: bool
        HockeyAppId: str
        HockeyAppToken: str
        ImmediatePurgeDataOn30Days: bool
        IngestionMode: Union[str, IngestionMode]
        InstrumentationKey: str
        LaMigrationDate: str
        Name: str
        OTLPLogsEndpoint: str
        OTLPMetricsEndpoint: str
        OTLPTracesEndpoint: str
        PrivateLinkScopedResources: list[PrivateLinkScopedResource]
        Request_Source: Union[str, RequestSource]
        RetentionInDays: int
        SamplingPercentage: float
        TenantId: str
        WorkspaceResourceId: str
        provisioningState: str
        publicNetworkAccessForIngestion: Union[str, PublicNetworkAccessType]
        publicNetworkAccessForQuery: Union[str, PublicNetworkAccessType]


    class azure.mgmt.applicationinsights.types.ComponentLinkedStorageAccounts(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('LinkedStorageAccountsProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: LinkedStorageAccountsProperties
        systemData: SystemData
        type: str


    class azure.mgmt.applicationinsights.types.ComponentLinkedStorageAccountsPatch(TypedDict, total=False):
        key "properties": ForwardRef('LinkedStorageAccountsProperties', module='types')
        properties: LinkedStorageAccountsProperties


    class azure.mgmt.applicationinsights.types.ComponentPurgeBody(TypedDict, total=False):
        key "filters": Required[list[ComponentPurgeBodyFilters]]
        key "table": Required[str]
        filters: list[ComponentPurgeBodyFilters]
        table: str


    class azure.mgmt.applicationinsights.types.ComponentPurgeBodyFilters(TypedDict, total=False):
        key "column": str
        key "key": str
        key "operator": str
        key "value": Any
        column: str
        key: str
        operator: str
        value: Any


    class azure.mgmt.applicationinsights.types.ComponentsResource(TypedDict, total=False):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "type": str
        id: str
        location: str
        name: str
        tags: dict[str, str]
        type: str


    class azure.mgmt.applicationinsights.types.HeaderField(TypedDict, total=False):
        key "key": str
        key "value": str
        key: str
        value: str


    class azure.mgmt.applicationinsights.types.LinkedStorageAccountsProperties(TypedDict, total=False):
        key "linkedStorageAccount": str
        linkedStorageAccount: str


    class azure.mgmt.applicationinsights.types.ManagedServiceIdentity(TypedDict, total=False):
        key "principalId": str
        key "tenantId": str
        key "type": Required[Union[str, ManagedServiceIdentityType]]
        principalId: str
        tenantId: str
        type: Union[str, ManagedServiceIdentityType]
        userAssignedIdentities: dict[str, UserAssignedIdentity]


    class azure.mgmt.applicationinsights.types.PrivateLinkScopedResource(TypedDict, total=False):
        key "ResourceId": str
        key "ScopeId": str
        ResourceId: str
        ScopeId: str


    class azure.mgmt.applicationinsights.types.ProxyResource(Resource):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        systemData: SystemData
        type: str


    class azure.mgmt.applicationinsights.types.Resource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        systemData: SystemData
        type: str


    class azure.mgmt.applicationinsights.types.SystemData(TypedDict, total=False):
        key "createdAt": str
        key "createdBy": str
        key "createdByType": Union[str, CreatedByType]
        key "lastModifiedAt": str
        key "lastModifiedBy": str
        key "lastModifiedByType": Union[str, CreatedByType]
        createdAt: str
        createdBy: str
        createdByType: Union[str, CreatedByType]
        lastModifiedAt: str
        lastModifiedBy: str
        lastModifiedByType: Union[str, CreatedByType]


    class azure.mgmt.applicationinsights.types.TagsResource(TypedDict, total=False):
        tags: dict[str, str]


    class azure.mgmt.applicationinsights.types.TrackedResource(Resource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.applicationinsights.types.UserAssignedIdentity(TypedDict, total=False):
        key "clientId": str
        key "principalId": str
        clientId: str
        principalId: str


    class azure.mgmt.applicationinsights.types.WebTest(WebtestsResource):
        key "id": str
        key "kind": Union[str, WebTestKind]
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('WebTestProperties', module='types')
        key "type": str
        id: str
        kind: Union[str, WebTestKind]
        location: str
        name: str
        properties: WebTestProperties
        tags: dict[str, str]
        type: str


    class azure.mgmt.applicationinsights.types.WebTestGeolocation(TypedDict, total=False):
        key "Id": str
        Id: str


    class azure.mgmt.applicationinsights.types.WebTestProperties(TypedDict, total=False):
        key "Configuration": ForwardRef('WebTestPropertiesConfiguration', module='types')
        key "Description": str
        key "Enabled": bool
        key "Frequency": int
        key "Kind": Required[Union[str, WebTestKind]]
        key "Locations": Required[list[WebTestGeolocation]]
        key "Name": Required[str]
        key "Request": ForwardRef('WebTestPropertiesRequest', module='types')
        key "RetryEnabled": bool
        key "SyntheticMonitorId": Required[str]
        key "Timeout": int
        key "ValidationRules": ForwardRef('WebTestPropertiesValidationRules', module='types')
        key "provisioningState": str
        Configuration: WebTestPropertiesConfiguration
        Description: str
        Enabled: bool
        Frequency: int
        Kind: Union[str, WebTestKind]
        Locations: list[WebTestGeolocation]
        Name: str
        Request: WebTestPropertiesRequest
        RetryEnabled: bool
        SyntheticMonitorId: str
        Timeout: int
        ValidationRules: WebTestPropertiesValidationRules
        provisioningState: str


    class azure.mgmt.applicationinsights.types.WebTestPropertiesConfiguration(TypedDict, total=False):
        key "WebTest": str
        WebTest: str


    class azure.mgmt.applicationinsights.types.WebTestPropertiesRequest(TypedDict, total=False):
        key "FollowRedirects": bool
        key "HttpVerb": str
        key "ParseDependentRequests": bool
        key "RequestBody": str
        key "RequestUrl": str
        FollowRedirects: bool
        Headers: list[HeaderField]
        HttpVerb: str
        ParseDependentRequests: bool
        RequestBody: str
        RequestUrl: str


    class azure.mgmt.applicationinsights.types.WebTestPropertiesValidationRules(TypedDict, total=False):
        key "ContentValidation": ForwardRef('WebTestPropertiesValidationRulesContentValidation', module='types')
        key "ExpectedHttpStatusCode": int
        key "IgnoreHttpStatusCode": bool
        key "SSLCertRemainingLifetimeCheck": int
        key "SSLCheck": bool
        ContentValidation: WebTestPropertiesValidationRulesContentValidation
        ExpectedHttpStatusCode: int
        IgnoreHttpStatusCode: bool
        SSLCertRemainingLifetimeCheck: int
        SSLCheck: bool


    class azure.mgmt.applicationinsights.types.WebTestPropertiesValidationRulesContentValidation(TypedDict, total=False):
        key "ContentMatch": str
        key "IgnoreCase": bool
        key "PassIfTextFound": bool
        ContentMatch: str
        IgnoreCase: bool
        PassIfTextFound: bool


    class azure.mgmt.applicationinsights.types.WebtestsResource(TypedDict, total=False):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "type": str
        id: str
        location: str
        name: str
        tags: dict[str, str]
        type: str


    class azure.mgmt.applicationinsights.types.WorkItemCreateConfiguration(TypedDict, total=False):
        key "ConnectorDataConfiguration": str
        key "ConnectorId": str
        key "ValidateOnly": bool
        ConnectorDataConfiguration: str
        ConnectorId: str
        ValidateOnly: bool
        WorkItemProperties: dict[str, str]


    class azure.mgmt.applicationinsights.types.Workbook(TrackedResource):
        key "etag": str
        key "id": str
        key "identity": ForwardRef('WorkbookResourceIdentity', module='types')
        key "kind": Union[str, WorkbookSharedTypeKind]
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('WorkbookProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        id: str
        identity: WorkbookResourceIdentity
        kind: Union[str, WorkbookSharedTypeKind]
        location: str
        name: str
        properties: WorkbookProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.applicationinsights.types.WorkbookProperties(TypedDict, total=False):
        key "category": Required[str]
        key "description": Optional[str]
        key "displayName": Required[str]
        key "revision": Optional[str]
        key "serializedData": Required[Optional[str]]
        key "sourceId": str
        key "storageUri": Optional[str]
        key "timeModified": str
        key "userId": str
        key "version": str
        category: str
        description: str
        displayName: str
        revision: str
        serializedData: str
        sourceId: str
        storageUri: str
        tags: list[str]
        timeModified: str
        userId: str
        version: str


    class azure.mgmt.applicationinsights.types.WorkbookPropertiesUpdateParameters(TypedDict, total=False):
        key "category": str
        key "description": Optional[str]
        key "displayName": str
        key "revision": Optional[str]
        key "serializedData": str
        category: str
        description: str
        displayName: str
        revision: str
        serializedData: str
        tags: list[str]


    class azure.mgmt.applicationinsights.types.WorkbookResourceIdentity(ManagedServiceIdentity):
        key "principalId": str
        key "tenantId": str
        key "type": Required[Union[str, ManagedServiceIdentityType]]
        principalId: str
        tenantId: str
        type: Union[str, ManagedServiceIdentityType]
        userAssignedIdentities: dict[str, UserAssignedIdentity]


    class azure.mgmt.applicationinsights.types.WorkbookTemplate(TrackedResource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('WorkbookTemplateProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: WorkbookTemplateProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.applicationinsights.types.WorkbookTemplateGallery(TypedDict, total=False):
        key "category": str
        key "name": str
        key "order": int
        key "resourceType": str
        key "type": str
        category: str
        name: str
        order: int
        resourceType: str
        type: str


    class azure.mgmt.applicationinsights.types.WorkbookTemplateLocalizedGallery(TypedDict, total=False):
        key "templateData": Any
        galleries: list[WorkbookTemplateGallery]
        templateData: Any


    class azure.mgmt.applicationinsights.types.WorkbookTemplateProperties(TypedDict, total=False):
        key "author": str
        key "galleries": Required[list[WorkbookTemplateGallery]]
        key "priority": int
        key "templateData": Required[Any]
        author: str
        galleries: list[WorkbookTemplateGallery]
        localized: dict[str, list[WorkbookTemplateLocalizedGallery]]
        priority: int
        templateData: Any


    class azure.mgmt.applicationinsights.types.WorkbookTemplateUpdateParameters(TypedDict, total=False):
        key "properties": ForwardRef('WorkbookTemplateProperties', module='types')
        properties: WorkbookTemplateProperties
        tags: dict[str, str]


    class azure.mgmt.applicationinsights.types.WorkbookUpdateParameters(TypedDict, total=False):
        key "kind": Union[str, WorkbookUpdateSharedTypeKind]
        key "properties": ForwardRef('WorkbookPropertiesUpdateParameters', module='types')
        kind: Union[str, WorkbookUpdateSharedTypeKind]
        properties: WorkbookPropertiesUpdateParameters
        tags: dict[str, str]


```