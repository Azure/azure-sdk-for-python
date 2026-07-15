```py
namespace azure.mgmt.confluent

    class azure.mgmt.confluent.ConfluentManagementClient: implements ContextManager 
        access: AccessOperations
        access_point_resources: AccessPointResourcesOperations
        cluster: ClusterOperations
        connector: ConnectorOperations
        environment: EnvironmentOperations
        marketplace_agreements: MarketplaceAgreementsOperations
        network_gateway_resources: NetworkGatewayResourcesOperations
        organization: OrganizationOperations
        organization_operations: OrganizationOperationsOperations
        topics: TopicsOperations
        validations: ValidationsOperations

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


namespace azure.mgmt.confluent.aio

    class azure.mgmt.confluent.aio.ConfluentManagementClient: implements AsyncContextManager 
        access: AccessOperations
        access_point_resources: AccessPointResourcesOperations
        cluster: ClusterOperations
        connector: ConnectorOperations
        environment: EnvironmentOperations
        marketplace_agreements: MarketplaceAgreementsOperations
        network_gateway_resources: NetworkGatewayResourcesOperations
        organization: OrganizationOperations
        organization_operations: OrganizationOperationsOperations
        topics: TopicsOperations
        validations: ValidationsOperations

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


namespace azure.mgmt.confluent.aio.operations

    class azure.mgmt.confluent.aio.operations.AccessOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_role_binding(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                body: AccessCreateRoleBindingRequestModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RoleBindingRecord: ...

        @overload
        async def create_role_binding(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                body: AccessCreateRoleBindingRequestModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RoleBindingRecord: ...

        @overload
        async def create_role_binding(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RoleBindingRecord: ...

        @distributed_trace_async
        async def delete_role_binding(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                role_binding_id: str, 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def invite_user(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                body: AccessInviteUserAccountModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> InvitationRecord: ...

        @overload
        async def invite_user(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                body: AccessInviteUserAccountModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> InvitationRecord: ...

        @overload
        async def invite_user(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> InvitationRecord: ...

        @overload
        async def list_clusters(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                body: ListAccessRequestModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AccessListClusterSuccessResponse: ...

        @overload
        async def list_clusters(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                body: ListAccessRequestModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AccessListClusterSuccessResponse: ...

        @overload
        async def list_clusters(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AccessListClusterSuccessResponse: ...

        @overload
        async def list_environments(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                body: ListAccessRequestModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AccessListEnvironmentsSuccessResponse: ...

        @overload
        async def list_environments(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                body: ListAccessRequestModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AccessListEnvironmentsSuccessResponse: ...

        @overload
        async def list_environments(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AccessListEnvironmentsSuccessResponse: ...

        @overload
        async def list_invitations(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                body: ListAccessRequestModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AccessListInvitationsSuccessResponse: ...

        @overload
        async def list_invitations(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                body: ListAccessRequestModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AccessListInvitationsSuccessResponse: ...

        @overload
        async def list_invitations(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AccessListInvitationsSuccessResponse: ...

        @overload
        async def list_role_binding_name_list(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                body: ListAccessRequestModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AccessRoleBindingNameListSuccessResponse: ...

        @overload
        async def list_role_binding_name_list(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                body: ListAccessRequestModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AccessRoleBindingNameListSuccessResponse: ...

        @overload
        async def list_role_binding_name_list(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AccessRoleBindingNameListSuccessResponse: ...

        @overload
        async def list_role_bindings(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                body: ListAccessRequestModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AccessListRoleBindingsSuccessResponse: ...

        @overload
        async def list_role_bindings(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                body: ListAccessRequestModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AccessListRoleBindingsSuccessResponse: ...

        @overload
        async def list_role_bindings(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AccessListRoleBindingsSuccessResponse: ...

        @overload
        async def list_service_accounts(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                body: ListAccessRequestModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AccessListServiceAccountsSuccessResponse: ...

        @overload
        async def list_service_accounts(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                body: ListAccessRequestModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AccessListServiceAccountsSuccessResponse: ...

        @overload
        async def list_service_accounts(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AccessListServiceAccountsSuccessResponse: ...

        @overload
        async def list_users(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                body: ListAccessRequestModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AccessListUsersSuccessResponse: ...

        @overload
        async def list_users(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                body: ListAccessRequestModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AccessListUsersSuccessResponse: ...

        @overload
        async def list_users(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AccessListUsersSuccessResponse: ...


    class azure.mgmt.confluent.aio.operations.AccessPointResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                environment_id: str, 
                network_gateway_id: str, 
                access_point_id: str, 
                resource: AccessPointResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AccessPointResource]: ...

        @overload
        async def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                environment_id: str, 
                network_gateway_id: str, 
                access_point_id: str, 
                resource: AccessPointResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AccessPointResource]: ...

        @overload
        async def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                environment_id: str, 
                network_gateway_id: str, 
                access_point_id: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AccessPointResource]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'organization_name', 'environment_id', 'network_gateway_id', 'access_point_id']}, api_versions_list=['2026-05-01-preview', '2026-06-02-preview'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                environment_id: str, 
                network_gateway_id: str, 
                access_point_id: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'organization_name', 'environment_id', 'network_gateway_id', 'access_point_id', 'accept']}, api_versions_list=['2026-05-01-preview', '2026-06-02-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                environment_id: str, 
                network_gateway_id: str, 
                access_point_id: str, 
                **kwargs: Any
            ) -> AccessPointResource: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'organization_name', 'environment_id', 'network_gateway_id', 'accept']}, api_versions_list=['2026-05-01-preview', '2026-06-02-preview'])
        def list(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                environment_id: str, 
                network_gateway_id: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[AccessPointResource]: ...


    class azure.mgmt.confluent.aio.operations.ClusterOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                environment_id: str, 
                cluster_id: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                environment_id: str, 
                cluster_id: str, 
                body: Optional[SCClusterRecord] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SCClusterRecord: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                environment_id: str, 
                cluster_id: str, 
                body: Optional[SCClusterRecord] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SCClusterRecord: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                environment_id: str, 
                cluster_id: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SCClusterRecord: ...


    class azure.mgmt.confluent.aio.operations.ConnectorOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                environment_id: str, 
                cluster_id: str, 
                connector_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                environment_id: str, 
                cluster_id: str, 
                connector_name: str, 
                body: Optional[ConnectorResource] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConnectorResource: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                environment_id: str, 
                cluster_id: str, 
                connector_name: str, 
                body: Optional[ConnectorResource] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConnectorResource: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                environment_id: str, 
                cluster_id: str, 
                connector_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConnectorResource: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                environment_id: str, 
                cluster_id: str, 
                connector_name: str, 
                **kwargs: Any
            ) -> ConnectorResource: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                environment_id: str, 
                cluster_id: str, 
                *, 
                page_size: Optional[int] = ..., 
                page_token: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[ConnectorResource]: ...


    class azure.mgmt.confluent.aio.operations.EnvironmentOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                environment_id: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                environment_id: str, 
                body: Optional[SCEnvironmentRecord] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SCEnvironmentRecord: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                environment_id: str, 
                body: Optional[SCEnvironmentRecord] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SCEnvironmentRecord: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                environment_id: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SCEnvironmentRecord: ...


    class azure.mgmt.confluent.aio.operations.MarketplaceAgreementsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create(
                self, 
                body: Optional[ConfluentAgreementResource] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConfluentAgreementResource: ...

        @overload
        async def create(
                self, 
                body: Optional[ConfluentAgreementResource] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConfluentAgreementResource: ...

        @overload
        async def create(
                self, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConfluentAgreementResource: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[ConfluentAgreementResource]: ...


    class azure.mgmt.confluent.aio.operations.NetworkGatewayResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                environment_id: str, 
                network_gateway_id: str, 
                resource: NetworkGatewayResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkGatewayResource]: ...

        @overload
        async def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                environment_id: str, 
                network_gateway_id: str, 
                resource: NetworkGatewayResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkGatewayResource]: ...

        @overload
        async def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                environment_id: str, 
                network_gateway_id: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkGatewayResource]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'organization_name', 'environment_id', 'network_gateway_id']}, api_versions_list=['2026-05-01-preview', '2026-06-02-preview'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                environment_id: str, 
                network_gateway_id: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'organization_name', 'environment_id', 'network_gateway_id', 'accept']}, api_versions_list=['2026-05-01-preview', '2026-06-02-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                environment_id: str, 
                network_gateway_id: str, 
                **kwargs: Any
            ) -> NetworkGatewayResource: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'organization_name', 'environment_id', 'accept']}, api_versions_list=['2026-05-01-preview', '2026-06-02-preview'])
        def list(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                environment_id: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[NetworkGatewayResource]: ...


    class azure.mgmt.confluent.aio.operations.OrganizationOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_activate_resource(
                self, 
                body: ActivateSaaSParameterRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SaaSResourceDetailsResponse]: ...

        @overload
        async def begin_activate_resource(
                self, 
                body: ActivateSaaSParameterRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SaaSResourceDetailsResponse]: ...

        @overload
        async def begin_activate_resource(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SaaSResourceDetailsResponse]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                body: Optional[OrganizationResource] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OrganizationResource]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                body: Optional[OrganizationResource] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OrganizationResource]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OrganizationResource]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_link_saa_s(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                body: SaaSData, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OrganizationResource]: ...

        @overload
        async def begin_link_saa_s(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                body: SaaSData, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OrganizationResource]: ...

        @overload
        async def begin_link_saa_s(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OrganizationResource]: ...

        @overload
        async def create_api_key(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                environment_id: str, 
                cluster_id: str, 
                body: CreateAPIKeyModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> APIKeyRecord: ...

        @overload
        async def create_api_key(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                environment_id: str, 
                cluster_id: str, 
                body: CreateAPIKeyModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> APIKeyRecord: ...

        @overload
        async def create_api_key(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                environment_id: str, 
                cluster_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> APIKeyRecord: ...

        @distributed_trace_async
        async def delete_cluster_api_key(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                api_key_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                **kwargs: Any
            ) -> OrganizationResource: ...

        @distributed_trace_async
        async def get_cluster_api_key(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                api_key_id: str, 
                **kwargs: Any
            ) -> APIKeyRecord: ...

        @distributed_trace_async
        async def get_cluster_by_id(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                environment_id: str, 
                cluster_id: str, 
                **kwargs: Any
            ) -> SCClusterRecord: ...

        @distributed_trace_async
        async def get_environment_by_id(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                environment_id: str, 
                **kwargs: Any
            ) -> SCEnvironmentRecord: ...

        @distributed_trace_async
        async def get_schema_registry_cluster_by_id(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                environment_id: str, 
                cluster_id: str, 
                **kwargs: Any
            ) -> SchemaRegistryClusterRecord: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-06-02-preview', params_added_on={'2026-06-02-preview': ['api_version', 'subscription_id', 'resource_group_name', 'organization_name', 'accept']}, api_versions_list=['2026-06-02-preview'])
        async def latest_linked_saa_s(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                **kwargs: Any
            ) -> LatestLinkedSaaSResponse: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[OrganizationResource]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[OrganizationResource]: ...

        @distributed_trace
        def list_clusters(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                environment_id: str, 
                *, 
                page_size: Optional[int] = ..., 
                page_token: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[SCClusterRecord]: ...

        @distributed_trace
        def list_environments(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                *, 
                page_size: Optional[int] = ..., 
                page_token: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[SCEnvironmentRecord]: ...

        @overload
        async def list_regions(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                body: ListAccessRequestModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ListRegionsSuccessResponse: ...

        @overload
        async def list_regions(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                body: ListAccessRequestModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ListRegionsSuccessResponse: ...

        @overload
        async def list_regions(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ListRegionsSuccessResponse: ...

        @distributed_trace
        def list_schema_registry_clusters(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                environment_id: str, 
                *, 
                page_size: Optional[int] = ..., 
                page_token: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[SchemaRegistryClusterRecord]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                body: Optional[OrganizationResourceUpdate] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> OrganizationResource: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                body: Optional[OrganizationResourceUpdate] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> OrganizationResource: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> OrganizationResource: ...


    class azure.mgmt.confluent.aio.operations.OrganizationOperationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[OperationResult]: ...


    class azure.mgmt.confluent.aio.operations.TopicsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                environment_id: str, 
                cluster_id: str, 
                topic_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                environment_id: str, 
                cluster_id: str, 
                topic_name: str, 
                body: Optional[TopicRecord] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TopicRecord: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                environment_id: str, 
                cluster_id: str, 
                topic_name: str, 
                body: Optional[TopicRecord] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TopicRecord: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                environment_id: str, 
                cluster_id: str, 
                topic_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TopicRecord: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                environment_id: str, 
                cluster_id: str, 
                topic_name: str, 
                **kwargs: Any
            ) -> TopicRecord: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                environment_id: str, 
                cluster_id: str, 
                *, 
                page_size: Optional[int] = ..., 
                page_token: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[TopicRecord]: ...


    class azure.mgmt.confluent.aio.operations.ValidationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def validate_organization(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                body: OrganizationResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> OrganizationResource: ...

        @overload
        async def validate_organization(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                body: OrganizationResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> OrganizationResource: ...

        @overload
        async def validate_organization(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> OrganizationResource: ...

        @overload
        async def validate_organization_v2(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                body: OrganizationResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ValidationResponse: ...

        @overload
        async def validate_organization_v2(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                body: OrganizationResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ValidationResponse: ...

        @overload
        async def validate_organization_v2(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ValidationResponse: ...


namespace azure.mgmt.confluent.models

    class azure.mgmt.confluent.models.APIKeyOwnerEntity(_Model):
        id: Optional[str]
        kind: Optional[str]
        related: Optional[str]
        resource_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                kind: Optional[str] = ..., 
                related: Optional[str] = ..., 
                resource_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.confluent.models.APIKeyProperties(_Model):
        metadata: Optional[SCMetadataEntity]
        spec: Optional[APIKeySpecEntity]

        @overload
        def __init__(
                self, 
                *, 
                metadata: Optional[SCMetadataEntity] = ..., 
                spec: Optional[APIKeySpecEntity] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.confluent.models.APIKeyRecord(_Model):
        id: Optional[str]
        kind: Optional[str]
        properties: Optional[APIKeyProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                kind: Optional[str] = ..., 
                properties: Optional[APIKeyProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.confluent.models.APIKeyResourceEntity(_Model):
        environment: Optional[str]
        id: Optional[str]
        kind: Optional[str]
        related: Optional[str]
        resource_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                environment: Optional[str] = ..., 
                id: Optional[str] = ..., 
                kind: Optional[str] = ..., 
                related: Optional[str] = ..., 
                resource_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.confluent.models.APIKeySpecEntity(_Model):
        description: Optional[str]
        name: Optional[str]
        owner: Optional[APIKeyOwnerEntity]
        resource: Optional[APIKeyResourceEntity]
        secret: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                name: Optional[str] = ..., 
                owner: Optional[APIKeyOwnerEntity] = ..., 
                resource: Optional[APIKeyResourceEntity] = ..., 
                secret: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.confluent.models.AccessCreateRoleBindingRequestModel(_Model):
        crn_pattern: Optional[str]
        principal: Optional[str]
        role_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                crn_pattern: Optional[str] = ..., 
                principal: Optional[str] = ..., 
                role_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.confluent.models.AccessInviteUserAccountModel(_Model):
        email: Optional[str]
        invited_user_details: Optional[AccessInvitedUserDetails]
        organization_id: Optional[str]
        upn: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                email: Optional[str] = ..., 
                invited_user_details: Optional[AccessInvitedUserDetails] = ..., 
                organization_id: Optional[str] = ..., 
                upn: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.confluent.models.AccessInvitedUserDetails(_Model):
        auth_type: Optional[str]
        invited_email: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                auth_type: Optional[str] = ..., 
                invited_email: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.confluent.models.AccessListClusterSuccessResponse(_Model):
        data: Optional[list[ClusterRecord]]
        kind: Optional[str]
        metadata: Optional[ConfluentListMetadata]

        @overload
        def __init__(
                self, 
                *, 
                data: Optional[list[ClusterRecord]] = ..., 
                kind: Optional[str] = ..., 
                metadata: Optional[ConfluentListMetadata] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.confluent.models.AccessListEnvironmentsSuccessResponse(_Model):
        data: Optional[list[EnvironmentRecord]]
        kind: Optional[str]
        metadata: Optional[ConfluentListMetadata]

        @overload
        def __init__(
                self, 
                *, 
                data: Optional[list[EnvironmentRecord]] = ..., 
                kind: Optional[str] = ..., 
                metadata: Optional[ConfluentListMetadata] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.confluent.models.AccessListInvitationsSuccessResponse(_Model):
        data: Optional[list[InvitationRecord]]
        kind: Optional[str]
        metadata: Optional[ConfluentListMetadata]

        @overload
        def __init__(
                self, 
                *, 
                data: Optional[list[InvitationRecord]] = ..., 
                kind: Optional[str] = ..., 
                metadata: Optional[ConfluentListMetadata] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.confluent.models.AccessListRoleBindingsSuccessResponse(_Model):
        data: Optional[list[RoleBindingRecord]]
        kind: Optional[str]
        metadata: Optional[ConfluentListMetadata]

        @overload
        def __init__(
                self, 
                *, 
                data: Optional[list[RoleBindingRecord]] = ..., 
                kind: Optional[str] = ..., 
                metadata: Optional[ConfluentListMetadata] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.confluent.models.AccessListServiceAccountsSuccessResponse(_Model):
        data: Optional[list[ServiceAccountRecord]]
        kind: Optional[str]
        metadata: Optional[ConfluentListMetadata]

        @overload
        def __init__(
                self, 
                *, 
                data: Optional[list[ServiceAccountRecord]] = ..., 
                kind: Optional[str] = ..., 
                metadata: Optional[ConfluentListMetadata] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.confluent.models.AccessListUsersSuccessResponse(_Model):
        data: Optional[list[UserRecord]]
        kind: Optional[str]
        metadata: Optional[ConfluentListMetadata]

        @overload
        def __init__(
                self, 
                *, 
                data: Optional[list[UserRecord]] = ..., 
                kind: Optional[str] = ..., 
                metadata: Optional[ConfluentListMetadata] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.confluent.models.AccessPointProperties(_Model):
        access_point_name: str
        dictionary: Optional[list[KeyValuePair]]
        egress_routes: Optional[list[str]]
        metadata: Optional[SCMetadataEntity]
        provisioning_state: Optional[Union[str, ProvisionState]]
        region: str
        vnet_injection: VnetInjectionDetails

        @overload
        def __init__(
                self, 
                *, 
                access_point_name: str, 
                dictionary: Optional[list[KeyValuePair]] = ..., 
                egress_routes: Optional[list[str]] = ..., 
                metadata: Optional[SCMetadataEntity] = ..., 
                region: str, 
                vnet_injection: VnetInjectionDetails
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.confluent.models.AccessPointResource(ProxyResource):
        id: str
        name: str
        properties: Optional[AccessPointProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[AccessPointProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.confluent.models.AccessRoleBindingNameListSuccessResponse(_Model):
        data: Optional[list[str]]
        kind: Optional[str]
        metadata: Optional[ConfluentListMetadata]

        @overload
        def __init__(
                self, 
                *, 
                data: Optional[list[str]] = ..., 
                kind: Optional[str] = ..., 
                metadata: Optional[ConfluentListMetadata] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.confluent.models.ActivateSaaSParameterRequest(_Model):
        publisher_id: Optional[str]
        saas_guid: str

        @overload
        def __init__(
                self, 
                *, 
                publisher_id: Optional[str] = ..., 
                saas_guid: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.confluent.models.AuthType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        KAFKA_API_KEY = "KAFKA_API_KEY"
        SERVICE_ACCOUNT = "SERVICE_ACCOUNT"


    class azure.mgmt.confluent.models.AzureBlobStorageSinkConnectorServiceInfo(ConnectorServiceTypeInfoBase, discriminator='AzureBlobStorageSinkConnector'):
        connector_service_type: Literal[ConnectorServiceType.AZURE_BLOB_STORAGE_SINK_CONNECTOR]
        storage_account_key: Optional[str]
        storage_account_name: Optional[str]
        storage_container_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                storage_account_key: Optional[str] = ..., 
                storage_account_name: Optional[str] = ..., 
                storage_container_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.confluent.models.AzureBlobStorageSourceConnectorServiceInfo(ConnectorServiceTypeInfoBase, discriminator='AzureBlobStorageSourceConnector'):
        connector_service_type: Literal[ConnectorServiceType.AZURE_BLOB_STORAGE_SOURCE_CONNECTOR]
        storage_account_key: Optional[str]
        storage_account_name: Optional[str]
        storage_container_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                storage_account_key: Optional[str] = ..., 
                storage_account_name: Optional[str] = ..., 
                storage_container_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.confluent.models.AzureCosmosDBSinkConnectorServiceInfo(ConnectorServiceTypeInfoBase, discriminator='AzureCosmosDBSinkConnector'):
        connector_service_type: Literal[ConnectorServiceType.AZURE_COSMOS_DB_SINK_CONNECTOR]
        cosmos_connection_endpoint: Optional[str]
        cosmos_containers_topic_mapping: Optional[str]
        cosmos_database_name: Optional[str]
        cosmos_id_strategy: Optional[str]
        cosmos_master_key: Optional[str]
        cosmos_write_details: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                cosmos_connection_endpoint: Optional[str] = ..., 
                cosmos_containers_topic_mapping: Optional[str] = ..., 
                cosmos_database_name: Optional[str] = ..., 
                cosmos_id_strategy: Optional[str] = ..., 
                cosmos_master_key: Optional[str] = ..., 
                cosmos_write_details: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.confluent.models.AzureCosmosDBSourceConnectorServiceInfo(ConnectorServiceTypeInfoBase, discriminator='AzureCosmosDBSourceConnector'):
        connector_service_type: Literal[ConnectorServiceType.AZURE_COSMOS_DB_SOURCE_CONNECTOR]
        cosmos_connection_endpoint: Optional[str]
        cosmos_containers_topic_mapping: Optional[str]
        cosmos_database_name: Optional[str]
        cosmos_include_all_containers: Optional[str]
        cosmos_master_key: Optional[str]
        cosmos_message_key_enabled: Optional[bool]
        cosmos_message_key_field: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                cosmos_connection_endpoint: Optional[str] = ..., 
                cosmos_containers_topic_mapping: Optional[str] = ..., 
                cosmos_database_name: Optional[str] = ..., 
                cosmos_include_all_containers: Optional[str] = ..., 
                cosmos_master_key: Optional[str] = ..., 
                cosmos_message_key_enabled: Optional[bool] = ..., 
                cosmos_message_key_field: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.confluent.models.AzureSynapseAnalyticsSinkConnectorServiceInfo(ConnectorServiceTypeInfoBase, discriminator='AzureSynapseAnalyticsSinkConnector'):
        connector_service_type: Literal[ConnectorServiceType.AZURE_SYNAPSE_ANALYTICS_SINK_CONNECTOR]
        synapse_sql_database_name: Optional[str]
        synapse_sql_password: Optional[str]
        synapse_sql_server_name: Optional[str]
        synapse_sql_user: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                synapse_sql_database_name: Optional[str] = ..., 
                synapse_sql_password: Optional[str] = ..., 
                synapse_sql_server_name: Optional[str] = ..., 
                synapse_sql_user: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.confluent.models.ClusterByokEntity(_Model):
        id: Optional[str]
        related: Optional[str]
        resource_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                related: Optional[str] = ..., 
                resource_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.confluent.models.ClusterConfigEntity(_Model):
        kind: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                kind: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.confluent.models.ClusterEnvironmentEntity(_Model):
        environment: Optional[str]
        id: Optional[str]
        related: Optional[str]
        resource_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                environment: Optional[str] = ..., 
                id: Optional[str] = ..., 
                related: Optional[str] = ..., 
                resource_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.confluent.models.ClusterNetworkEntity(_Model):
        environment: Optional[str]
        id: Optional[str]
        related: Optional[str]
        resource_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                environment: Optional[str] = ..., 
                id: Optional[str] = ..., 
                related: Optional[str] = ..., 
                resource_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.confluent.models.ClusterProperties(_Model):
        metadata: Optional[SCMetadataEntity]
        spec: Optional[SCClusterSpecEntity]
        status: Optional[ClusterStatusEntity]

        @overload
        def __init__(
                self, 
                *, 
                metadata: Optional[SCMetadataEntity] = ..., 
                spec: Optional[SCClusterSpecEntity] = ..., 
                status: Optional[ClusterStatusEntity] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.confluent.models.ClusterRecord(_Model):
        display_name: Optional[str]
        id: Optional[str]
        kind: Optional[str]
        metadata: Optional[MetadataEntity]
        spec: Optional[ClusterSpecEntity]
        status: Optional[ClusterStatusEntity]

        @overload
        def __init__(
                self, 
                *, 
                display_name: Optional[str] = ..., 
                id: Optional[str] = ..., 
                kind: Optional[str] = ..., 
                metadata: Optional[MetadataEntity] = ..., 
                spec: Optional[ClusterSpecEntity] = ..., 
                status: Optional[ClusterStatusEntity] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.confluent.models.ClusterSpecEntity(_Model):
        api_endpoint: Optional[str]
        availability: Optional[str]
        byok: Optional[ClusterByokEntity]
        cloud: Optional[str]
        config: Optional[ClusterConfigEntity]
        display_name: Optional[str]
        environment: Optional[ClusterEnvironmentEntity]
        http_endpoint: Optional[str]
        kafka_bootstrap_endpoint: Optional[str]
        network: Optional[ClusterNetworkEntity]
        region: Optional[str]
        zone: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                api_endpoint: Optional[str] = ..., 
                availability: Optional[str] = ..., 
                byok: Optional[ClusterByokEntity] = ..., 
                cloud: Optional[str] = ..., 
                config: Optional[ClusterConfigEntity] = ..., 
                display_name: Optional[str] = ..., 
                environment: Optional[ClusterEnvironmentEntity] = ..., 
                http_endpoint: Optional[str] = ..., 
                kafka_bootstrap_endpoint: Optional[str] = ..., 
                network: Optional[ClusterNetworkEntity] = ..., 
                region: Optional[str] = ..., 
                zone: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.confluent.models.ClusterStatusEntity(_Model):
        cku: Optional[int]
        phase: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                cku: Optional[int] = ..., 
                phase: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.confluent.models.ConfluentAgreementProperties(_Model):
        accepted: Optional[bool]
        license_text_link: Optional[str]
        plan: Optional[str]
        privacy_policy_link: Optional[str]
        product: Optional[str]
        publisher: Optional[str]
        retrieve_datetime: Optional[datetime]
        signature: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                accepted: Optional[bool] = ..., 
                license_text_link: Optional[str] = ..., 
                plan: Optional[str] = ..., 
                privacy_policy_link: Optional[str] = ..., 
                product: Optional[str] = ..., 
                publisher: Optional[str] = ..., 
                retrieve_datetime: Optional[datetime] = ..., 
                signature: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.confluent.models.ConfluentAgreementResource(_Model):
        id: Optional[str]
        name: Optional[str]
        properties: Optional[ConfluentAgreementProperties]
        system_data: Optional[SystemData]
        type: Optional[str]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ConfluentAgreementProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.confluent.models.ConfluentListMetadata(_Model):
        first: Optional[str]
        last: Optional[str]
        next: Optional[str]
        prev: Optional[str]
        total_size: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                first: Optional[str] = ..., 
                last: Optional[str] = ..., 
                next: Optional[str] = ..., 
                prev: Optional[str] = ..., 
                total_size: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.confluent.models.ConnectorClass(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZUREBLOBSINK = "AZUREBLOBSINK"
        AZUREBLOBSOURCE = "AZUREBLOBSOURCE"
        AZURECOSMOSV2_SINK = "AZURECOSMOSV2SINK"
        AZURECOSMOSV2_SOURCE = "AZURECOSMOSV2SOURCE"


    class azure.mgmt.confluent.models.ConnectorInfoBase(_Model):
        connector_class: Optional[Union[str, ConnectorClass]]
        connector_id: Optional[str]
        connector_name: Optional[str]
        connector_state: Optional[Union[str, ConnectorStatus]]
        connector_type: Optional[Union[str, ConnectorType]]

        @overload
        def __init__(
                self, 
                *, 
                connector_class: Optional[Union[str, ConnectorClass]] = ..., 
                connector_id: Optional[str] = ..., 
                connector_name: Optional[str] = ..., 
                connector_state: Optional[Union[str, ConnectorStatus]] = ..., 
                connector_type: Optional[Union[str, ConnectorType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.confluent.models.ConnectorResource(ProxyResource):
        id: str
        name: str
        properties: ConnectorResourceProperties
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: ConnectorResourceProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.confluent.models.ConnectorResourceProperties(_Model):
        connector_basic_info: Optional[ConnectorInfoBase]
        connector_service_type_info: Optional[ConnectorServiceTypeInfoBase]
        partner_connector_info: Optional[PartnerInfoBase]

        @overload
        def __init__(
                self, 
                *, 
                connector_basic_info: Optional[ConnectorInfoBase] = ..., 
                connector_service_type_info: Optional[ConnectorServiceTypeInfoBase] = ..., 
                partner_connector_info: Optional[PartnerInfoBase] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.confluent.models.ConnectorServiceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_BLOB_STORAGE_SINK_CONNECTOR = "AzureBlobStorageSinkConnector"
        AZURE_BLOB_STORAGE_SOURCE_CONNECTOR = "AzureBlobStorageSourceConnector"
        AZURE_COSMOS_DB_SINK_CONNECTOR = "AzureCosmosDBSinkConnector"
        AZURE_COSMOS_DB_SOURCE_CONNECTOR = "AzureCosmosDBSourceConnector"
        AZURE_SYNAPSE_ANALYTICS_SINK_CONNECTOR = "AzureSynapseAnalyticsSinkConnector"


    class azure.mgmt.confluent.models.ConnectorServiceTypeInfoBase(_Model):
        connector_service_type: str

        @overload
        def __init__(
                self, 
                *, 
                connector_service_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.confluent.models.ConnectorStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAILED = "FAILED"
        PAUSED = "PAUSED"
        PROVISIONING = "PROVISIONING"
        RUNNING = "RUNNING"


    class azure.mgmt.confluent.models.ConnectorType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SINK = "SINK"
        SOURCE = "SOURCE"


    class azure.mgmt.confluent.models.CreateAPIKeyModel(_Model):
        description: Optional[str]
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.confluent.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.confluent.models.DataFormatType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AVRO = "AVRO"
        BYTES = "BYTES"
        JSON = "JSON"
        PROTOBUF = "PROTOBUF"
        STRING = "STRING"


    class azure.mgmt.confluent.models.EnvironmentProperties(_Model):
        metadata: Optional[SCMetadataEntity]
        stream_governance_config: Optional[StreamGovernanceConfig]

        @overload
        def __init__(
                self, 
                *, 
                metadata: Optional[SCMetadataEntity] = ..., 
                stream_governance_config: Optional[StreamGovernanceConfig] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.confluent.models.EnvironmentRecord(_Model):
        display_name: Optional[str]
        id: Optional[str]
        kind: Optional[str]
        metadata: Optional[MetadataEntity]

        @overload
        def __init__(
                self, 
                *, 
                display_name: Optional[str] = ..., 
                id: Optional[str] = ..., 
                kind: Optional[str] = ..., 
                metadata: Optional[MetadataEntity] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.confluent.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.confluent.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.confluent.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.confluent.models.ErrorResponseBody(_Model):
        code: Optional[str]
        details: Optional[list[ErrorResponseBody]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.confluent.models.InvitationRecord(_Model):
        accepted_at: Optional[str]
        auth_type: Optional[str]
        email: Optional[str]
        expires_at: Optional[str]
        id: Optional[str]
        kind: Optional[str]
        metadata: Optional[MetadataEntity]
        status: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                accepted_at: Optional[str] = ..., 
                auth_type: Optional[str] = ..., 
                email: Optional[str] = ..., 
                expires_at: Optional[str] = ..., 
                id: Optional[str] = ..., 
                kind: Optional[str] = ..., 
                metadata: Optional[MetadataEntity] = ..., 
                status: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.confluent.models.KafkaAzureBlobStorageSinkConnectorInfo(PartnerInfoBase, discriminator='KafkaAzureBlobStorageSink'):
        api_key: Optional[str]
        api_secret: Optional[str]
        auth_type: Optional[Union[str, AuthType]]
        flush_size: Optional[str]
        input_format: Optional[Union[str, DataFormatType]]
        max_tasks: Optional[str]
        output_format: Optional[Union[str, DataFormatType]]
        partner_connector_type: Literal[PartnerConnectorType.KAFKA_AZURE_BLOB_STORAGE_SINK]
        service_account_id: Optional[str]
        service_account_name: Optional[str]
        time_interval: Optional[str]
        topics: Optional[list[str]]
        topics_dir: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                api_key: Optional[str] = ..., 
                api_secret: Optional[str] = ..., 
                auth_type: Optional[Union[str, AuthType]] = ..., 
                flush_size: Optional[str] = ..., 
                input_format: Optional[Union[str, DataFormatType]] = ..., 
                max_tasks: Optional[str] = ..., 
                output_format: Optional[Union[str, DataFormatType]] = ..., 
                service_account_id: Optional[str] = ..., 
                service_account_name: Optional[str] = ..., 
                time_interval: Optional[str] = ..., 
                topics: Optional[list[str]] = ..., 
                topics_dir: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.confluent.models.KafkaAzureBlobStorageSourceConnectorInfo(PartnerInfoBase, discriminator='KafkaAzureBlobStorageSource'):
        api_key: Optional[str]
        api_secret: Optional[str]
        auth_type: Optional[Union[str, AuthType]]
        input_format: Optional[Union[str, DataFormatType]]
        max_tasks: Optional[str]
        output_format: Optional[Union[str, DataFormatType]]
        partner_connector_type: Literal[PartnerConnectorType.KAFKA_AZURE_BLOB_STORAGE_SOURCE]
        service_account_id: Optional[str]
        service_account_name: Optional[str]
        topic_regex: Optional[str]
        topics_dir: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                api_key: Optional[str] = ..., 
                api_secret: Optional[str] = ..., 
                auth_type: Optional[Union[str, AuthType]] = ..., 
                input_format: Optional[Union[str, DataFormatType]] = ..., 
                max_tasks: Optional[str] = ..., 
                output_format: Optional[Union[str, DataFormatType]] = ..., 
                service_account_id: Optional[str] = ..., 
                service_account_name: Optional[str] = ..., 
                topic_regex: Optional[str] = ..., 
                topics_dir: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.confluent.models.KafkaAzureCosmosDBSinkConnectorInfo(PartnerInfoBase, discriminator='KafkaAzureCosmosDBSink'):
        api_key: Optional[str]
        api_secret: Optional[str]
        auth_type: Optional[Union[str, AuthType]]
        flush_size: Optional[str]
        input_format: Optional[Union[str, DataFormatType]]
        max_tasks: Optional[str]
        output_format: Optional[Union[str, DataFormatType]]
        partner_connector_type: Literal[PartnerConnectorType.KAFKA_AZURE_COSMOS_DB_SINK]
        service_account_id: Optional[str]
        service_account_name: Optional[str]
        time_interval: Optional[str]
        topics: Optional[list[str]]
        topics_dir: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                api_key: Optional[str] = ..., 
                api_secret: Optional[str] = ..., 
                auth_type: Optional[Union[str, AuthType]] = ..., 
                flush_size: Optional[str] = ..., 
                input_format: Optional[Union[str, DataFormatType]] = ..., 
                max_tasks: Optional[str] = ..., 
                output_format: Optional[Union[str, DataFormatType]] = ..., 
                service_account_id: Optional[str] = ..., 
                service_account_name: Optional[str] = ..., 
                time_interval: Optional[str] = ..., 
                topics: Optional[list[str]] = ..., 
                topics_dir: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.confluent.models.KafkaAzureCosmosDBSourceConnectorInfo(PartnerInfoBase, discriminator='KafkaAzureCosmosDBSource'):
        api_key: Optional[str]
        api_secret: Optional[str]
        auth_type: Optional[Union[str, AuthType]]
        input_format: Optional[Union[str, DataFormatType]]
        max_tasks: Optional[str]
        output_format: Optional[Union[str, DataFormatType]]
        partner_connector_type: Literal[PartnerConnectorType.KAFKA_AZURE_COSMOS_DB_SOURCE]
        service_account_id: Optional[str]
        service_account_name: Optional[str]
        topic_regex: Optional[str]
        topics_dir: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                api_key: Optional[str] = ..., 
                api_secret: Optional[str] = ..., 
                auth_type: Optional[Union[str, AuthType]] = ..., 
                input_format: Optional[Union[str, DataFormatType]] = ..., 
                max_tasks: Optional[str] = ..., 
                output_format: Optional[Union[str, DataFormatType]] = ..., 
                service_account_id: Optional[str] = ..., 
                service_account_name: Optional[str] = ..., 
                topic_regex: Optional[str] = ..., 
                topics_dir: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.confluent.models.KafkaAzureSynapseAnalyticsSinkConnectorInfo(PartnerInfoBase, discriminator='KafkaAzureSynapseAnalyticsSink'):
        api_key: Optional[str]
        api_secret: Optional[str]
        auth_type: Optional[Union[str, AuthType]]
        flush_size: Optional[str]
        input_format: Optional[Union[str, DataFormatType]]
        max_tasks: Optional[str]
        output_format: Optional[Union[str, DataFormatType]]
        partner_connector_type: Literal[PartnerConnectorType.KAFKA_AZURE_SYNAPSE_ANALYTICS_SINK]
        service_account_id: Optional[str]
        service_account_name: Optional[str]
        time_interval: Optional[str]
        topics: Optional[list[str]]
        topics_dir: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                api_key: Optional[str] = ..., 
                api_secret: Optional[str] = ..., 
                auth_type: Optional[Union[str, AuthType]] = ..., 
                flush_size: Optional[str] = ..., 
                input_format: Optional[Union[str, DataFormatType]] = ..., 
                max_tasks: Optional[str] = ..., 
                output_format: Optional[Union[str, DataFormatType]] = ..., 
                service_account_id: Optional[str] = ..., 
                service_account_name: Optional[str] = ..., 
                time_interval: Optional[str] = ..., 
                topics: Optional[list[str]] = ..., 
                topics_dir: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.confluent.models.KeyValuePair(_Model):
        key: str
        value: str

        @overload
        def __init__(
                self, 
                *, 
                key: str, 
                value: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.confluent.models.LatestLinkedSaaSResponse(_Model):
        is_hidden_saa_s: Optional[bool]
        saa_s_resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                is_hidden_saa_s: Optional[bool] = ..., 
                saa_s_resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.confluent.models.LinkOrganization(_Model):
        token: str

        @overload
        def __init__(
                self, 
                *, 
                token: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.confluent.models.ListAccessRequestModel(_Model):
        search_filters: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                search_filters: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.confluent.models.ListRegionsSuccessResponse(_Model):
        data: Optional[list[RegionRecord]]

        @overload
        def __init__(
                self, 
                *, 
                data: Optional[list[RegionRecord]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.confluent.models.MetadataEntity(_Model):
        created_at: Optional[str]
        deleted_at: Optional[str]
        resource_name: Optional[str]
        self_property: Optional[str]
        updated_at: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                created_at: Optional[str] = ..., 
                deleted_at: Optional[str] = ..., 
                resource_name: Optional[str] = ..., 
                self_property: Optional[str] = ..., 
                updated_at: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.confluent.models.NetworkGatewayProperties(_Model):
        dictionary: Optional[list[KeyValuePair]]
        metadata: Optional[SCMetadataEntity]
        network_gateway_name: str
        provisioning_state: Optional[Union[str, ProvisionState]]
        region: str

        @overload
        def __init__(
                self, 
                *, 
                dictionary: Optional[list[KeyValuePair]] = ..., 
                metadata: Optional[SCMetadataEntity] = ..., 
                network_gateway_name: str, 
                region: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.confluent.models.NetworkGatewayResource(ProxyResource):
        id: str
        name: str
        properties: Optional[NetworkGatewayProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[NetworkGatewayProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.confluent.models.OfferDetail(_Model):
        id: str
        plan_id: str
        plan_name: str
        private_offer_id: Optional[str]
        private_offer_ids: Optional[list[str]]
        publisher_id: str
        status: Optional[Union[str, SaaSOfferStatus]]
        term_id: Optional[str]
        term_unit: str

        @overload
        def __init__(
                self, 
                *, 
                id: str, 
                plan_id: str, 
                plan_name: str, 
                private_offer_id: Optional[str] = ..., 
                private_offer_ids: Optional[list[str]] = ..., 
                publisher_id: str, 
                status: Optional[Union[str, SaaSOfferStatus]] = ..., 
                term_id: Optional[str] = ..., 
                term_unit: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.confluent.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                operation: Optional[str] = ..., 
                provider: Optional[str] = ..., 
                resource: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.confluent.models.OperationResult(_Model):
        display: Optional[OperationDisplay]
        is_data_action: Optional[bool]
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                display: Optional[OperationDisplay] = ..., 
                is_data_action: Optional[bool] = ..., 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.confluent.models.OrganizationResource(TrackedResource):
        id: str
        location: str
        name: str
        properties: OrganizationResourceProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: OrganizationResourceProperties, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.confluent.models.OrganizationResourceProperties(_Model):
        created_time: Optional[datetime]
        link_organization: Optional[LinkOrganization]
        offer_detail: OfferDetail
        organization_id: Optional[str]
        provisioning_state: Optional[Union[str, ProvisionState]]
        sso_url: Optional[str]
        user_detail: UserDetail

        @overload
        def __init__(
                self, 
                *, 
                link_organization: Optional[LinkOrganization] = ..., 
                offer_detail: OfferDetail, 
                user_detail: UserDetail
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.confluent.models.OrganizationResourceUpdate(_Model):
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.confluent.models.Package(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ADVANCED = "ADVANCED"
        ESSENTIALS = "ESSENTIALS"


    class azure.mgmt.confluent.models.PartnerConnectorType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        KAFKA_AZURE_BLOB_STORAGE_SINK = "KafkaAzureBlobStorageSink"
        KAFKA_AZURE_BLOB_STORAGE_SOURCE = "KafkaAzureBlobStorageSource"
        KAFKA_AZURE_COSMOS_DB_SINK = "KafkaAzureCosmosDBSink"
        KAFKA_AZURE_COSMOS_DB_SOURCE = "KafkaAzureCosmosDBSource"
        KAFKA_AZURE_SYNAPSE_ANALYTICS_SINK = "KafkaAzureSynapseAnalyticsSink"


    class azure.mgmt.confluent.models.PartnerInfoBase(_Model):
        partner_connector_type: str

        @overload
        def __init__(
                self, 
                *, 
                partner_connector_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.confluent.models.ProvisionState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETED = "Deleted"
        DELETING = "Deleting"
        FAILED = "Failed"
        NOT_SPECIFIED = "NotSpecified"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.confluent.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.confluent.models.RegionProperties(_Model):
        metadata: Optional[SCMetadataEntity]
        spec: Optional[RegionSpecEntity]

        @overload
        def __init__(
                self, 
                *, 
                metadata: Optional[SCMetadataEntity] = ..., 
                spec: Optional[RegionSpecEntity] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.confluent.models.RegionRecord(_Model):
        id: Optional[str]
        kind: Optional[str]
        properties: Optional[RegionProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                kind: Optional[str] = ..., 
                properties: Optional[RegionProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.confluent.models.RegionSpecEntity(_Model):
        cloud: Optional[str]
        name: Optional[str]
        packages: Optional[list[str]]
        region_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                cloud: Optional[str] = ..., 
                name: Optional[str] = ..., 
                packages: Optional[list[str]] = ..., 
                region_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.confluent.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.confluent.models.ResourceProviderDefaultErrorResponse(_Model):
        error: Optional[ErrorResponseBody]


    class azure.mgmt.confluent.models.RoleBindingRecord(_Model):
        crn_pattern: Optional[str]
        id: Optional[str]
        kind: Optional[str]
        metadata: Optional[MetadataEntity]
        principal: Optional[str]
        role_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                crn_pattern: Optional[str] = ..., 
                id: Optional[str] = ..., 
                kind: Optional[str] = ..., 
                metadata: Optional[MetadataEntity] = ..., 
                principal: Optional[str] = ..., 
                role_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.confluent.models.SCClusterByokEntity(_Model):
        id: Optional[str]
        related: Optional[str]
        resource_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                related: Optional[str] = ..., 
                resource_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.confluent.models.SCClusterNetworkEnvironmentEntity(_Model):
        environment: Optional[str]
        id: Optional[str]
        related: Optional[str]
        resource_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                environment: Optional[str] = ..., 
                id: Optional[str] = ..., 
                related: Optional[str] = ..., 
                resource_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.confluent.models.SCClusterRecord(ProxyResource):
        id: str
        kind: Optional[str]
        name: str
        properties: Optional[ClusterProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                kind: Optional[str] = ..., 
                properties: Optional[ClusterProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.confluent.models.SCClusterSpecEntity(_Model):
        api_endpoint: Optional[str]
        availability: Optional[str]
        byok: Optional[SCClusterByokEntity]
        cloud: Optional[str]
        config: Optional[ClusterConfigEntity]
        environment: Optional[SCClusterNetworkEnvironmentEntity]
        http_endpoint: Optional[str]
        kafka_bootstrap_endpoint: Optional[str]
        name: Optional[str]
        network: Optional[SCClusterNetworkEnvironmentEntity]
        package: Optional[Union[str, Package]]
        region: Optional[str]
        zone: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                api_endpoint: Optional[str] = ..., 
                availability: Optional[str] = ..., 
                byok: Optional[SCClusterByokEntity] = ..., 
                cloud: Optional[str] = ..., 
                config: Optional[ClusterConfigEntity] = ..., 
                environment: Optional[SCClusterNetworkEnvironmentEntity] = ..., 
                http_endpoint: Optional[str] = ..., 
                kafka_bootstrap_endpoint: Optional[str] = ..., 
                name: Optional[str] = ..., 
                network: Optional[SCClusterNetworkEnvironmentEntity] = ..., 
                package: Optional[Union[str, Package]] = ..., 
                region: Optional[str] = ..., 
                zone: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.confluent.models.SCEnvironmentRecord(ProxyResource):
        id: str
        kind: Optional[str]
        name: str
        properties: Optional[EnvironmentProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                kind: Optional[str] = ..., 
                properties: Optional[EnvironmentProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.confluent.models.SCMetadataEntity(_Model):
        created_timestamp: Optional[str]
        deleted_timestamp: Optional[str]
        resource_name: Optional[str]
        self_property: Optional[str]
        updated_timestamp: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                created_timestamp: Optional[str] = ..., 
                deleted_timestamp: Optional[str] = ..., 
                resource_name: Optional[str] = ..., 
                self_property: Optional[str] = ..., 
                updated_timestamp: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.confluent.models.SaaSData(_Model):
        saa_s_resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                saa_s_resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.confluent.models.SaaSOfferStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAILED = "Failed"
        IN_PROGRESS = "InProgress"
        PENDING_FULFILLMENT_START = "PendingFulfillmentStart"
        REINSTATED = "Reinstated"
        STARTED = "Started"
        SUBSCRIBED = "Subscribed"
        SUCCEEDED = "Succeeded"
        SUSPENDED = "Suspended"
        UNSUBSCRIBED = "Unsubscribed"
        UPDATING = "Updating"


    class azure.mgmt.confluent.models.SaaSResourceDetailsResponse(Resource):
        id: str
        name: str
        saas_id: Optional[str]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                saas_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.confluent.models.SchemaRegistryClusterEnvironmentRegionEntity(_Model):
        id: Optional[str]
        related: Optional[str]
        resource_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                related: Optional[str] = ..., 
                resource_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.confluent.models.SchemaRegistryClusterProperties(_Model):
        metadata: Optional[SCMetadataEntity]
        spec: Optional[SchemaRegistryClusterSpecEntity]
        status: Optional[SchemaRegistryClusterStatusEntity]

        @overload
        def __init__(
                self, 
                *, 
                metadata: Optional[SCMetadataEntity] = ..., 
                spec: Optional[SchemaRegistryClusterSpecEntity] = ..., 
                status: Optional[SchemaRegistryClusterStatusEntity] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.confluent.models.SchemaRegistryClusterRecord(_Model):
        id: Optional[str]
        kind: Optional[str]
        properties: Optional[SchemaRegistryClusterProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                kind: Optional[str] = ..., 
                properties: Optional[SchemaRegistryClusterProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.confluent.models.SchemaRegistryClusterSpecEntity(_Model):
        cloud: Optional[str]
        environment: Optional[SchemaRegistryClusterEnvironmentRegionEntity]
        http_endpoint: Optional[str]
        name: Optional[str]
        package: Optional[str]
        region: Optional[SchemaRegistryClusterEnvironmentRegionEntity]

        @overload
        def __init__(
                self, 
                *, 
                cloud: Optional[str] = ..., 
                environment: Optional[SchemaRegistryClusterEnvironmentRegionEntity] = ..., 
                http_endpoint: Optional[str] = ..., 
                name: Optional[str] = ..., 
                package: Optional[str] = ..., 
                region: Optional[SchemaRegistryClusterEnvironmentRegionEntity] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.confluent.models.SchemaRegistryClusterStatusEntity(_Model):
        phase: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                phase: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.confluent.models.ServiceAccountRecord(_Model):
        description: Optional[str]
        display_name: Optional[str]
        id: Optional[str]
        kind: Optional[str]
        metadata: Optional[MetadataEntity]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                id: Optional[str] = ..., 
                kind: Optional[str] = ..., 
                metadata: Optional[MetadataEntity] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.confluent.models.StreamGovernanceConfig(_Model):
        package: Optional[Union[str, Package]]

        @overload
        def __init__(
                self, 
                *, 
                package: Optional[Union[str, Package]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.confluent.models.SystemData(_Model):
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


    class azure.mgmt.confluent.models.TopicMetadataEntity(_Model):
        resource_name: Optional[str]
        self_property: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                resource_name: Optional[str] = ..., 
                self_property: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.confluent.models.TopicProperties(_Model):
        configs: Optional[TopicsRelatedLink]
        input_configs: Optional[list[TopicsInputConfig]]
        kind: Optional[str]
        metadata: Optional[TopicMetadataEntity]
        partitions: Optional[TopicsRelatedLink]
        partitions_count: Optional[str]
        partitions_reassignments: Optional[TopicsRelatedLink]
        replication_factor: Optional[str]
        topic_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                configs: Optional[TopicsRelatedLink] = ..., 
                input_configs: Optional[list[TopicsInputConfig]] = ..., 
                kind: Optional[str] = ..., 
                metadata: Optional[TopicMetadataEntity] = ..., 
                partitions: Optional[TopicsRelatedLink] = ..., 
                partitions_count: Optional[str] = ..., 
                partitions_reassignments: Optional[TopicsRelatedLink] = ..., 
                replication_factor: Optional[str] = ..., 
                topic_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.confluent.models.TopicRecord(ProxyResource):
        id: str
        name: str
        properties: Optional[TopicProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[TopicProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.confluent.models.TopicsInputConfig(_Model):
        name: Optional[str]
        value: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                value: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.confluent.models.TopicsRelatedLink(_Model):
        related: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                related: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.confluent.models.TrackedResource(Resource):
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


    class azure.mgmt.confluent.models.UserDetail(_Model):
        aad_email: Optional[str]
        email_address: str
        first_name: Optional[str]
        last_name: Optional[str]
        user_principal_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                aad_email: Optional[str] = ..., 
                email_address: str, 
                first_name: Optional[str] = ..., 
                last_name: Optional[str] = ..., 
                user_principal_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.confluent.models.UserRecord(_Model):
        auth_type: Optional[str]
        email: Optional[str]
        full_name: Optional[str]
        id: Optional[str]
        kind: Optional[str]
        metadata: Optional[MetadataEntity]

        @overload
        def __init__(
                self, 
                *, 
                auth_type: Optional[str] = ..., 
                email: Optional[str] = ..., 
                full_name: Optional[str] = ..., 
                id: Optional[str] = ..., 
                kind: Optional[str] = ..., 
                metadata: Optional[MetadataEntity] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.confluent.models.ValidationResponse(_Model):
        info: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                info: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.confluent.models.VnetInjectionDetails(_Model):
        subnet_resource_id: str
        virtual_network_resource_id: str

        @overload
        def __init__(
                self, 
                *, 
                subnet_resource_id: str, 
                virtual_network_resource_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


namespace azure.mgmt.confluent.operations

    class azure.mgmt.confluent.operations.AccessOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_role_binding(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                body: AccessCreateRoleBindingRequestModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RoleBindingRecord: ...

        @overload
        def create_role_binding(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                body: AccessCreateRoleBindingRequestModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RoleBindingRecord: ...

        @overload
        def create_role_binding(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RoleBindingRecord: ...

        @distributed_trace
        def delete_role_binding(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                role_binding_id: str, 
                **kwargs: Any
            ) -> None: ...

        @overload
        def invite_user(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                body: AccessInviteUserAccountModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> InvitationRecord: ...

        @overload
        def invite_user(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                body: AccessInviteUserAccountModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> InvitationRecord: ...

        @overload
        def invite_user(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> InvitationRecord: ...

        @overload
        def list_clusters(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                body: ListAccessRequestModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AccessListClusterSuccessResponse: ...

        @overload
        def list_clusters(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                body: ListAccessRequestModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AccessListClusterSuccessResponse: ...

        @overload
        def list_clusters(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AccessListClusterSuccessResponse: ...

        @overload
        def list_environments(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                body: ListAccessRequestModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AccessListEnvironmentsSuccessResponse: ...

        @overload
        def list_environments(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                body: ListAccessRequestModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AccessListEnvironmentsSuccessResponse: ...

        @overload
        def list_environments(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AccessListEnvironmentsSuccessResponse: ...

        @overload
        def list_invitations(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                body: ListAccessRequestModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AccessListInvitationsSuccessResponse: ...

        @overload
        def list_invitations(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                body: ListAccessRequestModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AccessListInvitationsSuccessResponse: ...

        @overload
        def list_invitations(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AccessListInvitationsSuccessResponse: ...

        @overload
        def list_role_binding_name_list(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                body: ListAccessRequestModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AccessRoleBindingNameListSuccessResponse: ...

        @overload
        def list_role_binding_name_list(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                body: ListAccessRequestModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AccessRoleBindingNameListSuccessResponse: ...

        @overload
        def list_role_binding_name_list(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AccessRoleBindingNameListSuccessResponse: ...

        @overload
        def list_role_bindings(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                body: ListAccessRequestModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AccessListRoleBindingsSuccessResponse: ...

        @overload
        def list_role_bindings(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                body: ListAccessRequestModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AccessListRoleBindingsSuccessResponse: ...

        @overload
        def list_role_bindings(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AccessListRoleBindingsSuccessResponse: ...

        @overload
        def list_service_accounts(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                body: ListAccessRequestModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AccessListServiceAccountsSuccessResponse: ...

        @overload
        def list_service_accounts(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                body: ListAccessRequestModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AccessListServiceAccountsSuccessResponse: ...

        @overload
        def list_service_accounts(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AccessListServiceAccountsSuccessResponse: ...

        @overload
        def list_users(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                body: ListAccessRequestModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AccessListUsersSuccessResponse: ...

        @overload
        def list_users(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                body: ListAccessRequestModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AccessListUsersSuccessResponse: ...

        @overload
        def list_users(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AccessListUsersSuccessResponse: ...


    class azure.mgmt.confluent.operations.AccessPointResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                environment_id: str, 
                network_gateway_id: str, 
                access_point_id: str, 
                resource: AccessPointResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AccessPointResource]: ...

        @overload
        def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                environment_id: str, 
                network_gateway_id: str, 
                access_point_id: str, 
                resource: AccessPointResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AccessPointResource]: ...

        @overload
        def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                environment_id: str, 
                network_gateway_id: str, 
                access_point_id: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AccessPointResource]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'organization_name', 'environment_id', 'network_gateway_id', 'access_point_id']}, api_versions_list=['2026-05-01-preview', '2026-06-02-preview'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                environment_id: str, 
                network_gateway_id: str, 
                access_point_id: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'organization_name', 'environment_id', 'network_gateway_id', 'access_point_id', 'accept']}, api_versions_list=['2026-05-01-preview', '2026-06-02-preview'])
        def get(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                environment_id: str, 
                network_gateway_id: str, 
                access_point_id: str, 
                **kwargs: Any
            ) -> AccessPointResource: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'organization_name', 'environment_id', 'network_gateway_id', 'accept']}, api_versions_list=['2026-05-01-preview', '2026-06-02-preview'])
        def list(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                environment_id: str, 
                network_gateway_id: str, 
                **kwargs: Any
            ) -> ItemPaged[AccessPointResource]: ...


    class azure.mgmt.confluent.operations.ClusterOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                environment_id: str, 
                cluster_id: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                environment_id: str, 
                cluster_id: str, 
                body: Optional[SCClusterRecord] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SCClusterRecord: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                environment_id: str, 
                cluster_id: str, 
                body: Optional[SCClusterRecord] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SCClusterRecord: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                environment_id: str, 
                cluster_id: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SCClusterRecord: ...


    class azure.mgmt.confluent.operations.ConnectorOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                environment_id: str, 
                cluster_id: str, 
                connector_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                environment_id: str, 
                cluster_id: str, 
                connector_name: str, 
                body: Optional[ConnectorResource] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConnectorResource: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                environment_id: str, 
                cluster_id: str, 
                connector_name: str, 
                body: Optional[ConnectorResource] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConnectorResource: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                environment_id: str, 
                cluster_id: str, 
                connector_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConnectorResource: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                environment_id: str, 
                cluster_id: str, 
                connector_name: str, 
                **kwargs: Any
            ) -> ConnectorResource: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                environment_id: str, 
                cluster_id: str, 
                *, 
                page_size: Optional[int] = ..., 
                page_token: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[ConnectorResource]: ...


    class azure.mgmt.confluent.operations.EnvironmentOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                environment_id: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                environment_id: str, 
                body: Optional[SCEnvironmentRecord] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SCEnvironmentRecord: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                environment_id: str, 
                body: Optional[SCEnvironmentRecord] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SCEnvironmentRecord: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                environment_id: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SCEnvironmentRecord: ...


    class azure.mgmt.confluent.operations.MarketplaceAgreementsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create(
                self, 
                body: Optional[ConfluentAgreementResource] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConfluentAgreementResource: ...

        @overload
        def create(
                self, 
                body: Optional[ConfluentAgreementResource] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConfluentAgreementResource: ...

        @overload
        def create(
                self, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConfluentAgreementResource: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[ConfluentAgreementResource]: ...


    class azure.mgmt.confluent.operations.NetworkGatewayResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                environment_id: str, 
                network_gateway_id: str, 
                resource: NetworkGatewayResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetworkGatewayResource]: ...

        @overload
        def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                environment_id: str, 
                network_gateway_id: str, 
                resource: NetworkGatewayResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetworkGatewayResource]: ...

        @overload
        def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                environment_id: str, 
                network_gateway_id: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetworkGatewayResource]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'organization_name', 'environment_id', 'network_gateway_id']}, api_versions_list=['2026-05-01-preview', '2026-06-02-preview'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                environment_id: str, 
                network_gateway_id: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'organization_name', 'environment_id', 'network_gateway_id', 'accept']}, api_versions_list=['2026-05-01-preview', '2026-06-02-preview'])
        def get(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                environment_id: str, 
                network_gateway_id: str, 
                **kwargs: Any
            ) -> NetworkGatewayResource: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'organization_name', 'environment_id', 'accept']}, api_versions_list=['2026-05-01-preview', '2026-06-02-preview'])
        def list(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                environment_id: str, 
                **kwargs: Any
            ) -> ItemPaged[NetworkGatewayResource]: ...


    class azure.mgmt.confluent.operations.OrganizationOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_activate_resource(
                self, 
                body: ActivateSaaSParameterRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SaaSResourceDetailsResponse]: ...

        @overload
        def begin_activate_resource(
                self, 
                body: ActivateSaaSParameterRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SaaSResourceDetailsResponse]: ...

        @overload
        def begin_activate_resource(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SaaSResourceDetailsResponse]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                body: Optional[OrganizationResource] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OrganizationResource]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                body: Optional[OrganizationResource] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OrganizationResource]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OrganizationResource]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_link_saa_s(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                body: SaaSData, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OrganizationResource]: ...

        @overload
        def begin_link_saa_s(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                body: SaaSData, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OrganizationResource]: ...

        @overload
        def begin_link_saa_s(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OrganizationResource]: ...

        @overload
        def create_api_key(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                environment_id: str, 
                cluster_id: str, 
                body: CreateAPIKeyModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> APIKeyRecord: ...

        @overload
        def create_api_key(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                environment_id: str, 
                cluster_id: str, 
                body: CreateAPIKeyModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> APIKeyRecord: ...

        @overload
        def create_api_key(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                environment_id: str, 
                cluster_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> APIKeyRecord: ...

        @distributed_trace
        def delete_cluster_api_key(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                api_key_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                **kwargs: Any
            ) -> OrganizationResource: ...

        @distributed_trace
        def get_cluster_api_key(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                api_key_id: str, 
                **kwargs: Any
            ) -> APIKeyRecord: ...

        @distributed_trace
        def get_cluster_by_id(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                environment_id: str, 
                cluster_id: str, 
                **kwargs: Any
            ) -> SCClusterRecord: ...

        @distributed_trace
        def get_environment_by_id(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                environment_id: str, 
                **kwargs: Any
            ) -> SCEnvironmentRecord: ...

        @distributed_trace
        def get_schema_registry_cluster_by_id(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                environment_id: str, 
                cluster_id: str, 
                **kwargs: Any
            ) -> SchemaRegistryClusterRecord: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-06-02-preview', params_added_on={'2026-06-02-preview': ['api_version', 'subscription_id', 'resource_group_name', 'organization_name', 'accept']}, api_versions_list=['2026-06-02-preview'])
        def latest_linked_saa_s(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                **kwargs: Any
            ) -> LatestLinkedSaaSResponse: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[OrganizationResource]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[OrganizationResource]: ...

        @distributed_trace
        def list_clusters(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                environment_id: str, 
                *, 
                page_size: Optional[int] = ..., 
                page_token: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[SCClusterRecord]: ...

        @distributed_trace
        def list_environments(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                *, 
                page_size: Optional[int] = ..., 
                page_token: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[SCEnvironmentRecord]: ...

        @overload
        def list_regions(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                body: ListAccessRequestModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ListRegionsSuccessResponse: ...

        @overload
        def list_regions(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                body: ListAccessRequestModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ListRegionsSuccessResponse: ...

        @overload
        def list_regions(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ListRegionsSuccessResponse: ...

        @distributed_trace
        def list_schema_registry_clusters(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                environment_id: str, 
                *, 
                page_size: Optional[int] = ..., 
                page_token: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[SchemaRegistryClusterRecord]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                body: Optional[OrganizationResourceUpdate] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> OrganizationResource: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                body: Optional[OrganizationResourceUpdate] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> OrganizationResource: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> OrganizationResource: ...


    class azure.mgmt.confluent.operations.OrganizationOperationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[OperationResult]: ...


    class azure.mgmt.confluent.operations.TopicsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                environment_id: str, 
                cluster_id: str, 
                topic_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                environment_id: str, 
                cluster_id: str, 
                topic_name: str, 
                body: Optional[TopicRecord] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TopicRecord: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                environment_id: str, 
                cluster_id: str, 
                topic_name: str, 
                body: Optional[TopicRecord] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TopicRecord: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                environment_id: str, 
                cluster_id: str, 
                topic_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TopicRecord: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                environment_id: str, 
                cluster_id: str, 
                topic_name: str, 
                **kwargs: Any
            ) -> TopicRecord: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                environment_id: str, 
                cluster_id: str, 
                *, 
                page_size: Optional[int] = ..., 
                page_token: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[TopicRecord]: ...


    class azure.mgmt.confluent.operations.ValidationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def validate_organization(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                body: OrganizationResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> OrganizationResource: ...

        @overload
        def validate_organization(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                body: OrganizationResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> OrganizationResource: ...

        @overload
        def validate_organization(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> OrganizationResource: ...

        @overload
        def validate_organization_v2(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                body: OrganizationResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ValidationResponse: ...

        @overload
        def validate_organization_v2(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                body: OrganizationResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ValidationResponse: ...

        @overload
        def validate_organization_v2(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ValidationResponse: ...


namespace azure.mgmt.confluent.types

    class azure.mgmt.confluent.types.AccessCreateRoleBindingRequestModel(TypedDict, total=False):
        key "crn_pattern": str
        key "principal": str
        key "role_name": str
        crn_pattern: str
        principal: str
        role_name: str


    class azure.mgmt.confluent.types.AccessInviteUserAccountModel(TypedDict, total=False):
        key "email": str
        key "invitedUserDetails": ForwardRef('AccessInvitedUserDetails', module='types')
        key "organizationId": str
        key "upn": str
        email: str
        invited_user_details: AccessInvitedUserDetails
        organization_id: str
        upn: str


    class azure.mgmt.confluent.types.AccessInvitedUserDetails(TypedDict, total=False):
        key "auth_type": str
        key "invitedEmail": str
        auth_type: str
        invited_email: str


    class azure.mgmt.confluent.types.AccessPointProperties(TypedDict, total=False):
        key "accessPointName": Required[str]
        key "metadata": ForwardRef('SCMetadataEntity', module='types')
        key "provisioningState": Union[str, ProvisionState]
        key "region": Required[str]
        key "vnetInjection": Required[VnetInjectionDetails]
        access_point_name: str
        dictionary: list[KeyValuePair]
        egressRoutes: list[str]
        egress_routes: list[str]
        metadata: SCMetadataEntity
        provisioning_state: Union[str, ProvisionState]
        region: str
        vnet_injection: VnetInjectionDetails


    class azure.mgmt.confluent.types.AccessPointResource(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('AccessPointProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: AccessPointProperties
        system_data: SystemData
        type: str


    class azure.mgmt.confluent.types.ActivateSaaSParameterRequest(TypedDict, total=False):
        key "publisherId": str
        key "saasGuid": Required[str]
        publisher_id: str
        saas_guid: str


    class azure.mgmt.confluent.types.AzureBlobStorageSinkConnectorServiceInfo(TypedDict, total=False):
        key "connectorServiceType": Required[Literal[ConnectorServiceType.AZURE_BLOB_STORAGE_SINK_CONNECTOR]]
        key "storageAccountKey": str
        key "storageAccountName": str
        key "storageContainerName": str
        connector_service_type: Literal[ConnectorServiceType.AZURE_BLOB_STORAGE_SINK_CONNECTOR]
        storage_account_key: str
        storage_account_name: str
        storage_container_name: str


    class azure.mgmt.confluent.types.AzureBlobStorageSourceConnectorServiceInfo(TypedDict, total=False):
        key "connectorServiceType": Required[Literal[ConnectorServiceType.AZURE_BLOB_STORAGE_SOURCE_CONNECTOR]]
        key "storageAccountKey": str
        key "storageAccountName": str
        key "storageContainerName": str
        connector_service_type: Literal[ConnectorServiceType.AZURE_BLOB_STORAGE_SOURCE_CONNECTOR]
        storage_account_key: str
        storage_account_name: str
        storage_container_name: str


    class azure.mgmt.confluent.types.AzureCosmosDBSinkConnectorServiceInfo(TypedDict, total=False):
        key "connectorServiceType": Required[Literal[ConnectorServiceType.AZURE_COSMOS_DB_SINK_CONNECTOR]]
        key "cosmosConnectionEndpoint": str
        key "cosmosContainersTopicMapping": str
        key "cosmosDatabaseName": str
        key "cosmosIdStrategy": str
        key "cosmosMasterKey": str
        key "cosmosWriteDetails": str
        connector_service_type: Literal[ConnectorServiceType.AZURE_COSMOS_DB_SINK_CONNECTOR]
        cosmos_connection_endpoint: str
        cosmos_containers_topic_mapping: str
        cosmos_database_name: str
        cosmos_id_strategy: str
        cosmos_master_key: str
        cosmos_write_details: str


    class azure.mgmt.confluent.types.AzureCosmosDBSourceConnectorServiceInfo(TypedDict, total=False):
        key "connectorServiceType": Required[Literal[ConnectorServiceType.AZURE_COSMOS_DB_SOURCE_CONNECTOR]]
        key "cosmosConnectionEndpoint": str
        key "cosmosContainersTopicMapping": str
        key "cosmosDatabaseName": str
        key "cosmosIncludeAllContainers": str
        key "cosmosMasterKey": str
        key "cosmosMessageKeyEnabled": bool
        key "cosmosMessageKeyField": str
        connector_service_type: Literal[ConnectorServiceType.AZURE_COSMOS_DB_SOURCE_CONNECTOR]
        cosmos_connection_endpoint: str
        cosmos_containers_topic_mapping: str
        cosmos_database_name: str
        cosmos_include_all_containers: str
        cosmos_master_key: str
        cosmos_message_key_enabled: bool
        cosmos_message_key_field: str


    class azure.mgmt.confluent.types.AzureSynapseAnalyticsSinkConnectorServiceInfo(TypedDict, total=False):
        key "connectorServiceType": Required[Literal[ConnectorServiceType.AZURE_SYNAPSE_ANALYTICS_SINK_CONNECTOR]]
        key "synapseSqlDatabaseName": str
        key "synapseSqlPassword": str
        key "synapseSqlServerName": str
        key "synapseSqlUser": str
        connector_service_type: Literal[ConnectorServiceType.AZURE_SYNAPSE_ANALYTICS_SINK_CONNECTOR]
        synapse_sql_database_name: str
        synapse_sql_password: str
        synapse_sql_server_name: str
        synapse_sql_user: str


    class azure.mgmt.confluent.types.ClusterConfigEntity(TypedDict, total=False):
        key "kind": str
        kind: str


    class azure.mgmt.confluent.types.ClusterProperties(TypedDict, total=False):
        key "metadata": ForwardRef('SCMetadataEntity', module='types')
        key "spec": ForwardRef('SCClusterSpecEntity', module='types')
        key "status": ForwardRef('ClusterStatusEntity', module='types')
        metadata: SCMetadataEntity
        spec: SCClusterSpecEntity
        status: ClusterStatusEntity


    class azure.mgmt.confluent.types.ClusterStatusEntity(TypedDict, total=False):
        key "cku": int
        key "phase": str
        cku: int
        phase: str


    class azure.mgmt.confluent.types.ConfluentAgreementProperties(TypedDict, total=False):
        key "accepted": bool
        key "licenseTextLink": str
        key "plan": str
        key "privacyPolicyLink": str
        key "product": str
        key "publisher": str
        key "retrieveDatetime": str
        key "signature": str
        accepted: bool
        license_text_link: str
        plan: str
        privacy_policy_link: str
        product: str
        publisher: str
        retrieve_datetime: str
        signature: str


    class azure.mgmt.confluent.types.ConfluentAgreementResource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "properties": ForwardRef('ConfluentAgreementProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: ConfluentAgreementProperties
        system_data: SystemData
        type: str


    class azure.mgmt.confluent.types.ConnectorInfoBase(TypedDict, total=False):
        key "connectorClass": Union[str, ConnectorClass]
        key "connectorId": str
        key "connectorName": str
        key "connectorState": Union[str, ConnectorStatus]
        key "connectorType": Union[str, ConnectorType]
        connector_class: Union[str, ConnectorClass]
        connector_id: str
        connector_name: str
        connector_state: Union[str, ConnectorStatus]
        connector_type: Union[str, ConnectorType]


    class azure.mgmt.confluent.types.ConnectorResource(ProxyResource):
        key "id": str
        key "name": str
        key "properties": Required[ConnectorResourceProperties]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: ConnectorResourceProperties
        system_data: SystemData
        type: str


    class azure.mgmt.confluent.types.ConnectorResourceProperties(TypedDict, total=False):
        key "connectorBasicInfo": ForwardRef('ConnectorInfoBase', module='types')
        key "connectorServiceTypeInfo": ForwardRef('ConnectorServiceTypeInfoBase', module='types')
        key "partnerConnectorInfo": ForwardRef('PartnerInfoBase', module='types')
        connector_basic_info: ConnectorInfoBase
        connector_service_type_info: ConnectorServiceTypeInfoBase
        partner_connector_info: PartnerInfoBase


    class azure.mgmt.confluent.types.ConnectorServiceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_BLOB_STORAGE_SINK_CONNECTOR = "AzureBlobStorageSinkConnector"
        AZURE_BLOB_STORAGE_SOURCE_CONNECTOR = "AzureBlobStorageSourceConnector"
        AZURE_COSMOS_DB_SINK_CONNECTOR = "AzureCosmosDBSinkConnector"
        AZURE_COSMOS_DB_SOURCE_CONNECTOR = "AzureCosmosDBSourceConnector"
        AZURE_SYNAPSE_ANALYTICS_SINK_CONNECTOR = "AzureSynapseAnalyticsSinkConnector"


    class azure.mgmt.confluent.types.CreateAPIKeyModel(TypedDict, total=False):
        key "description": str
        key "name": str
        description: str
        name: str


    class azure.mgmt.confluent.types.EnvironmentProperties(TypedDict, total=False):
        key "metadata": ForwardRef('SCMetadataEntity', module='types')
        key "streamGovernanceConfig": ForwardRef('StreamGovernanceConfig', module='types')
        metadata: SCMetadataEntity
        stream_governance_config: StreamGovernanceConfig


    class azure.mgmt.confluent.types.KafkaAzureBlobStorageSinkConnectorInfo(TypedDict, total=False):
        key "apiKey": str
        key "apiSecret": str
        key "authType": Union[str, AuthType]
        key "flushSize": str
        key "inputFormat": Union[str, DataFormatType]
        key "maxTasks": str
        key "outputFormat": Union[str, DataFormatType]
        key "partnerConnectorType": Required[Literal[PartnerConnectorType.KAFKA_AZURE_BLOB_STORAGE_SINK]]
        key "serviceAccountId": str
        key "serviceAccountName": str
        key "timeInterval": str
        key "topicsDir": str
        api_key: str
        api_secret: str
        auth_type: Union[str, AuthType]
        flush_size: str
        input_format: Union[str, DataFormatType]
        max_tasks: str
        output_format: Union[str, DataFormatType]
        partner_connector_type: Literal[PartnerConnectorType.KAFKA_AZURE_BLOB_STORAGE_SINK]
        service_account_id: str
        service_account_name: str
        time_interval: str
        topics: list[str]
        topics_dir: str


    class azure.mgmt.confluent.types.KafkaAzureBlobStorageSourceConnectorInfo(TypedDict, total=False):
        key "apiKey": str
        key "apiSecret": str
        key "authType": Union[str, AuthType]
        key "inputFormat": Union[str, DataFormatType]
        key "maxTasks": str
        key "outputFormat": Union[str, DataFormatType]
        key "partnerConnectorType": Required[Literal[PartnerConnectorType.KAFKA_AZURE_BLOB_STORAGE_SOURCE]]
        key "serviceAccountId": str
        key "serviceAccountName": str
        key "topicRegex": str
        key "topicsDir": str
        api_key: str
        api_secret: str
        auth_type: Union[str, AuthType]
        input_format: Union[str, DataFormatType]
        max_tasks: str
        output_format: Union[str, DataFormatType]
        partner_connector_type: Literal[PartnerConnectorType.KAFKA_AZURE_BLOB_STORAGE_SOURCE]
        service_account_id: str
        service_account_name: str
        topic_regex: str
        topics_dir: str


    class azure.mgmt.confluent.types.KafkaAzureCosmosDBSinkConnectorInfo(TypedDict, total=False):
        key "apiKey": str
        key "apiSecret": str
        key "authType": Union[str, AuthType]
        key "flushSize": str
        key "inputFormat": Union[str, DataFormatType]
        key "maxTasks": str
        key "outputFormat": Union[str, DataFormatType]
        key "partnerConnectorType": Required[Literal[PartnerConnectorType.KAFKA_AZURE_COSMOS_DB_SINK]]
        key "serviceAccountId": str
        key "serviceAccountName": str
        key "timeInterval": str
        key "topicsDir": str
        api_key: str
        api_secret: str
        auth_type: Union[str, AuthType]
        flush_size: str
        input_format: Union[str, DataFormatType]
        max_tasks: str
        output_format: Union[str, DataFormatType]
        partner_connector_type: Literal[PartnerConnectorType.KAFKA_AZURE_COSMOS_DB_SINK]
        service_account_id: str
        service_account_name: str
        time_interval: str
        topics: list[str]
        topics_dir: str


    class azure.mgmt.confluent.types.KafkaAzureCosmosDBSourceConnectorInfo(TypedDict, total=False):
        key "apiKey": str
        key "apiSecret": str
        key "authType": Union[str, AuthType]
        key "inputFormat": Union[str, DataFormatType]
        key "maxTasks": str
        key "outputFormat": Union[str, DataFormatType]
        key "partnerConnectorType": Required[Literal[PartnerConnectorType.KAFKA_AZURE_COSMOS_DB_SOURCE]]
        key "serviceAccountId": str
        key "serviceAccountName": str
        key "topicRegex": str
        key "topicsDir": str
        api_key: str
        api_secret: str
        auth_type: Union[str, AuthType]
        input_format: Union[str, DataFormatType]
        max_tasks: str
        output_format: Union[str, DataFormatType]
        partner_connector_type: Literal[PartnerConnectorType.KAFKA_AZURE_COSMOS_DB_SOURCE]
        service_account_id: str
        service_account_name: str
        topic_regex: str
        topics_dir: str


    class azure.mgmt.confluent.types.KafkaAzureSynapseAnalyticsSinkConnectorInfo(TypedDict, total=False):
        key "apiKey": str
        key "apiSecret": str
        key "authType": Union[str, AuthType]
        key "flushSize": str
        key "inputFormat": Union[str, DataFormatType]
        key "maxTasks": str
        key "outputFormat": Union[str, DataFormatType]
        key "partnerConnectorType": Required[Literal[PartnerConnectorType.KAFKA_AZURE_SYNAPSE_ANALYTICS_SINK]]
        key "serviceAccountId": str
        key "serviceAccountName": str
        key "timeInterval": str
        key "topicsDir": str
        api_key: str
        api_secret: str
        auth_type: Union[str, AuthType]
        flush_size: str
        input_format: Union[str, DataFormatType]
        max_tasks: str
        output_format: Union[str, DataFormatType]
        partner_connector_type: Literal[PartnerConnectorType.KAFKA_AZURE_SYNAPSE_ANALYTICS_SINK]
        service_account_id: str
        service_account_name: str
        time_interval: str
        topics: list[str]
        topics_dir: str


    class azure.mgmt.confluent.types.KeyValuePair(TypedDict, total=False):
        key "key": Required[str]
        key "value": Required[str]
        key: str
        value: str


    class azure.mgmt.confluent.types.LinkOrganization(TypedDict, total=False):
        key "token": Required[str]
        token: str


    class azure.mgmt.confluent.types.ListAccessRequestModel(TypedDict, total=False):
        searchFilters: dict[str, str]
        search_filters: dict[str, str]


    class azure.mgmt.confluent.types.NetworkGatewayProperties(TypedDict, total=False):
        key "metadata": ForwardRef('SCMetadataEntity', module='types')
        key "networkGatewayName": Required[str]
        key "provisioningState": Union[str, ProvisionState]
        key "region": Required[str]
        dictionary: list[KeyValuePair]
        metadata: SCMetadataEntity
        network_gateway_name: str
        provisioning_state: Union[str, ProvisionState]
        region: str


    class azure.mgmt.confluent.types.NetworkGatewayResource(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('NetworkGatewayProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: NetworkGatewayProperties
        system_data: SystemData
        type: str


    class azure.mgmt.confluent.types.OfferDetail(TypedDict, total=False):
        key "id": Required[str]
        key "planId": Required[str]
        key "planName": Required[str]
        key "privateOfferId": str
        key "publisherId": Required[str]
        key "status": Union[str, SaaSOfferStatus]
        key "termId": str
        key "termUnit": Required[str]
        id: str
        plan_id: str
        plan_name: str
        privateOfferIds: list[str]
        private_offer_id: str
        private_offer_ids: list[str]
        publisher_id: str
        status: Union[str, SaaSOfferStatus]
        term_id: str
        term_unit: str


    class azure.mgmt.confluent.types.OrganizationResource(TrackedResource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": Required[OrganizationResourceProperties]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: OrganizationResourceProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.confluent.types.OrganizationResourceProperties(TypedDict, total=False):
        key "createdTime": str
        key "linkOrganization": ForwardRef('LinkOrganization', module='types')
        key "offerDetail": Required[OfferDetail]
        key "organizationId": str
        key "provisioningState": Union[str, ProvisionState]
        key "ssoUrl": str
        key "userDetail": Required[UserDetail]
        created_time: str
        link_organization: LinkOrganization
        offer_detail: OfferDetail
        organization_id: str
        provisioning_state: Union[str, ProvisionState]
        sso_url: str
        user_detail: UserDetail


    class azure.mgmt.confluent.types.OrganizationResourceUpdate(TypedDict, total=False):
        tags: dict[str, str]


    class azure.mgmt.confluent.types.PartnerConnectorType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        KAFKA_AZURE_BLOB_STORAGE_SINK = "KafkaAzureBlobStorageSink"
        KAFKA_AZURE_BLOB_STORAGE_SOURCE = "KafkaAzureBlobStorageSource"
        KAFKA_AZURE_COSMOS_DB_SINK = "KafkaAzureCosmosDBSink"
        KAFKA_AZURE_COSMOS_DB_SOURCE = "KafkaAzureCosmosDBSource"
        KAFKA_AZURE_SYNAPSE_ANALYTICS_SINK = "KafkaAzureSynapseAnalyticsSink"


    class azure.mgmt.confluent.types.ProxyResource(Resource):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.confluent.types.Resource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.confluent.types.SCClusterByokEntity(TypedDict, total=False):
        key "id": str
        key "related": str
        key "resourceName": str
        id: str
        related: str
        resource_name: str


    class azure.mgmt.confluent.types.SCClusterNetworkEnvironmentEntity(TypedDict, total=False):
        key "environment": str
        key "id": str
        key "related": str
        key "resourceName": str
        environment: str
        id: str
        related: str
        resource_name: str


    class azure.mgmt.confluent.types.SCClusterRecord(ProxyResource):
        key "id": str
        key "kind": str
        key "name": str
        key "properties": ForwardRef('ClusterProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        kind: str
        name: str
        properties: ClusterProperties
        system_data: SystemData
        type: str


    class azure.mgmt.confluent.types.SCClusterSpecEntity(TypedDict, total=False):
        key "apiEndpoint": str
        key "availability": str
        key "byok": ForwardRef('SCClusterByokEntity', module='types')
        key "cloud": str
        key "config": ForwardRef('ClusterConfigEntity', module='types')
        key "environment": ForwardRef('SCClusterNetworkEnvironmentEntity', module='types')
        key "httpEndpoint": str
        key "kafkaBootstrapEndpoint": str
        key "name": str
        key "network": ForwardRef('SCClusterNetworkEnvironmentEntity', module='types')
        key "package": Union[str, Package]
        key "region": str
        key "zone": str
        api_endpoint: str
        availability: str
        byok: SCClusterByokEntity
        cloud: str
        config: ClusterConfigEntity
        environment: SCClusterNetworkEnvironmentEntity
        http_endpoint: str
        kafka_bootstrap_endpoint: str
        name: str
        network: SCClusterNetworkEnvironmentEntity
        package: Union[str, Package]
        region: str
        zone: str


    class azure.mgmt.confluent.types.SCEnvironmentRecord(ProxyResource):
        key "id": str
        key "kind": str
        key "name": str
        key "properties": ForwardRef('EnvironmentProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        kind: str
        name: str
        properties: EnvironmentProperties
        system_data: SystemData
        type: str


    class azure.mgmt.confluent.types.SCMetadataEntity(TypedDict, total=False):
        key "createdTimestamp": str
        key "deletedTimestamp": str
        key "resourceName": str
        key "self": str
        key "updatedTimestamp": str
        created_timestamp: str
        deleted_timestamp: str
        resource_name: str
        self_property: str
        updated_timestamp: str


    class azure.mgmt.confluent.types.SaaSData(TypedDict, total=False):
        key "saaSResourceId": str
        saa_s_resource_id: str


    class azure.mgmt.confluent.types.StreamGovernanceConfig(TypedDict, total=False):
        key "package": Union[str, Package]
        package: Union[str, Package]


    class azure.mgmt.confluent.types.SystemData(TypedDict, total=False):
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


    class azure.mgmt.confluent.types.TopicMetadataEntity(TypedDict, total=False):
        key "resourceName": str
        key "self": str
        resource_name: str
        self_property: str


    class azure.mgmt.confluent.types.TopicProperties(TypedDict, total=False):
        key "configs": ForwardRef('TopicsRelatedLink', module='types')
        key "kind": str
        key "metadata": ForwardRef('TopicMetadataEntity', module='types')
        key "partitions": ForwardRef('TopicsRelatedLink', module='types')
        key "partitionsCount": str
        key "partitionsReassignments": ForwardRef('TopicsRelatedLink', module='types')
        key "replicationFactor": str
        key "topicId": str
        configs: TopicsRelatedLink
        inputConfigs: list[TopicsInputConfig]
        input_configs: list[TopicsInputConfig]
        kind: str
        metadata: TopicMetadataEntity
        partitions: TopicsRelatedLink
        partitions_count: str
        partitions_reassignments: TopicsRelatedLink
        replication_factor: str
        topic_id: str


    class azure.mgmt.confluent.types.TopicRecord(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('TopicProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: TopicProperties
        system_data: SystemData
        type: str


    class azure.mgmt.confluent.types.TopicsInputConfig(TypedDict, total=False):
        key "name": str
        key "value": str
        name: str
        value: str


    class azure.mgmt.confluent.types.TopicsRelatedLink(TypedDict, total=False):
        key "related": str
        related: str


    class azure.mgmt.confluent.types.TrackedResource(Resource):
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


    class azure.mgmt.confluent.types.UserDetail(TypedDict, total=False):
        key "aadEmail": str
        key "emailAddress": Required[str]
        key "firstName": str
        key "lastName": str
        key "userPrincipalName": str
        aad_email: str
        email_address: str
        first_name: str
        last_name: str
        user_principal_name: str


    class azure.mgmt.confluent.types.VnetInjectionDetails(TypedDict, total=False):
        key "subnetResourceId": Required[str]
        key "virtualNetworkResourceId": Required[str]
        subnet_resource_id: str
        virtual_network_resource_id: str


```