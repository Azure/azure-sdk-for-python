```py
namespace azure.mgmt.networksecurity

    class azure.mgmt.networksecurity.NetworkSecurityMgmtClient: implements ContextManager 
        agent_fabrics: AgentFabricsOperations
        cluster_associations: ClusterAssociationsOperations
        egress_trust_bundles: EgressTrustBundlesOperations
        members: MembersOperations
        neuro_shield_findings: NeuroShieldFindingsOperations
        neuro_shield_mitigations: NeuroShieldMitigationsOperations
        neuro_shield_operation_statuses: NeuroShieldOperationStatusesOperations
        neuro_shield_protected_resources: NeuroShieldProtectedResourcesOperations
        neuro_shield_summaries: NeuroShieldSummariesOperations
        neuro_shields: NeuroShieldsOperations
        operation_status: OperationStatusOperations
        operations: Operations
        policy_groups: PolicyGroupsOperations

        def __init__(
                self, 
                credential: TokenCredential, 
                subscription_id: str, 
                base_url: Optional[str] = None, 
                *, 
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


namespace azure.mgmt.networksecurity.aio

    class azure.mgmt.networksecurity.aio.NetworkSecurityMgmtClient: implements AsyncContextManager 
        agent_fabrics: AgentFabricsOperations
        cluster_associations: ClusterAssociationsOperations
        egress_trust_bundles: EgressTrustBundlesOperations
        members: MembersOperations
        neuro_shield_findings: NeuroShieldFindingsOperations
        neuro_shield_mitigations: NeuroShieldMitigationsOperations
        neuro_shield_operation_statuses: NeuroShieldOperationStatusesOperations
        neuro_shield_protected_resources: NeuroShieldProtectedResourcesOperations
        neuro_shield_summaries: NeuroShieldSummariesOperations
        neuro_shields: NeuroShieldsOperations
        operation_status: OperationStatusOperations
        operations: Operations
        policy_groups: PolicyGroupsOperations

        def __init__(
                self, 
                credential: AsyncTokenCredential, 
                subscription_id: str, 
                base_url: Optional[str] = None, 
                *, 
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


namespace azure.mgmt.networksecurity.aio.operations

    class azure.mgmt.networksecurity.aio.operations.AgentFabricsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                agent_fabric_name: str, 
                resource: AgentFabric, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AgentFabric]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                agent_fabric_name: str, 
                resource: AgentFabric, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AgentFabric]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                agent_fabric_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AgentFabric]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                agent_fabric_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                agent_fabric_name: str, 
                properties: AgentFabricTagsUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AgentFabric]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                agent_fabric_name: str, 
                properties: AgentFabricTagsUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AgentFabric]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                agent_fabric_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AgentFabric]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                agent_fabric_name: str, 
                **kwargs: Any
            ) -> AgentFabric: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[AgentFabric]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[AgentFabric]: ...


    class azure.mgmt.networksecurity.aio.operations.ClusterAssociationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                agent_fabric_name: str, 
                cluster_association_name: str, 
                resource: ClusterAssociation, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[Union[str, ClusterAssociationIfNoneMatch]] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[ClusterAssociation]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                agent_fabric_name: str, 
                cluster_association_name: str, 
                resource: ClusterAssociation, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[Union[str, ClusterAssociationIfNoneMatch]] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[ClusterAssociation]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                agent_fabric_name: str, 
                cluster_association_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[Union[str, ClusterAssociationIfNoneMatch]] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[ClusterAssociation]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                agent_fabric_name: str, 
                cluster_association_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                agent_fabric_name: str, 
                cluster_association_name: str, 
                properties: ClusterAssociationUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ClusterAssociation]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                agent_fabric_name: str, 
                cluster_association_name: str, 
                properties: ClusterAssociationUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ClusterAssociation]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                agent_fabric_name: str, 
                cluster_association_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ClusterAssociation]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                agent_fabric_name: str, 
                cluster_association_name: str, 
                **kwargs: Any
            ) -> ClusterAssociation: ...

        @distributed_trace
        def list_by_parent(
                self, 
                resource_group_name: str, 
                agent_fabric_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ClusterAssociation]: ...


    class azure.mgmt.networksecurity.aio.operations.EgressTrustBundlesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                agent_fabric_name: str, 
                **kwargs: Any
            ) -> EgressTrustBundle: ...

        @distributed_trace
        def list_by_parent(
                self, 
                resource_group_name: str, 
                agent_fabric_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[EgressTrustBundle]: ...


    class azure.mgmt.networksecurity.aio.operations.MembersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                agent_fabric_name: str, 
                member_name: str, 
                resource: Member, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Member]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                agent_fabric_name: str, 
                member_name: str, 
                resource: Member, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Member]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                agent_fabric_name: str, 
                member_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Member]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                agent_fabric_name: str, 
                member_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                agent_fabric_name: str, 
                member_name: str, 
                properties: MemberTagsUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Member]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                agent_fabric_name: str, 
                member_name: str, 
                properties: MemberTagsUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Member]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                agent_fabric_name: str, 
                member_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Member]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                agent_fabric_name: str, 
                member_name: str, 
                **kwargs: Any
            ) -> Member: ...

        @distributed_trace
        def list_by_parent(
                self, 
                resource_group_name: str, 
                agent_fabric_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Member]: ...


    class azure.mgmt.networksecurity.aio.operations.NeuroShieldFindingsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                neuro_shield_name: str, 
                protected_resource_name: str, 
                finding_id: str, 
                **kwargs: Any
            ) -> NeuroShieldFinding: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                neuro_shield_name: str, 
                protected_resource_name: str, 
                *, 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[NeuroShieldFinding]: ...

        @distributed_trace
        def list_by_neuro_shield(
                self, 
                resource_group_name: str, 
                neuro_shield_name: str, 
                *, 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[NeuroShieldFinding]: ...

        @distributed_trace_async
        async def mitigate(
                self, 
                resource_group_name: str, 
                neuro_shield_name: str, 
                protected_resource_name: str, 
                finding_id: str, 
                **kwargs: Any
            ) -> NeuroShieldMitigationActionResult: ...

        @distributed_trace_async
        async def rollback(
                self, 
                resource_group_name: str, 
                neuro_shield_name: str, 
                protected_resource_name: str, 
                finding_id: str, 
                **kwargs: Any
            ) -> NeuroShieldMitigationActionResult: ...


    class azure.mgmt.networksecurity.aio.operations.NeuroShieldMitigationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def execute(
                self, 
                resource_group_name: str, 
                neuro_shield_name: str, 
                protected_resource_name: str, 
                mitigation_id: str, 
                **kwargs: Any
            ) -> NeuroShieldMitigation: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                neuro_shield_name: str, 
                protected_resource_name: str, 
                mitigation_id: str, 
                **kwargs: Any
            ) -> NeuroShieldMitigation: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                neuro_shield_name: str, 
                protected_resource_name: str, 
                *, 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[NeuroShieldMitigation]: ...

        @distributed_trace
        def list_by_neuro_shield(
                self, 
                resource_group_name: str, 
                neuro_shield_name: str, 
                *, 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[NeuroShieldMitigation]: ...

        @distributed_trace_async
        async def rollback(
                self, 
                resource_group_name: str, 
                neuro_shield_name: str, 
                protected_resource_name: str, 
                mitigation_id: str, 
                **kwargs: Any
            ) -> NeuroShieldMitigation: ...


    class azure.mgmt.networksecurity.aio.operations.NeuroShieldOperationStatusesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                location: str, 
                operation_id: str, 
                **kwargs: Any
            ) -> OperationStatusResult: ...


    class azure.mgmt.networksecurity.aio.operations.NeuroShieldProtectedResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                neuro_shield_name: str, 
                protected_resource_name: str, 
                resource: NeuroShieldProtectedResource, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[NeuroShieldProtectedResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                neuro_shield_name: str, 
                protected_resource_name: str, 
                resource: NeuroShieldProtectedResource, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[NeuroShieldProtectedResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                neuro_shield_name: str, 
                protected_resource_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[NeuroShieldProtectedResource]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                neuro_shield_name: str, 
                protected_resource_name: str, 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                neuro_shield_name: str, 
                protected_resource_name: str, 
                **kwargs: Any
            ) -> NeuroShieldProtectedResource: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                neuro_shield_name: str, 
                *, 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[NeuroShieldProtectedResource]: ...

        @distributed_trace_async
        async def trigger_inventory_upload(
                self, 
                resource_group_name: str, 
                neuro_shield_name: str, 
                protected_resource_name: str, 
                **kwargs: Any
            ) -> NeuroShieldInventoryUploadRequestResult: ...


    class azure.mgmt.networksecurity.aio.operations.NeuroShieldSummariesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                neuro_shield_name: str, 
                **kwargs: Any
            ) -> NeuroShieldSummary: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                neuro_shield_name: str, 
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[NeuroShieldSummary]: ...


    class azure.mgmt.networksecurity.aio.operations.NeuroShieldsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                neuro_shield_name: str, 
                resource: NeuroShieldResource, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> NeuroShieldResource: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                neuro_shield_name: str, 
                resource: NeuroShieldResource, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> NeuroShieldResource: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                neuro_shield_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> NeuroShieldResource: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                neuro_shield_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                neuro_shield_name: str, 
                **kwargs: Any
            ) -> NeuroShieldResource: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[NeuroShieldResource]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[NeuroShieldResource]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                neuro_shield_name: str, 
                properties: NeuroShieldPatch, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> NeuroShieldResource: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                neuro_shield_name: str, 
                properties: NeuroShieldPatch, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> NeuroShieldResource: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                neuro_shield_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> NeuroShieldResource: ...


    class azure.mgmt.networksecurity.aio.operations.OperationStatusOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                location: str, 
                operation_id: str, 
                **kwargs: Any
            ) -> OperationStatusResult: ...


    class azure.mgmt.networksecurity.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        @api_version_validation(params_added_on={'v3': ['api_version']})
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


    class azure.mgmt.networksecurity.aio.operations.PolicyGroupsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                policy_group_name: str, 
                resource: PolicyGroup, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PolicyGroup]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                policy_group_name: str, 
                resource: PolicyGroup, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PolicyGroup]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                policy_group_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PolicyGroup]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                policy_group_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                policy_group_name: str, 
                properties: PolicyGroupTagsUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PolicyGroup]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                policy_group_name: str, 
                properties: PolicyGroupTagsUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PolicyGroup]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                policy_group_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PolicyGroup]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                policy_group_name: str, 
                **kwargs: Any
            ) -> PolicyGroup: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[PolicyGroup]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[PolicyGroup]: ...


namespace azure.mgmt.networksecurity.models

    class azure.mgmt.networksecurity.models.AciWorkload(WorkloadBase, discriminator='ACI'):
        agent_identity: Optional[AgentIdentity]
        member_guid: str
        resource_id: str
        type: Literal[WorkloadType.ACI]
        workload_id: str

        @overload
        def __init__(
                self, 
                *, 
                agent_identity: Optional[AgentIdentity] = ..., 
                member_guid: Optional[str] = ..., 
                resource_id: str, 
                workload_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networksecurity.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.networksecurity.models.AgentFabric(TrackedResource):
        id: str
        identity: Optional[SystemAssignedServiceIdentity]
        location: str
        name: str
        properties: Optional[AgentFabricProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[SystemAssignedServiceIdentity] = ..., 
                location: str, 
                properties: Optional[AgentFabricProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networksecurity.models.AgentFabricProperties(_Model):
        content_inspection_profile: Optional[ContentInspectionProfile]
        default_policy_groups: Optional[list[str]]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        resource_guid: Optional[str]
        trust_domain: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                content_inspection_profile: Optional[ContentInspectionProfile] = ..., 
                default_policy_groups: Optional[list[str]] = ..., 
                trust_domain: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networksecurity.models.AgentFabricSandboxEndpoint(_Model):
        name: str
        protocol: str
        service_port: int
        target_port: int

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                protocol: str, 
                service_port: int, 
                target_port: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networksecurity.models.AgentFabricSandboxImage(_Model):
        digest: Optional[str]
        pull_policy: Optional[Union[str, ImagePullPolicy]]
        uri: str

        @overload
        def __init__(
                self, 
                *, 
                digest: Optional[str] = ..., 
                pull_policy: Optional[Union[str, ImagePullPolicy]] = ..., 
                uri: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networksecurity.models.AgentFabricSandboxResources(_Model):
        cpu: str
        disk: Optional[str]
        memory: str

        @overload
        def __init__(
                self, 
                *, 
                cpu: str, 
                disk: Optional[str] = ..., 
                memory: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networksecurity.models.AgentFabricSandboxWorkload(WorkloadBase, discriminator='AgentFabricSandbox'):
        agent_identity: Optional[AgentIdentity]
        domain: str
        endpoints: Optional[list[AgentFabricSandboxEndpoint]]
        image: AgentFabricSandboxImage
        member_guid: str
        resources: AgentFabricSandboxResources
        type: Literal[WorkloadType.AGENT_FABRIC_SANDBOX]
        workload_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                agent_identity: Optional[AgentIdentity] = ..., 
                domain: str, 
                endpoints: Optional[list[AgentFabricSandboxEndpoint]] = ..., 
                image: AgentFabricSandboxImage, 
                member_guid: Optional[str] = ..., 
                resources: AgentFabricSandboxResources
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networksecurity.models.AgentFabricTagsUpdate(_Model):
        identity: Optional[SystemAssignedServiceIdentity]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[SystemAssignedServiceIdentity] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networksecurity.models.AgentIdentity(_Model):
        agent_id: str
        blueprint_id: Optional[str]
        tenant_id: str

        @overload
        def __init__(
                self, 
                *, 
                agent_id: str, 
                blueprint_id: Optional[str] = ..., 
                tenant_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networksecurity.models.AksWorkload(WorkloadBase, discriminator='AKS'):
        cluster_association_id: str
        cluster_resource_id: str
        endpoints: Optional[list[AksWorkloadPortMapping]]
        member_guid: str
        type: Literal[WorkloadType.AKS]
        workload: AksWorkloadReference
        workload_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                cluster_association_id: str, 
                cluster_resource_id: str, 
                endpoints: Optional[list[AksWorkloadPortMapping]] = ..., 
                member_guid: Optional[str] = ..., 
                workload: AksWorkloadReference
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networksecurity.models.AksWorkloadPortMapping(_Model):
        name: str
        protocol: str
        service_port: int
        target_port: int

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                protocol: str, 
                service_port: int, 
                target_port: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networksecurity.models.AksWorkloadReference(_Model):
        api_version: str
        kind: str
        name: str
        namespace: str

        @overload
        def __init__(
                self, 
                *, 
                api_version: str, 
                kind: str, 
                name: str, 
                namespace: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networksecurity.models.AzureManagedCaCertificate(TlsInspectionCertificateBase, discriminator='AzureManagedCA'):
        mode: Literal[TlsInspectionCertificateMode.AZURE_MANAGED_CA]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networksecurity.models.ClusterAssociation(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[ClusterAssociationProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[ClusterAssociationProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networksecurity.models.ClusterAssociationIfNoneMatch(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        WILDCARD = "*"


    class azure.mgmt.networksecurity.models.ClusterAssociationProperties(_Model):
        cluster_resource_id: str
        provisioning_state: Optional[Union[str, ProvisioningState]]
        sku: Optional[Union[str, ClusterAssociationSkuName]]
        status: Optional[ClusterAssociationStatus]
        workload_cluster_gateway_ip: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                cluster_resource_id: str, 
                sku: Optional[Union[str, ClusterAssociationSkuName]] = ..., 
                workload_cluster_gateway_ip: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networksecurity.models.ClusterAssociationSkuName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PREMIUM = "Premium"
        STANDARD = "Standard"


    class azure.mgmt.networksecurity.models.ClusterAssociationStatus(_Model):
        code: Optional[str]
        message: Optional[str]


    class azure.mgmt.networksecurity.models.ClusterAssociationUpdate(_Model):
        properties: ClusterAssociationUpdateProperties
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                properties: ClusterAssociationUpdateProperties, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networksecurity.models.ClusterAssociationUpdateProperties(_Model):
        cluster_resource_id: Optional[str]
        sku: Optional[Union[str, ClusterAssociationSkuName]]
        workload_cluster_gateway_ip: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                cluster_resource_id: Optional[str] = ..., 
                sku: Optional[Union[str, ClusterAssociationSkuName]] = ..., 
                workload_cluster_gateway_ip: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networksecurity.models.ContentInspectionPolicy(NetworkSecurityPolicyBase, discriminator='ContentInspection'):
        prompt_injection_protection: Optional[PromptInjectionProtection]
        source: ContentInspectionPolicySource
        type: Literal[NetworkSecurityPolicyType.CONTENT_INSPECTION]

        @overload
        def __init__(
                self, 
                *, 
                prompt_injection_protection: Optional[PromptInjectionProtection] = ..., 
                source: ContentInspectionPolicySource
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networksecurity.models.ContentInspectionPolicyAddressPrefixesSource(ContentInspectionPolicySource, discriminator='AddressPrefixes'):
        prefixes: list[str]
        type: Literal[ContentInspectionPolicySourceType.ADDRESS_PREFIXES]

        @overload
        def __init__(
                self, 
                *, 
                prefixes: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networksecurity.models.ContentInspectionPolicySource(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networksecurity.models.ContentInspectionPolicySourceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ADDRESS_PREFIXES = "AddressPrefixes"
        WORKLOAD_ID_PATTERNS = "WorkloadIdPatterns"


    class azure.mgmt.networksecurity.models.ContentInspectionPolicyWorkloadIdPatternsSource(ContentInspectionPolicySource, discriminator='WorkloadIdPatterns'):
        patterns: list[str]
        type: Literal[ContentInspectionPolicySourceType.WORKLOAD_ID_PATTERNS]

        @overload
        def __init__(
                self, 
                *, 
                patterns: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networksecurity.models.ContentInspectionProfile(_Model):
        api_key: Optional[str]
        endpoint: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                api_key: Optional[str] = ..., 
                endpoint: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networksecurity.models.ContentInspectionSensitivity(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HIGH = "High"
        LOW = "Low"
        MEDIUM = "Medium"


    class azure.mgmt.networksecurity.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.networksecurity.models.EgressTrustBundle(ProxyResource):
        id: str
        name: str
        properties: Optional[EgressTrustBundleProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[EgressTrustBundleProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networksecurity.models.EgressTrustBundleCertificate(_Model):
        certificate_id: str
        not_after: datetime
        not_before: datetime
        pem: str
        thumbprint_sha256: str


    class azure.mgmt.networksecurity.models.EgressTrustBundleProperties(_Model):
        bundle_version: str
        cache_expires_at: datetime
        cache_validity_seconds: int
        certificates: list[EgressTrustBundleCertificate]
        provisioning_state: Optional[Union[str, ProvisioningState]]


    class azure.mgmt.networksecurity.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.networksecurity.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.networksecurity.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networksecurity.models.FqdnFilteringAddressPrefixesSource(FqdnFilteringSource, discriminator='AddressPrefixes'):
        prefixes: list[str]
        type: Literal[FqdnFilteringSourceType.ADDRESS_PREFIXES]

        @overload
        def __init__(
                self, 
                *, 
                prefixes: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networksecurity.models.FqdnFilteringDestination(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networksecurity.models.FqdnFilteringDestinationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FQDNS = "Fqdns"


    class azure.mgmt.networksecurity.models.FqdnFilteringFqdnsDestination(FqdnFilteringDestination, discriminator='Fqdns'):
        fqdns: list[str]
        type: Literal[FqdnFilteringDestinationType.FQDNS]

        @overload
        def __init__(
                self, 
                *, 
                fqdns: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networksecurity.models.FqdnFilteringPolicy(NetworkSecurityPolicyBase, discriminator='FqdnFiltering'):
        destination: Optional[FqdnFilteringDestination]
        direction: Optional[Union[str, PolicyDirection]]
        name: Optional[str]
        ports: Optional[list[int]]
        priority: Optional[int]
        source: FqdnFilteringSource
        type: Literal[NetworkSecurityPolicyType.FQDN_FILTERING]

        @overload
        def __init__(
                self, 
                *, 
                destination: Optional[FqdnFilteringDestination] = ..., 
                direction: Optional[Union[str, PolicyDirection]] = ..., 
                name: Optional[str] = ..., 
                ports: Optional[list[int]] = ..., 
                priority: Optional[int] = ..., 
                source: FqdnFilteringSource
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networksecurity.models.FqdnFilteringSource(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networksecurity.models.FqdnFilteringSourceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ADDRESS_PREFIXES = "AddressPrefixes"
        WORKLOAD_ID_PATTERNS = "WorkloadIdPatterns"


    class azure.mgmt.networksecurity.models.FqdnFilteringWorkloadIdPatternsSource(FqdnFilteringSource, discriminator='WorkloadIdPatterns'):
        patterns: list[str]
        type: Literal[FqdnFilteringSourceType.WORKLOAD_ID_PATTERNS]

        @overload
        def __init__(
                self, 
                *, 
                patterns: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networksecurity.models.HttpMethod(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DELETE = "DELETE"
        GET = "GET"
        HEAD = "HEAD"
        OPTIONS = "OPTIONS"
        PATCH = "PATCH"
        POST = "POST"
        PUT = "PUT"


    class azure.mgmt.networksecurity.models.ImagePullPolicy(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALWAYS = "Always"
        IF_NOT_PRESENT = "IfNotPresent"


    class azure.mgmt.networksecurity.models.ManagedServiceIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        SYSTEM_ASSIGNED_USER_ASSIGNED = "SystemAssigned,UserAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.networksecurity.models.McpArgumentMatching(_Model):
        match_case: Optional[Union[str, McpMatchCase]]
        match_type: Union[str, McpMatchType]
        path: Optional[str]
        values_property: list[str]

        @overload
        def __init__(
                self, 
                *, 
                match_case: Optional[Union[str, McpMatchCase]] = ..., 
                match_type: Union[str, McpMatchType], 
                path: Optional[str] = ..., 
                values_property: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networksecurity.models.McpMatchCase(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CASE_INSENSITIVE = "CaseInsensitive"
        CASE_SENSITIVE = "CaseSensitive"


    class azure.mgmt.networksecurity.models.McpMatchType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONTAINS = "Contains"
        EXACT_MATCH = "ExactMatch"
        NOT_CONTAINS = "NotContains"
        NOT_EXACT_MATCH = "NotExactMatch"


    class azure.mgmt.networksecurity.models.McpPolicy(NetworkSecurityPolicyBase, discriminator='Mcp'):
        default_action: Union[str, PolicyAction]
        destination: McpPolicyDestination
        rules: list[McpRule]
        source: McpPolicySource
        type: Literal[NetworkSecurityPolicyType.MCP]

        @overload
        def __init__(
                self, 
                *, 
                default_action: Union[str, PolicyAction], 
                destination: McpPolicyDestination, 
                rules: list[McpRule], 
                source: McpPolicySource
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networksecurity.models.McpPolicyAddressPrefixesDestination(McpPolicyDestination, discriminator='AddressPrefixes'):
        prefixes: list[str]
        type: Literal[McpPolicyDestinationType.ADDRESS_PREFIXES]

        @overload
        def __init__(
                self, 
                *, 
                prefixes: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networksecurity.models.McpPolicyAddressPrefixesSource(McpPolicySource, discriminator='AddressPrefixes'):
        prefixes: list[str]
        type: Literal[McpPolicySourceType.ADDRESS_PREFIXES]

        @overload
        def __init__(
                self, 
                *, 
                prefixes: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networksecurity.models.McpPolicyDestination(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networksecurity.models.McpPolicyDestinationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ADDRESS_PREFIXES = "AddressPrefixes"
        FQDNS = "Fqdns"
        WORKLOAD_ID_PATTERNS = "WorkloadIdPatterns"


    class azure.mgmt.networksecurity.models.McpPolicyFqdnsDestination(McpPolicyDestination, discriminator='Fqdns'):
        fqdns: list[str]
        type: Literal[McpPolicyDestinationType.FQDNS]

        @overload
        def __init__(
                self, 
                *, 
                fqdns: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networksecurity.models.McpPolicySource(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networksecurity.models.McpPolicySourceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ADDRESS_PREFIXES = "AddressPrefixes"
        WORKLOAD_ID_PATTERNS = "WorkloadIdPatterns"


    class azure.mgmt.networksecurity.models.McpPolicyWorkloadIdPatternsDestination(McpPolicyDestination, discriminator='WorkloadIdPatterns'):
        patterns: list[str]
        type: Literal[McpPolicyDestinationType.WORKLOAD_ID_PATTERNS]

        @overload
        def __init__(
                self, 
                *, 
                patterns: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networksecurity.models.McpPolicyWorkloadIdPatternsSource(McpPolicySource, discriminator='WorkloadIdPatterns'):
        patterns: list[str]
        type: Literal[McpPolicySourceType.WORKLOAD_ID_PATTERNS]

        @overload
        def __init__(
                self, 
                *, 
                patterns: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networksecurity.models.McpPromptMatching(_Model):
        arguments: Optional[McpArgumentMatching]
        descriptions: Optional[McpStringMatching]
        methods: Optional[list[Union[str, McpPromptMethod]]]
        names: Optional[McpStringMatching]
        response_contents: Optional[McpStringMatching]
        titles: Optional[McpStringMatching]

        @overload
        def __init__(
                self, 
                *, 
                arguments: Optional[McpArgumentMatching] = ..., 
                descriptions: Optional[McpStringMatching] = ..., 
                methods: Optional[list[Union[str, McpPromptMethod]]] = ..., 
                names: Optional[McpStringMatching] = ..., 
                response_contents: Optional[McpStringMatching] = ..., 
                titles: Optional[McpStringMatching] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networksecurity.models.McpPromptMethod(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        GET = "Get"
        LIST = "List"


    class azure.mgmt.networksecurity.models.McpRule(_Model):
        action: Optional[Union[str, PolicyAction]]
        matching_conditions: Optional[McpRuleMatchingConditions]
        name: Optional[str]
        priority: Optional[int]
        tools: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                action: Optional[Union[str, PolicyAction]] = ..., 
                matching_conditions: Optional[McpRuleMatchingConditions] = ..., 
                name: Optional[str] = ..., 
                priority: Optional[int] = ..., 
                tools: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networksecurity.models.McpRuleDestinationMatching(_Model):
        prompt_matching: Optional[McpPromptMatching]
        protocol_versions: Optional[McpStringMatching]
        server_fqdns: Optional[list[str]]
        tool_matching: Optional[McpToolMatching]

        @overload
        def __init__(
                self, 
                *, 
                prompt_matching: Optional[McpPromptMatching] = ..., 
                protocol_versions: Optional[McpStringMatching] = ..., 
                server_fqdns: Optional[list[str]] = ..., 
                tool_matching: Optional[McpToolMatching] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networksecurity.models.McpRuleMatchingConditions(_Model):
        destinations: McpRuleDestinationMatching

        @overload
        def __init__(
                self, 
                *, 
                destinations: McpRuleDestinationMatching
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networksecurity.models.McpStringMatching(_Model):
        match_case: Optional[Union[str, McpMatchCase]]
        match_type: Union[str, McpMatchType]
        values_property: list[str]

        @overload
        def __init__(
                self, 
                *, 
                match_case: Optional[Union[str, McpMatchCase]] = ..., 
                match_type: Union[str, McpMatchType], 
                values_property: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networksecurity.models.McpToolMatching(_Model):
        call_arguments: Optional[McpArgumentMatching]
        descriptions: Optional[McpStringMatching]
        methods: Optional[list[Union[str, McpToolMethod]]]
        names: Optional[McpStringMatching]
        response_contents: Optional[McpStringMatching]
        titles: Optional[McpStringMatching]

        @overload
        def __init__(
                self, 
                *, 
                call_arguments: Optional[McpArgumentMatching] = ..., 
                descriptions: Optional[McpStringMatching] = ..., 
                methods: Optional[list[Union[str, McpToolMethod]]] = ..., 
                names: Optional[McpStringMatching] = ..., 
                response_contents: Optional[McpStringMatching] = ..., 
                titles: Optional[McpStringMatching] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networksecurity.models.McpToolMethod(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CALL = "Call"
        LIST = "List"


    class azure.mgmt.networksecurity.models.Member(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[MemberProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[MemberProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networksecurity.models.MemberProperties(_Model):
        fqdn: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        spiffe_id: Optional[str]
        workload: Optional[WorkloadBase]

        @overload
        def __init__(
                self, 
                *, 
                fqdn: Optional[str] = ..., 
                workload: Optional[WorkloadBase] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networksecurity.models.MemberTagsUpdate(_Model):
        properties: Optional[MemberUpdateProperties]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[MemberUpdateProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networksecurity.models.MemberUpdateProperties(_Model):
        fqdn: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                fqdn: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networksecurity.models.NetworkSecurityPolicyBase(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networksecurity.models.NetworkSecurityPolicyType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONTENT_INSPECTION = "ContentInspection"
        FQDN_FILTERING = "FqdnFiltering"
        MCP = "Mcp"
        TLS_INSPECTION = "TlsInspection"
        URL_FILTERING = "UrlFiltering"


    class azure.mgmt.networksecurity.models.NeuroShieldAgentHealth(_Model):
        last_seen_time: Optional[datetime]


    class azure.mgmt.networksecurity.models.NeuroShieldFinding(ProxyResource):
        id: str
        name: str
        properties: NeuroShieldFindingProperties
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: NeuroShieldFindingProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networksecurity.models.NeuroShieldFindingProperties(_Model):
        cve_id: str
        description: str
        detected_time: Optional[datetime]
        provisioning_state: Optional[Union[str, ResourceProvisioningState]]
        reason: str
        severity: Union[str, NeuroShieldSeverityThreshold]
        status: Union[str, NeuroShieldFindingStatus]
        virtual_machine_arm_id: str


    class azure.mgmt.networksecurity.models.NeuroShieldFindingStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        AWAITING_APPROVAL = "AwaitingApproval"
        MITIGATED = "Mitigated"
        MITIGATIONS_EXHAUSTED = "MitigationsExhausted"
        MITIGATION_IN_PROGRESS = "MitigationInProgress"
        SKIPPED = "Skipped"
        UNREACHABLE = "Unreachable"


    class azure.mgmt.networksecurity.models.NeuroShieldInventoryUploadRequestMetadata(_Model):
        expires_at: datetime
        request_id: str
        requested_at: datetime


    class azure.mgmt.networksecurity.models.NeuroShieldInventoryUploadRequestResult(_Model):
        deduplicated: bool
        expires_at: datetime
        request_id: str
        requested_at: datetime

        @overload
        def __init__(
                self, 
                *, 
                deduplicated: bool, 
                expires_at: datetime, 
                request_id: str, 
                requested_at: datetime
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networksecurity.models.NeuroShieldMitigation(ProxyResource):
        id: str
        name: str
        properties: NeuroShieldMitigationProperties
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: NeuroShieldMitigationProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networksecurity.models.NeuroShieldMitigationActionResult(_Model):
        value: list[NeuroShieldMitigation]

        @overload
        def __init__(
                self, 
                *, 
                value: list[NeuroShieldMitigation]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networksecurity.models.NeuroShieldMitigationProperties(_Model):
        applied_time: Optional[datetime]
        commands_summary: str
        cve_id: str
        finding_id: str
        is_rollbackable: bool
        provisioning_state: Optional[Union[str, ResourceProvisioningState]]
        rank: int
        status: Union[str, NeuroShieldMitigationStatus]
        status_details: Optional[str]
        virtual_machine_arm_id: str


    class azure.mgmt.networksecurity.models.NeuroShieldMitigationStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AWAITING_APPROVAL = "AwaitingApproval"
        FAILED = "Failed"
        IN_PROGRESS = "InProgress"
        QUEUED = "Queued"
        ROLLBACK_FAILED = "RollbackFailed"
        ROLLBACK_IN_PROGRESS = "RollbackInProgress"
        ROLLED_BACK = "RolledBack"
        SKIPPED = "Skipped"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.networksecurity.models.NeuroShieldPatch(_Model):
        properties: Optional[NeuroShieldPatchProperties]
        tags: Optional[Any]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[NeuroShieldPatchProperties] = ..., 
                tags: Optional[Any] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networksecurity.models.NeuroShieldPatchProperties(_Model):
        description: Optional[str]
        response_mode: Optional[Union[str, NeuroShieldResponseMode]]
        severity_threshold: Optional[Union[str, NeuroShieldSeverityThreshold]]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                response_mode: Optional[Union[str, NeuroShieldResponseMode]] = ..., 
                severity_threshold: Optional[Union[str, NeuroShieldSeverityThreshold]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networksecurity.models.NeuroShieldProperties(_Model):
        description: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningStateNeuroShield]]
        resource_guid: Optional[str]
        response_mode: Union[str, NeuroShieldResponseMode]
        severity_threshold: Optional[Union[str, NeuroShieldSeverityThreshold]]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                response_mode: Union[str, NeuroShieldResponseMode], 
                severity_threshold: Optional[Union[str, NeuroShieldSeverityThreshold]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networksecurity.models.NeuroShieldProtectedResource(ProxyResource):
        id: str
        name: str
        properties: NeuroShieldProtectedResourceProperties
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: NeuroShieldProtectedResourceProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networksecurity.models.NeuroShieldProtectedResourceIdentity(_Model):
        principal_id: Optional[str]
        tenant_id: Optional[str]
        type: Union[str, ManagedServiceIdentityType]
        user_assigned_identities: Optional[Any]

        @overload
        def __init__(
                self, 
                *, 
                principal_id: Optional[str] = ..., 
                tenant_id: Optional[str] = ..., 
                type: Union[str, ManagedServiceIdentityType], 
                user_assigned_identities: Optional[Any] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networksecurity.models.NeuroShieldProtectedResourceProperties(_Model):
        agent_health: Optional[NeuroShieldAgentHealth]
        inventory_upload_request: Optional[NeuroShieldInventoryUploadRequestMetadata]
        provisioning_state: Optional[Union[str, ProvisioningStateNeuroShield]]
        target_identity: Optional[NeuroShieldProtectedResourceIdentity]
        target_resource_id: str

        @overload
        def __init__(
                self, 
                *, 
                target_identity: Optional[NeuroShieldProtectedResourceIdentity] = ..., 
                target_resource_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networksecurity.models.NeuroShieldProtectedResourceUserAssignedIdentity(_Model):
        client_id: Optional[str]
        principal_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                client_id: Optional[str] = ..., 
                principal_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networksecurity.models.NeuroShieldResource(TrackedResource):
        e_tag: Optional[str]
        id: str
        location: str
        name: str
        properties: NeuroShieldProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: NeuroShieldProperties, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networksecurity.models.NeuroShieldResponseMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTO = "Auto"
        MANUAL = "Manual"


    class azure.mgmt.networksecurity.models.NeuroShieldSeverityThreshold(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CRITICAL = "Critical"
        HIGH = "High"
        LOW = "Low"
        MEDIUM = "Medium"


    class azure.mgmt.networksecurity.models.NeuroShieldSummary(ProxyResource):
        id: str
        name: str
        properties: NeuroShieldSummaryProperties
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: NeuroShieldSummaryProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networksecurity.models.NeuroShieldSummaryProperties(_Model):
        active_findings: int
        awaiting_approval_mitigations: int
        critical_findings: int
        failed_mitigations: int
        high_findings: int
        in_progress_mitigations: int
        low_findings: int
        medium_findings: int
        protected_count: int
        provisioning_state: Optional[Union[str, ResourceProvisioningState]]
        queued_mitigations: int
        rollback_in_progress_mitigations: int
        scanned_protected_count: int
        succeeded_mitigations: int
        unreachable_findings: int

        @overload
        def __init__(
                self, 
                *, 
                active_findings: int, 
                awaiting_approval_mitigations: int, 
                critical_findings: int, 
                failed_mitigations: int, 
                high_findings: int, 
                in_progress_mitigations: int, 
                low_findings: int, 
                medium_findings: int, 
                protected_count: int, 
                queued_mitigations: int, 
                rollback_in_progress_mitigations: int, 
                scanned_protected_count: int, 
                succeeded_mitigations: int, 
                unreachable_findings: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networksecurity.models.Operation(_Model):
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


    class azure.mgmt.networksecurity.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.networksecurity.models.OperationStatusResult(_Model):
        end_time: Optional[datetime]
        error: Optional[ErrorDetail]
        id: Optional[str]
        name: Optional[str]
        operations: Optional[list[OperationStatusResult]]
        percent_complete: Optional[float]
        resource_id: Optional[str]
        start_time: Optional[datetime]
        status: str

        @overload
        def __init__(
                self, 
                *, 
                end_time: Optional[datetime] = ..., 
                error: Optional[ErrorDetail] = ..., 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                operations: Optional[list[OperationStatusResult]] = ..., 
                percent_complete: Optional[float] = ..., 
                start_time: Optional[datetime] = ..., 
                status: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networksecurity.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.networksecurity.models.PolicyAction(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALLOW = "Allow"
        DENY = "Deny"


    class azure.mgmt.networksecurity.models.PolicyDirection(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BOTH = "Both"
        INBOUND = "Inbound"
        OUTBOUND = "Outbound"


    class azure.mgmt.networksecurity.models.PolicyGroup(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[PolicyGroupProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[PolicyGroupProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networksecurity.models.PolicyGroupProperties(_Model):
        description: Optional[str]
        display_name: Optional[str]
        network_security_policies: Optional[list[NetworkSecurityPolicyBase]]
        priority: Optional[int]
        provisioning_state: Optional[Union[str, ProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                network_security_policies: Optional[list[NetworkSecurityPolicyBase]] = ..., 
                priority: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networksecurity.models.PolicyGroupTagsUpdate(_Model):
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networksecurity.models.PromptInjectionOnDetection(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALERT = "Alert"
        BLOCK_AND_ALERT = "BlockAndAlert"
        SANITIZE = "Sanitize"


    class azure.mgmt.networksecurity.models.PromptInjectionProtection(_Model):
        on_detection: Union[str, PromptInjectionOnDetection]
        prompt_locations: Optional[list[str]]
        response_locations: Optional[list[str]]
        sensitivity: Optional[Union[str, ContentInspectionSensitivity]]

        @overload
        def __init__(
                self, 
                *, 
                on_detection: Union[str, PromptInjectionOnDetection], 
                prompt_locations: Optional[list[str]] = ..., 
                response_locations: Optional[list[str]] = ..., 
                sensitivity: Optional[Union[str, ContentInspectionSensitivity]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networksecurity.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        PROVISIONING = "Provisioning"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.networksecurity.models.ProvisioningStateNeuroShield(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.networksecurity.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.networksecurity.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.networksecurity.models.ResourceProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.networksecurity.models.SystemAssignedServiceIdentity(_Model):
        principal_id: Optional[str]
        tenant_id: Optional[str]
        type: Union[str, SystemAssignedServiceIdentityType]

        @overload
        def __init__(
                self, 
                *, 
                type: Union[str, SystemAssignedServiceIdentityType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networksecurity.models.SystemAssignedServiceIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"


    class azure.mgmt.networksecurity.models.SystemData(_Model):
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


    class azure.mgmt.networksecurity.models.TlsInspectionAction(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BYPASS = "Bypass"
        INSPECT = "Inspect"


    class azure.mgmt.networksecurity.models.TlsInspectionCertificateBase(_Model):
        mode: str

        @overload
        def __init__(
                self, 
                *, 
                mode: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networksecurity.models.TlsInspectionCertificateMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_MANAGED_CA = "AzureManagedCA"


    class azure.mgmt.networksecurity.models.TlsInspectionPolicy(NetworkSecurityPolicyBase, discriminator='TlsInspection'):
        certificate: TlsInspectionCertificateBase
        default_action: Optional[Union[str, TlsInspectionAction]]
        rules: Optional[list[TlsInspectionRule]]
        source: TlsInspectionPolicySource
        type: Literal[NetworkSecurityPolicyType.TLS_INSPECTION]

        @overload
        def __init__(
                self, 
                *, 
                certificate: TlsInspectionCertificateBase, 
                default_action: Optional[Union[str, TlsInspectionAction]] = ..., 
                rules: Optional[list[TlsInspectionRule]] = ..., 
                source: TlsInspectionPolicySource
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networksecurity.models.TlsInspectionPolicySource(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networksecurity.models.TlsInspectionPolicySourceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        WORKLOAD_ID_PATTERNS = "WorkloadIdPatterns"


    class azure.mgmt.networksecurity.models.TlsInspectionPolicyWorkloadIdPatternsSource(TlsInspectionPolicySource, discriminator='WorkloadIdPatterns'):
        patterns: list[str]
        type: Literal[TlsInspectionPolicySourceType.WORKLOAD_ID_PATTERNS]

        @overload
        def __init__(
                self, 
                *, 
                patterns: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networksecurity.models.TlsInspectionRule(_Model):
        action: Optional[Union[str, TlsInspectionAction]]
        destinations: list[TlsInspectionRuleDestination]
        name: str
        priority: int

        @overload
        def __init__(
                self, 
                *, 
                action: Optional[Union[str, TlsInspectionAction]] = ..., 
                destinations: list[TlsInspectionRuleDestination], 
                name: str, 
                priority: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networksecurity.models.TlsInspectionRuleDestination(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networksecurity.models.TlsInspectionRuleDestinationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FQDNS = "Fqdns"


    class azure.mgmt.networksecurity.models.TlsInspectionRuleFqdnsDestination(TlsInspectionRuleDestination, discriminator='Fqdns'):
        fqdns: list[str]
        type: Literal[TlsInspectionRuleDestinationType.FQDNS]

        @overload
        def __init__(
                self, 
                *, 
                fqdns: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networksecurity.models.TrackedResource(Resource):
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


    class azure.mgmt.networksecurity.models.UrlFilteringAddressPrefixesDestination(UrlFilteringDestination, discriminator='AddressPrefixes'):
        prefixes: list[str]
        type: Literal[UrlFilteringDestinationType.ADDRESS_PREFIXES]

        @overload
        def __init__(
                self, 
                *, 
                prefixes: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networksecurity.models.UrlFilteringAddressPrefixesSource(UrlFilteringSource, discriminator='AddressPrefixes'):
        prefixes: list[str]
        type: Literal[UrlFilteringSourceType.ADDRESS_PREFIXES]

        @overload
        def __init__(
                self, 
                *, 
                prefixes: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networksecurity.models.UrlFilteringDestination(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networksecurity.models.UrlFilteringDestinationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ADDRESS_PREFIXES = "AddressPrefixes"
        FQDNS = "Fqdns"
        WORKLOAD_ID_PATTERNS = "WorkloadIdPatterns"


    class azure.mgmt.networksecurity.models.UrlFilteringFqdnsDestination(UrlFilteringDestination, discriminator='Fqdns'):
        fqdns: list[str]
        type: Literal[UrlFilteringDestinationType.FQDNS]

        @overload
        def __init__(
                self, 
                *, 
                fqdns: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networksecurity.models.UrlFilteringPolicy(NetworkSecurityPolicyBase, discriminator='UrlFiltering'):
        default_action: Union[str, PolicyAction]
        destination: Optional[UrlFilteringDestination]
        rules: list[UrlFilteringRule]
        source: UrlFilteringSource
        type: Literal[NetworkSecurityPolicyType.URL_FILTERING]

        @overload
        def __init__(
                self, 
                *, 
                default_action: Union[str, PolicyAction], 
                destination: Optional[UrlFilteringDestination] = ..., 
                rules: list[UrlFilteringRule], 
                source: UrlFilteringSource
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networksecurity.models.UrlFilteringRule(_Model):
        action: Optional[Union[str, PolicyAction]]
        hostname: Optional[str]
        method: Optional[Union[str, HttpMethod]]
        name: str
        paths: Optional[list[str]]
        priority: int

        @overload
        def __init__(
                self, 
                *, 
                action: Optional[Union[str, PolicyAction]] = ..., 
                hostname: Optional[str] = ..., 
                method: Optional[Union[str, HttpMethod]] = ..., 
                name: str, 
                paths: Optional[list[str]] = ..., 
                priority: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networksecurity.models.UrlFilteringSource(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networksecurity.models.UrlFilteringSourceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ADDRESS_PREFIXES = "AddressPrefixes"
        WORKLOAD_ID_PATTERNS = "WorkloadIdPatterns"


    class azure.mgmt.networksecurity.models.UrlFilteringWorkloadIdPatternsDestination(UrlFilteringDestination, discriminator='WorkloadIdPatterns'):
        patterns: list[str]
        type: Literal[UrlFilteringDestinationType.WORKLOAD_ID_PATTERNS]

        @overload
        def __init__(
                self, 
                *, 
                patterns: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networksecurity.models.UrlFilteringWorkloadIdPatternsSource(UrlFilteringSource, discriminator='WorkloadIdPatterns'):
        patterns: list[str]
        type: Literal[UrlFilteringSourceType.WORKLOAD_ID_PATTERNS]

        @overload
        def __init__(
                self, 
                *, 
                patterns: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networksecurity.models.WorkloadBase(_Model):
        member_guid: Optional[str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                member_guid: Optional[str] = ..., 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networksecurity.models.WorkloadType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACI = "ACI"
        AGENT_FABRIC_SANDBOX = "AgentFabricSandbox"
        AKS = "AKS"


namespace azure.mgmt.networksecurity.operations

    class azure.mgmt.networksecurity.operations.AgentFabricsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                agent_fabric_name: str, 
                resource: AgentFabric, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AgentFabric]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                agent_fabric_name: str, 
                resource: AgentFabric, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AgentFabric]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                agent_fabric_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AgentFabric]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                agent_fabric_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                agent_fabric_name: str, 
                properties: AgentFabricTagsUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AgentFabric]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                agent_fabric_name: str, 
                properties: AgentFabricTagsUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AgentFabric]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                agent_fabric_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AgentFabric]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                agent_fabric_name: str, 
                **kwargs: Any
            ) -> AgentFabric: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[AgentFabric]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[AgentFabric]: ...


    class azure.mgmt.networksecurity.operations.ClusterAssociationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                agent_fabric_name: str, 
                cluster_association_name: str, 
                resource: ClusterAssociation, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[Union[str, ClusterAssociationIfNoneMatch]] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[ClusterAssociation]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                agent_fabric_name: str, 
                cluster_association_name: str, 
                resource: ClusterAssociation, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[Union[str, ClusterAssociationIfNoneMatch]] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[ClusterAssociation]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                agent_fabric_name: str, 
                cluster_association_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[Union[str, ClusterAssociationIfNoneMatch]] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[ClusterAssociation]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                agent_fabric_name: str, 
                cluster_association_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                agent_fabric_name: str, 
                cluster_association_name: str, 
                properties: ClusterAssociationUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ClusterAssociation]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                agent_fabric_name: str, 
                cluster_association_name: str, 
                properties: ClusterAssociationUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ClusterAssociation]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                agent_fabric_name: str, 
                cluster_association_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ClusterAssociation]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                agent_fabric_name: str, 
                cluster_association_name: str, 
                **kwargs: Any
            ) -> ClusterAssociation: ...

        @distributed_trace
        def list_by_parent(
                self, 
                resource_group_name: str, 
                agent_fabric_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ClusterAssociation]: ...


    class azure.mgmt.networksecurity.operations.EgressTrustBundlesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                agent_fabric_name: str, 
                **kwargs: Any
            ) -> EgressTrustBundle: ...

        @distributed_trace
        def list_by_parent(
                self, 
                resource_group_name: str, 
                agent_fabric_name: str, 
                **kwargs: Any
            ) -> ItemPaged[EgressTrustBundle]: ...


    class azure.mgmt.networksecurity.operations.MembersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                agent_fabric_name: str, 
                member_name: str, 
                resource: Member, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Member]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                agent_fabric_name: str, 
                member_name: str, 
                resource: Member, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Member]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                agent_fabric_name: str, 
                member_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Member]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                agent_fabric_name: str, 
                member_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                agent_fabric_name: str, 
                member_name: str, 
                properties: MemberTagsUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Member]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                agent_fabric_name: str, 
                member_name: str, 
                properties: MemberTagsUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Member]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                agent_fabric_name: str, 
                member_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Member]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                agent_fabric_name: str, 
                member_name: str, 
                **kwargs: Any
            ) -> Member: ...

        @distributed_trace
        def list_by_parent(
                self, 
                resource_group_name: str, 
                agent_fabric_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Member]: ...


    class azure.mgmt.networksecurity.operations.NeuroShieldFindingsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                neuro_shield_name: str, 
                protected_resource_name: str, 
                finding_id: str, 
                **kwargs: Any
            ) -> NeuroShieldFinding: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                neuro_shield_name: str, 
                protected_resource_name: str, 
                *, 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[NeuroShieldFinding]: ...

        @distributed_trace
        def list_by_neuro_shield(
                self, 
                resource_group_name: str, 
                neuro_shield_name: str, 
                *, 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[NeuroShieldFinding]: ...

        @distributed_trace
        def mitigate(
                self, 
                resource_group_name: str, 
                neuro_shield_name: str, 
                protected_resource_name: str, 
                finding_id: str, 
                **kwargs: Any
            ) -> NeuroShieldMitigationActionResult: ...

        @distributed_trace
        def rollback(
                self, 
                resource_group_name: str, 
                neuro_shield_name: str, 
                protected_resource_name: str, 
                finding_id: str, 
                **kwargs: Any
            ) -> NeuroShieldMitigationActionResult: ...


    class azure.mgmt.networksecurity.operations.NeuroShieldMitigationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def execute(
                self, 
                resource_group_name: str, 
                neuro_shield_name: str, 
                protected_resource_name: str, 
                mitigation_id: str, 
                **kwargs: Any
            ) -> NeuroShieldMitigation: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                neuro_shield_name: str, 
                protected_resource_name: str, 
                mitigation_id: str, 
                **kwargs: Any
            ) -> NeuroShieldMitigation: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                neuro_shield_name: str, 
                protected_resource_name: str, 
                *, 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[NeuroShieldMitigation]: ...

        @distributed_trace
        def list_by_neuro_shield(
                self, 
                resource_group_name: str, 
                neuro_shield_name: str, 
                *, 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[NeuroShieldMitigation]: ...

        @distributed_trace
        def rollback(
                self, 
                resource_group_name: str, 
                neuro_shield_name: str, 
                protected_resource_name: str, 
                mitigation_id: str, 
                **kwargs: Any
            ) -> NeuroShieldMitigation: ...


    class azure.mgmt.networksecurity.operations.NeuroShieldOperationStatusesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                location: str, 
                operation_id: str, 
                **kwargs: Any
            ) -> OperationStatusResult: ...


    class azure.mgmt.networksecurity.operations.NeuroShieldProtectedResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                neuro_shield_name: str, 
                protected_resource_name: str, 
                resource: NeuroShieldProtectedResource, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[NeuroShieldProtectedResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                neuro_shield_name: str, 
                protected_resource_name: str, 
                resource: NeuroShieldProtectedResource, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[NeuroShieldProtectedResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                neuro_shield_name: str, 
                protected_resource_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[NeuroShieldProtectedResource]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                neuro_shield_name: str, 
                protected_resource_name: str, 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                neuro_shield_name: str, 
                protected_resource_name: str, 
                **kwargs: Any
            ) -> NeuroShieldProtectedResource: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                neuro_shield_name: str, 
                *, 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[NeuroShieldProtectedResource]: ...

        @distributed_trace
        def trigger_inventory_upload(
                self, 
                resource_group_name: str, 
                neuro_shield_name: str, 
                protected_resource_name: str, 
                **kwargs: Any
            ) -> NeuroShieldInventoryUploadRequestResult: ...


    class azure.mgmt.networksecurity.operations.NeuroShieldSummariesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                neuro_shield_name: str, 
                **kwargs: Any
            ) -> NeuroShieldSummary: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                neuro_shield_name: str, 
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[NeuroShieldSummary]: ...


    class azure.mgmt.networksecurity.operations.NeuroShieldsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                neuro_shield_name: str, 
                resource: NeuroShieldResource, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> NeuroShieldResource: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                neuro_shield_name: str, 
                resource: NeuroShieldResource, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> NeuroShieldResource: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                neuro_shield_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> NeuroShieldResource: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                neuro_shield_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                neuro_shield_name: str, 
                **kwargs: Any
            ) -> NeuroShieldResource: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[NeuroShieldResource]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[NeuroShieldResource]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                neuro_shield_name: str, 
                properties: NeuroShieldPatch, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> NeuroShieldResource: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                neuro_shield_name: str, 
                properties: NeuroShieldPatch, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> NeuroShieldResource: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                neuro_shield_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> NeuroShieldResource: ...


    class azure.mgmt.networksecurity.operations.OperationStatusOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                location: str, 
                operation_id: str, 
                **kwargs: Any
            ) -> OperationStatusResult: ...


    class azure.mgmt.networksecurity.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        @api_version_validation(params_added_on={'v3': ['api_version']})
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


    class azure.mgmt.networksecurity.operations.PolicyGroupsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                policy_group_name: str, 
                resource: PolicyGroup, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PolicyGroup]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                policy_group_name: str, 
                resource: PolicyGroup, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PolicyGroup]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                policy_group_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PolicyGroup]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                policy_group_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                policy_group_name: str, 
                properties: PolicyGroupTagsUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PolicyGroup]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                policy_group_name: str, 
                properties: PolicyGroupTagsUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PolicyGroup]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                policy_group_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PolicyGroup]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                policy_group_name: str, 
                **kwargs: Any
            ) -> PolicyGroup: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[PolicyGroup]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[PolicyGroup]: ...


namespace azure.mgmt.networksecurity.types

    class azure.mgmt.networksecurity.types.AciWorkload(TypedDict, total=False):
        key "agentIdentity": ForwardRef('AgentIdentity', module='types')
        key "memberGuid": str
        key "resourceId": Required[str]
        key "type": Required[Literal[WorkloadType.ACI]]
        key "workloadId": Required[str]
        agentIdentity: AgentIdentity
        memberGuid: str
        resourceId: str
        type: Literal[WorkloadType.ACI]
        workloadId: str


    class azure.mgmt.networksecurity.types.AgentFabric(TrackedResource):
        key "id": str
        key "identity": ForwardRef('SystemAssignedServiceIdentity', module='types')
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('AgentFabricProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        identity: SystemAssignedServiceIdentity
        location: str
        name: str
        properties: AgentFabricProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.networksecurity.types.AgentFabricProperties(TypedDict, total=False):
        key "contentInspectionProfile": ForwardRef('ContentInspectionProfile', module='types')
        key "provisioningState": Union[str, ProvisioningState]
        key "resourceGuid": str
        key "trustDomain": str
        contentInspectionProfile: ContentInspectionProfile
        defaultPolicyGroups: list[str]
        provisioningState: Union[str, ProvisioningState]
        resourceGuid: str
        trustDomain: str


    class azure.mgmt.networksecurity.types.AgentFabricSandboxEndpoint(TypedDict, total=False):
        key "name": Required[str]
        key "protocol": Required[str]
        key "servicePort": Required[int]
        key "targetPort": Required[int]
        name: str
        protocol: str
        servicePort: int
        targetPort: int


    class azure.mgmt.networksecurity.types.AgentFabricSandboxImage(TypedDict, total=False):
        key "digest": str
        key "pullPolicy": Union[str, ImagePullPolicy]
        key "uri": Required[str]
        digest: str
        pullPolicy: Union[str, ImagePullPolicy]
        uri: str


    class azure.mgmt.networksecurity.types.AgentFabricSandboxResources(TypedDict, total=False):
        key "cpu": Required[str]
        key "disk": str
        key "memory": Required[str]
        cpu: str
        disk: str
        memory: str


    class azure.mgmt.networksecurity.types.AgentFabricSandboxWorkload(TypedDict, total=False):
        key "agentIdentity": ForwardRef('AgentIdentity', module='types')
        key "domain": Required[str]
        key "image": Required[AgentFabricSandboxImage]
        key "memberGuid": str
        key "resources": Required[AgentFabricSandboxResources]
        key "type": Required[Literal[WorkloadType.AGENT_FABRIC_SANDBOX]]
        key "workloadId": str
        agentIdentity: AgentIdentity
        domain: str
        endpoints: list[AgentFabricSandboxEndpoint]
        image: AgentFabricSandboxImage
        memberGuid: str
        resources: AgentFabricSandboxResources
        type: Literal[WorkloadType.AGENT_FABRIC_SANDBOX]
        workloadId: str


    class azure.mgmt.networksecurity.types.AgentFabricTagsUpdate(TypedDict, total=False):
        key "identity": ForwardRef('SystemAssignedServiceIdentity', module='types')
        identity: SystemAssignedServiceIdentity
        tags: dict[str, str]


    class azure.mgmt.networksecurity.types.AgentIdentity(TypedDict, total=False):
        key "agentId": Required[str]
        key "blueprintId": str
        key "tenantId": Required[str]
        agentId: str
        blueprintId: str
        tenantId: str


    class azure.mgmt.networksecurity.types.AksWorkload(TypedDict, total=False):
        key "clusterAssociationId": Required[str]
        key "clusterResourceId": Required[str]
        key "memberGuid": str
        key "type": Required[Literal[WorkloadType.AKS]]
        key "workload": Required[AksWorkloadReference]
        key "workloadId": str
        clusterAssociationId: str
        clusterResourceId: str
        endpoints: list[AksWorkloadPortMapping]
        memberGuid: str
        type: Literal[WorkloadType.AKS]
        workload: AksWorkloadReference
        workloadId: str


    class azure.mgmt.networksecurity.types.AksWorkloadPortMapping(TypedDict, total=False):
        key "name": Required[str]
        key "protocol": Required[str]
        key "servicePort": Required[int]
        key "targetPort": Required[int]
        name: str
        protocol: str
        servicePort: int
        targetPort: int


    class azure.mgmt.networksecurity.types.AksWorkloadReference(TypedDict, total=False):
        key "apiVersion": Required[str]
        key "kind": Required[str]
        key "name": Required[str]
        key "namespace": Required[str]
        apiVersion: str
        kind: str
        name: str
        namespace: str


    class azure.mgmt.networksecurity.types.AzureManagedCaCertificate(TypedDict, total=False):
        key "mode": Required[Literal[TlsInspectionCertificateMode.AZURE_MANAGED_CA]]
        mode: Literal[TlsInspectionCertificateMode.AZURE_MANAGED_CA]


    class azure.mgmt.networksecurity.types.ClusterAssociation(TrackedResource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('ClusterAssociationProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: ClusterAssociationProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.networksecurity.types.ClusterAssociationProperties(TypedDict, total=False):
        key "clusterResourceId": Required[str]
        key "provisioningState": Union[str, ProvisioningState]
        key "sku": Union[str, ClusterAssociationSkuName]
        key "status": ForwardRef('ClusterAssociationStatus', module='types')
        key "workloadClusterGatewayIp": str
        clusterResourceId: str
        provisioningState: Union[str, ProvisioningState]
        sku: Union[str, ClusterAssociationSkuName]
        status: ClusterAssociationStatus
        workloadClusterGatewayIp: str


    class azure.mgmt.networksecurity.types.ClusterAssociationStatus(TypedDict, total=False):
        key "code": str
        key "message": str
        code: str
        message: str


    class azure.mgmt.networksecurity.types.ClusterAssociationUpdate(TypedDict, total=False):
        key "properties": Required[ClusterAssociationUpdateProperties]
        properties: ClusterAssociationUpdateProperties
        tags: dict[str, str]


    class azure.mgmt.networksecurity.types.ClusterAssociationUpdateProperties(TypedDict, total=False):
        key "clusterResourceId": str
        key "sku": Union[str, ClusterAssociationSkuName]
        key "workloadClusterGatewayIp": str
        clusterResourceId: str
        sku: Union[str, ClusterAssociationSkuName]
        workloadClusterGatewayIp: str


    class azure.mgmt.networksecurity.types.ContentInspectionPolicy(TypedDict, total=False):
        key "promptInjectionProtection": ForwardRef('PromptInjectionProtection', module='types')
        key "source": Required[ContentInspectionPolicySource]
        key "type": Required[Literal[NetworkSecurityPolicyType.CONTENT_INSPECTION]]
        promptInjectionProtection: PromptInjectionProtection
        source: ContentInspectionPolicySource
        type: Literal[NetworkSecurityPolicyType.CONTENT_INSPECTION]


    class azure.mgmt.networksecurity.types.ContentInspectionPolicyAddressPrefixesSource(TypedDict, total=False):
        key "prefixes": Required[list[str]]
        key "type": Required[Literal[ContentInspectionPolicySourceType.ADDRESS_PREFIXES]]
        prefixes: list[str]
        type: Literal[ContentInspectionPolicySourceType.ADDRESS_PREFIXES]


    class azure.mgmt.networksecurity.types.ContentInspectionPolicySourceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ADDRESS_PREFIXES = "AddressPrefixes"
        WORKLOAD_ID_PATTERNS = "WorkloadIdPatterns"


    class azure.mgmt.networksecurity.types.ContentInspectionPolicyWorkloadIdPatternsSource(TypedDict, total=False):
        key "patterns": Required[list[str]]
        key "type": Required[Literal[ContentInspectionPolicySourceType.WORKLOAD_ID_PATTERNS]]
        patterns: list[str]
        type: Literal[ContentInspectionPolicySourceType.WORKLOAD_ID_PATTERNS]


    class azure.mgmt.networksecurity.types.ContentInspectionProfile(TypedDict, total=False):
        key "apiKey": str
        key "endpoint": str
        apiKey: str
        endpoint: str


    class azure.mgmt.networksecurity.types.FqdnFilteringAddressPrefixesSource(TypedDict, total=False):
        key "prefixes": Required[list[str]]
        key "type": Required[Literal[FqdnFilteringSourceType.ADDRESS_PREFIXES]]
        prefixes: list[str]
        type: Literal[FqdnFilteringSourceType.ADDRESS_PREFIXES]


    class azure.mgmt.networksecurity.types.FqdnFilteringDestination(TypedDict, total=False):
        key "fqdns": Required[list[str]]
        key "type": Required[Literal[FqdnFilteringDestinationType.FQDNS]]
        fqdns: list[str]
        type: Literal[FqdnFilteringDestinationType.FQDNS]


    class azure.mgmt.networksecurity.types.FqdnFilteringDestinationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FQDNS = "Fqdns"


    class azure.mgmt.networksecurity.types.FqdnFilteringFqdnsDestination(TypedDict, total=False):
        key "fqdns": Required[list[str]]
        key "type": Required[Literal[FqdnFilteringDestinationType.FQDNS]]
        fqdns: list[str]
        type: Literal[FqdnFilteringDestinationType.FQDNS]


    class azure.mgmt.networksecurity.types.FqdnFilteringPolicy(TypedDict, total=False):
        key "destination": ForwardRef('FqdnFilteringDestination', module='types')
        key "direction": Union[str, PolicyDirection]
        key "name": str
        key "priority": int
        key "source": Required[FqdnFilteringSource]
        key "type": Required[Literal[NetworkSecurityPolicyType.FQDN_FILTERING]]
        destination: FqdnFilteringDestination
        direction: Union[str, PolicyDirection]
        name: str
        ports: list[int]
        priority: int
        source: FqdnFilteringSource
        type: Literal[NetworkSecurityPolicyType.FQDN_FILTERING]


    class azure.mgmt.networksecurity.types.FqdnFilteringSourceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ADDRESS_PREFIXES = "AddressPrefixes"
        WORKLOAD_ID_PATTERNS = "WorkloadIdPatterns"


    class azure.mgmt.networksecurity.types.FqdnFilteringWorkloadIdPatternsSource(TypedDict, total=False):
        key "patterns": Required[list[str]]
        key "type": Required[Literal[FqdnFilteringSourceType.WORKLOAD_ID_PATTERNS]]
        patterns: list[str]
        type: Literal[FqdnFilteringSourceType.WORKLOAD_ID_PATTERNS]


    class azure.mgmt.networksecurity.types.McpArgumentMatching(TypedDict, total=False):
        key "matchCase": Union[str, McpMatchCase]
        key "matchType": Required[Union[str, McpMatchType]]
        key "path": str
        key "values": Required[list[str]]
        matchCase: Union[str, McpMatchCase]
        matchType: Union[str, McpMatchType]
        path: str
        values: list[str]


    class azure.mgmt.networksecurity.types.McpPolicy(TypedDict, total=False):
        key "defaultAction": Required[Union[str, PolicyAction]]
        key "destination": Required[McpPolicyDestination]
        key "rules": Required[list[McpRule]]
        key "source": Required[McpPolicySource]
        key "type": Required[Literal[NetworkSecurityPolicyType.MCP]]
        defaultAction: Union[str, PolicyAction]
        destination: McpPolicyDestination
        rules: list[McpRule]
        source: McpPolicySource
        type: Literal[NetworkSecurityPolicyType.MCP]


    class azure.mgmt.networksecurity.types.McpPolicyAddressPrefixesDestination(TypedDict, total=False):
        key "prefixes": Required[list[str]]
        key "type": Required[Literal[McpPolicyDestinationType.ADDRESS_PREFIXES]]
        prefixes: list[str]
        type: Literal[McpPolicyDestinationType.ADDRESS_PREFIXES]


    class azure.mgmt.networksecurity.types.McpPolicyAddressPrefixesSource(TypedDict, total=False):
        key "prefixes": Required[list[str]]
        key "type": Required[Literal[McpPolicySourceType.ADDRESS_PREFIXES]]
        prefixes: list[str]
        type: Literal[McpPolicySourceType.ADDRESS_PREFIXES]


    class azure.mgmt.networksecurity.types.McpPolicyDestinationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ADDRESS_PREFIXES = "AddressPrefixes"
        FQDNS = "Fqdns"
        WORKLOAD_ID_PATTERNS = "WorkloadIdPatterns"


    class azure.mgmt.networksecurity.types.McpPolicyFqdnsDestination(TypedDict, total=False):
        key "fqdns": Required[list[str]]
        key "type": Required[Literal[McpPolicyDestinationType.FQDNS]]
        fqdns: list[str]
        type: Literal[McpPolicyDestinationType.FQDNS]


    class azure.mgmt.networksecurity.types.McpPolicySourceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ADDRESS_PREFIXES = "AddressPrefixes"
        WORKLOAD_ID_PATTERNS = "WorkloadIdPatterns"


    class azure.mgmt.networksecurity.types.McpPolicyWorkloadIdPatternsDestination(TypedDict, total=False):
        key "patterns": Required[list[str]]
        key "type": Required[Literal[McpPolicyDestinationType.WORKLOAD_ID_PATTERNS]]
        patterns: list[str]
        type: Literal[McpPolicyDestinationType.WORKLOAD_ID_PATTERNS]


    class azure.mgmt.networksecurity.types.McpPolicyWorkloadIdPatternsSource(TypedDict, total=False):
        key "patterns": Required[list[str]]
        key "type": Required[Literal[McpPolicySourceType.WORKLOAD_ID_PATTERNS]]
        patterns: list[str]
        type: Literal[McpPolicySourceType.WORKLOAD_ID_PATTERNS]


    class azure.mgmt.networksecurity.types.McpPromptMatching(TypedDict, total=False):
        key "arguments": ForwardRef('McpArgumentMatching', module='types')
        key "descriptions": ForwardRef('McpStringMatching', module='types')
        key "names": ForwardRef('McpStringMatching', module='types')
        key "responseContents": ForwardRef('McpStringMatching', module='types')
        key "titles": ForwardRef('McpStringMatching', module='types')
        arguments: McpArgumentMatching
        descriptions: McpStringMatching
        methods: list[Union[str, McpPromptMethod]]
        names: McpStringMatching
        responseContents: McpStringMatching
        titles: McpStringMatching


    class azure.mgmt.networksecurity.types.McpRule(TypedDict, total=False):
        key "action": Union[str, PolicyAction]
        key "matchingConditions": ForwardRef('McpRuleMatchingConditions', module='types')
        key "name": str
        key "priority": int
        action: Union[str, PolicyAction]
        matchingConditions: McpRuleMatchingConditions
        name: str
        priority: int
        tools: list[str]


    class azure.mgmt.networksecurity.types.McpRuleDestinationMatching(TypedDict, total=False):
        key "promptMatching": ForwardRef('McpPromptMatching', module='types')
        key "protocolVersions": ForwardRef('McpStringMatching', module='types')
        key "toolMatching": ForwardRef('McpToolMatching', module='types')
        promptMatching: McpPromptMatching
        protocolVersions: McpStringMatching
        serverFqdns: list[str]
        toolMatching: McpToolMatching


    class azure.mgmt.networksecurity.types.McpRuleMatchingConditions(TypedDict, total=False):
        key "destinations": Required[McpRuleDestinationMatching]
        destinations: McpRuleDestinationMatching


    class azure.mgmt.networksecurity.types.McpStringMatching(TypedDict, total=False):
        key "matchCase": Union[str, McpMatchCase]
        key "matchType": Required[Union[str, McpMatchType]]
        key "values": Required[list[str]]
        matchCase: Union[str, McpMatchCase]
        matchType: Union[str, McpMatchType]
        values: list[str]


    class azure.mgmt.networksecurity.types.McpToolMatching(TypedDict, total=False):
        key "callArguments": ForwardRef('McpArgumentMatching', module='types')
        key "descriptions": ForwardRef('McpStringMatching', module='types')
        key "names": ForwardRef('McpStringMatching', module='types')
        key "responseContents": ForwardRef('McpStringMatching', module='types')
        key "titles": ForwardRef('McpStringMatching', module='types')
        callArguments: McpArgumentMatching
        descriptions: McpStringMatching
        methods: list[Union[str, McpToolMethod]]
        names: McpStringMatching
        responseContents: McpStringMatching
        titles: McpStringMatching


    class azure.mgmt.networksecurity.types.Member(TrackedResource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('MemberProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: MemberProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.networksecurity.types.MemberProperties(TypedDict, total=False):
        key "fqdn": str
        key "provisioningState": Union[str, ProvisioningState]
        key "spiffeId": str
        key "workload": ForwardRef('WorkloadBase', module='types')
        fqdn: str
        provisioningState: Union[str, ProvisioningState]
        spiffeId: str
        workload: WorkloadBase


    class azure.mgmt.networksecurity.types.MemberTagsUpdate(TypedDict, total=False):
        key "properties": ForwardRef('MemberUpdateProperties', module='types')
        properties: MemberUpdateProperties
        tags: dict[str, str]


    class azure.mgmt.networksecurity.types.MemberUpdateProperties(TypedDict, total=False):
        key "fqdn": str
        fqdn: str


    class azure.mgmt.networksecurity.types.NetworkSecurityPolicyType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONTENT_INSPECTION = "ContentInspection"
        FQDN_FILTERING = "FqdnFiltering"
        MCP = "Mcp"
        TLS_INSPECTION = "TlsInspection"
        URL_FILTERING = "UrlFiltering"


    class azure.mgmt.networksecurity.types.NeuroShieldAgentHealth(TypedDict, total=False):
        key "lastSeenTime": str
        lastSeenTime: str


    class azure.mgmt.networksecurity.types.NeuroShieldInventoryUploadRequestMetadata(TypedDict, total=False):
        key "expiresAt": Required[str]
        key "requestId": Required[str]
        key "requestedAt": Required[str]
        expiresAt: str
        requestId: str
        requestedAt: str


    class azure.mgmt.networksecurity.types.NeuroShieldPatch(TypedDict, total=False):
        key "properties": ForwardRef('NeuroShieldPatchProperties', module='types')
        key "tags": Any
        properties: NeuroShieldPatchProperties
        tags: Any


    class azure.mgmt.networksecurity.types.NeuroShieldPatchProperties(TypedDict, total=False):
        key "description": str
        key "responseMode": Union[str, NeuroShieldResponseMode]
        key "severityThreshold": Union[str, NeuroShieldSeverityThreshold]
        description: str
        responseMode: Union[str, NeuroShieldResponseMode]
        severityThreshold: Union[str, NeuroShieldSeverityThreshold]


    class azure.mgmt.networksecurity.types.NeuroShieldProperties(TypedDict, total=False):
        key "description": str
        key "provisioningState": Union[str, ProvisioningStateNeuroShield]
        key "resourceGuid": str
        key "responseMode": Required[Union[str, NeuroShieldResponseMode]]
        key "severityThreshold": Union[str, NeuroShieldSeverityThreshold]
        description: str
        provisioningState: Union[str, ProvisioningStateNeuroShield]
        resourceGuid: str
        responseMode: Union[str, NeuroShieldResponseMode]
        severityThreshold: Union[str, NeuroShieldSeverityThreshold]


    class azure.mgmt.networksecurity.types.NeuroShieldProtectedResource(ProxyResource):
        key "id": str
        key "name": str
        key "properties": Required[NeuroShieldProtectedResourceProperties]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: NeuroShieldProtectedResourceProperties
        systemData: SystemData
        type: str


    class azure.mgmt.networksecurity.types.NeuroShieldProtectedResourceIdentity(TypedDict, total=False):
        key "principalId": str
        key "tenantId": str
        key "type": Required[Union[str, ManagedServiceIdentityType]]
        key "userAssignedIdentities": Any
        principalId: str
        tenantId: str
        type: Union[str, ManagedServiceIdentityType]
        userAssignedIdentities: Any


    class azure.mgmt.networksecurity.types.NeuroShieldProtectedResourceProperties(TypedDict, total=False):
        key "agentHealth": ForwardRef('NeuroShieldAgentHealth', module='types')
        key "inventoryUploadRequest": ForwardRef('NeuroShieldInventoryUploadRequestMetadata', module='types')
        key "provisioningState": Union[str, ProvisioningStateNeuroShield]
        key "targetIdentity": ForwardRef('NeuroShieldProtectedResourceIdentity', module='types')
        key "targetResourceId": Required[str]
        agentHealth: NeuroShieldAgentHealth
        inventoryUploadRequest: NeuroShieldInventoryUploadRequestMetadata
        provisioningState: Union[str, ProvisioningStateNeuroShield]
        targetIdentity: NeuroShieldProtectedResourceIdentity
        targetResourceId: str


    class azure.mgmt.networksecurity.types.NeuroShieldResource(TrackedResource):
        key "etag": str
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": Required[NeuroShieldProperties]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        id: str
        location: str
        name: str
        properties: NeuroShieldProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.networksecurity.types.PolicyGroup(TrackedResource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('PolicyGroupProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: PolicyGroupProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.networksecurity.types.PolicyGroupProperties(TypedDict, total=False):
        key "description": str
        key "displayName": str
        key "priority": int
        key "provisioningState": Union[str, ProvisioningState]
        description: str
        displayName: str
        networkSecurityPolicies: list[NetworkSecurityPolicyBase]
        priority: int
        provisioningState: Union[str, ProvisioningState]


    class azure.mgmt.networksecurity.types.PolicyGroupTagsUpdate(TypedDict, total=False):
        tags: dict[str, str]


    class azure.mgmt.networksecurity.types.PromptInjectionProtection(TypedDict, total=False):
        key "onDetection": Required[Union[str, PromptInjectionOnDetection]]
        key "sensitivity": Union[str, ContentInspectionSensitivity]
        onDetection: Union[str, PromptInjectionOnDetection]
        promptLocations: list[str]
        responseLocations: list[str]
        sensitivity: Union[str, ContentInspectionSensitivity]


    class azure.mgmt.networksecurity.types.ProxyResource(Resource):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        systemData: SystemData
        type: str


    class azure.mgmt.networksecurity.types.Resource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        systemData: SystemData
        type: str


    class azure.mgmt.networksecurity.types.SystemAssignedServiceIdentity(TypedDict, total=False):
        key "principalId": str
        key "tenantId": str
        key "type": Required[Union[str, SystemAssignedServiceIdentityType]]
        principalId: str
        tenantId: str
        type: Union[str, SystemAssignedServiceIdentityType]


    class azure.mgmt.networksecurity.types.SystemData(TypedDict, total=False):
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


    class azure.mgmt.networksecurity.types.TlsInspectionCertificateBase(TypedDict, total=False):
        key "mode": Required[Literal[TlsInspectionCertificateMode.AZURE_MANAGED_CA]]
        mode: Literal[TlsInspectionCertificateMode.AZURE_MANAGED_CA]


    class azure.mgmt.networksecurity.types.TlsInspectionCertificateMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_MANAGED_CA = "AzureManagedCA"


    class azure.mgmt.networksecurity.types.TlsInspectionPolicy(TypedDict, total=False):
        key "certificate": Required[TlsInspectionCertificateBase]
        key "defaultAction": Union[str, TlsInspectionAction]
        key "source": Required[TlsInspectionPolicySource]
        key "type": Required[Literal[NetworkSecurityPolicyType.TLS_INSPECTION]]
        certificate: TlsInspectionCertificateBase
        defaultAction: Union[str, TlsInspectionAction]
        rules: list[TlsInspectionRule]
        source: TlsInspectionPolicySource
        type: Literal[NetworkSecurityPolicyType.TLS_INSPECTION]


    class azure.mgmt.networksecurity.types.TlsInspectionPolicySource(TypedDict, total=False):
        key "patterns": Required[list[str]]
        key "type": Required[Literal[TlsInspectionPolicySourceType.WORKLOAD_ID_PATTERNS]]
        patterns: list[str]
        type: Literal[TlsInspectionPolicySourceType.WORKLOAD_ID_PATTERNS]


    class azure.mgmt.networksecurity.types.TlsInspectionPolicySourceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        WORKLOAD_ID_PATTERNS = "WorkloadIdPatterns"


    class azure.mgmt.networksecurity.types.TlsInspectionPolicyWorkloadIdPatternsSource(TypedDict, total=False):
        key "patterns": Required[list[str]]
        key "type": Required[Literal[TlsInspectionPolicySourceType.WORKLOAD_ID_PATTERNS]]
        patterns: list[str]
        type: Literal[TlsInspectionPolicySourceType.WORKLOAD_ID_PATTERNS]


    class azure.mgmt.networksecurity.types.TlsInspectionRule(TypedDict, total=False):
        key "action": Union[str, TlsInspectionAction]
        key "destinations": Required[list[TlsInspectionRuleDestination]]
        key "name": Required[str]
        key "priority": Required[int]
        action: Union[str, TlsInspectionAction]
        destinations: list[TlsInspectionRuleDestination]
        name: str
        priority: int


    class azure.mgmt.networksecurity.types.TlsInspectionRuleDestination(TypedDict, total=False):
        key "fqdns": Required[list[str]]
        key "type": Required[Literal[TlsInspectionRuleDestinationType.FQDNS]]
        fqdns: list[str]
        type: Literal[TlsInspectionRuleDestinationType.FQDNS]


    class azure.mgmt.networksecurity.types.TlsInspectionRuleDestinationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FQDNS = "Fqdns"


    class azure.mgmt.networksecurity.types.TlsInspectionRuleFqdnsDestination(TypedDict, total=False):
        key "fqdns": Required[list[str]]
        key "type": Required[Literal[TlsInspectionRuleDestinationType.FQDNS]]
        fqdns: list[str]
        type: Literal[TlsInspectionRuleDestinationType.FQDNS]


    class azure.mgmt.networksecurity.types.TrackedResource(Resource):
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


    class azure.mgmt.networksecurity.types.UrlFilteringAddressPrefixesDestination(TypedDict, total=False):
        key "prefixes": Required[list[str]]
        key "type": Required[Literal[UrlFilteringDestinationType.ADDRESS_PREFIXES]]
        prefixes: list[str]
        type: Literal[UrlFilteringDestinationType.ADDRESS_PREFIXES]


    class azure.mgmt.networksecurity.types.UrlFilteringAddressPrefixesSource(TypedDict, total=False):
        key "prefixes": Required[list[str]]
        key "type": Required[Literal[UrlFilteringSourceType.ADDRESS_PREFIXES]]
        prefixes: list[str]
        type: Literal[UrlFilteringSourceType.ADDRESS_PREFIXES]


    class azure.mgmt.networksecurity.types.UrlFilteringDestinationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ADDRESS_PREFIXES = "AddressPrefixes"
        FQDNS = "Fqdns"
        WORKLOAD_ID_PATTERNS = "WorkloadIdPatterns"


    class azure.mgmt.networksecurity.types.UrlFilteringFqdnsDestination(TypedDict, total=False):
        key "fqdns": Required[list[str]]
        key "type": Required[Literal[UrlFilteringDestinationType.FQDNS]]
        fqdns: list[str]
        type: Literal[UrlFilteringDestinationType.FQDNS]


    class azure.mgmt.networksecurity.types.UrlFilteringPolicy(TypedDict, total=False):
        key "defaultAction": Required[Union[str, PolicyAction]]
        key "destination": ForwardRef('UrlFilteringDestination', module='types')
        key "rules": Required[list[UrlFilteringRule]]
        key "source": Required[UrlFilteringSource]
        key "type": Required[Literal[NetworkSecurityPolicyType.URL_FILTERING]]
        defaultAction: Union[str, PolicyAction]
        destination: UrlFilteringDestination
        rules: list[UrlFilteringRule]
        source: UrlFilteringSource
        type: Literal[NetworkSecurityPolicyType.URL_FILTERING]


    class azure.mgmt.networksecurity.types.UrlFilteringRule(TypedDict, total=False):
        key "action": Union[str, PolicyAction]
        key "hostname": str
        key "method": Union[str, HttpMethod]
        key "name": Required[str]
        key "priority": Required[int]
        action: Union[str, PolicyAction]
        hostname: str
        method: Union[str, HttpMethod]
        name: str
        paths: list[str]
        priority: int


    class azure.mgmt.networksecurity.types.UrlFilteringSourceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ADDRESS_PREFIXES = "AddressPrefixes"
        WORKLOAD_ID_PATTERNS = "WorkloadIdPatterns"


    class azure.mgmt.networksecurity.types.UrlFilteringWorkloadIdPatternsDestination(TypedDict, total=False):
        key "patterns": Required[list[str]]
        key "type": Required[Literal[UrlFilteringDestinationType.WORKLOAD_ID_PATTERNS]]
        patterns: list[str]
        type: Literal[UrlFilteringDestinationType.WORKLOAD_ID_PATTERNS]


    class azure.mgmt.networksecurity.types.UrlFilteringWorkloadIdPatternsSource(TypedDict, total=False):
        key "patterns": Required[list[str]]
        key "type": Required[Literal[UrlFilteringSourceType.WORKLOAD_ID_PATTERNS]]
        patterns: list[str]
        type: Literal[UrlFilteringSourceType.WORKLOAD_ID_PATTERNS]


    class azure.mgmt.networksecurity.types.WorkloadType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACI = "ACI"
        AGENT_FABRIC_SANDBOX = "AgentFabricSandbox"
        AKS = "AKS"


```