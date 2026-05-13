```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.dnsresolver

    class azure.mgmt.dnsresolver.DnsResolverManagementClient: implements ContextManager 
        dns_forwarding_rulesets: DnsForwardingRulesetsOperations
        dns_resolver_domain_lists: DnsResolverDomainListsOperations
        dns_resolver_policies: DnsResolverPoliciesOperations
        dns_resolver_policy_virtual_network_links: DnsResolverPolicyVirtualNetworkLinksOperations
        dns_resolvers: DnsResolversOperations
        dns_security_rules: DnsSecurityRulesOperations
        forwarding_rules: ForwardingRulesOperations
        inbound_endpoints: InboundEndpointsOperations
        outbound_endpoints: OutboundEndpointsOperations
        virtual_network_links: VirtualNetworkLinksOperations

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


namespace azure.mgmt.dnsresolver.aio

    class azure.mgmt.dnsresolver.aio.DnsResolverManagementClient: implements AsyncContextManager 
        dns_forwarding_rulesets: DnsForwardingRulesetsOperations
        dns_resolver_domain_lists: DnsResolverDomainListsOperations
        dns_resolver_policies: DnsResolverPoliciesOperations
        dns_resolver_policy_virtual_network_links: DnsResolverPolicyVirtualNetworkLinksOperations
        dns_resolvers: DnsResolversOperations
        dns_security_rules: DnsSecurityRulesOperations
        forwarding_rules: ForwardingRulesOperations
        inbound_endpoints: InboundEndpointsOperations
        outbound_endpoints: OutboundEndpointsOperations
        virtual_network_links: VirtualNetworkLinksOperations

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


namespace azure.mgmt.dnsresolver.aio.operations

    class azure.mgmt.dnsresolver.aio.operations.DnsForwardingRulesetsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                dns_forwarding_ruleset_name: str, 
                parameters: DnsForwardingRuleset, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[DnsForwardingRuleset]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                dns_forwarding_ruleset_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[DnsForwardingRuleset]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                dns_forwarding_ruleset_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[DnsForwardingRuleset]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                dns_forwarding_ruleset_name: str, 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                dns_forwarding_ruleset_name: str, 
                parameters: DnsForwardingRulesetPatch, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[DnsForwardingRuleset]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                dns_forwarding_ruleset_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[DnsForwardingRuleset]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                dns_forwarding_ruleset_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[DnsForwardingRuleset]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                dns_forwarding_ruleset_name: str, 
                **kwargs: Any
            ) -> DnsForwardingRuleset: ...

        @distributed_trace
        def list(
                self, 
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[DnsForwardingRuleset]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[DnsForwardingRuleset]: ...

        @distributed_trace
        def list_by_virtual_network(
                self, 
                resource_group_name: str, 
                virtual_network_name: str, 
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[VirtualNetworkDnsForwardingRuleset]: ...


    class azure.mgmt.dnsresolver.aio.operations.DnsResolverDomainListsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_bulk(
                self, 
                resource_group_name: str, 
                dns_resolver_domain_list_name: str, 
                parameters: DnsResolverDomainListBulk, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[DnsResolverDomainList]: ...

        @overload
        async def begin_bulk(
                self, 
                resource_group_name: str, 
                dns_resolver_domain_list_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[DnsResolverDomainList]: ...

        @overload
        async def begin_bulk(
                self, 
                resource_group_name: str, 
                dns_resolver_domain_list_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[DnsResolverDomainList]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                dns_resolver_domain_list_name: str, 
                parameters: DnsResolverDomainList, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[DnsResolverDomainList]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                dns_resolver_domain_list_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[DnsResolverDomainList]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                dns_resolver_domain_list_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[DnsResolverDomainList]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                dns_resolver_domain_list_name: str, 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                dns_resolver_domain_list_name: str, 
                parameters: DnsResolverDomainListPatch, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[DnsResolverDomainList]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                dns_resolver_domain_list_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[DnsResolverDomainList]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                dns_resolver_domain_list_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[DnsResolverDomainList]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                dns_resolver_domain_list_name: str, 
                **kwargs: Any
            ) -> DnsResolverDomainList: ...

        @distributed_trace
        def list(
                self, 
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[DnsResolverDomainList]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[DnsResolverDomainList]: ...


    class azure.mgmt.dnsresolver.aio.operations.DnsResolverPoliciesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                dns_resolver_policy_name: str, 
                parameters: DnsResolverPolicy, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[DnsResolverPolicy]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                dns_resolver_policy_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[DnsResolverPolicy]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                dns_resolver_policy_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[DnsResolverPolicy]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                dns_resolver_policy_name: str, 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                dns_resolver_policy_name: str, 
                parameters: DnsResolverPolicyPatch, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[DnsResolverPolicy]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                dns_resolver_policy_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[DnsResolverPolicy]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                dns_resolver_policy_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[DnsResolverPolicy]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                dns_resolver_policy_name: str, 
                **kwargs: Any
            ) -> DnsResolverPolicy: ...

        @distributed_trace
        def list(
                self, 
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[DnsResolverPolicy]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[DnsResolverPolicy]: ...

        @distributed_trace
        def list_by_virtual_network(
                self, 
                resource_group_name: str, 
                virtual_network_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[SubResource]: ...


    class azure.mgmt.dnsresolver.aio.operations.DnsResolverPolicyVirtualNetworkLinksOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                dns_resolver_policy_name: str, 
                dns_resolver_policy_virtual_network_link_name: str, 
                parameters: DnsResolverPolicyVirtualNetworkLink, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[DnsResolverPolicyVirtualNetworkLink]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                dns_resolver_policy_name: str, 
                dns_resolver_policy_virtual_network_link_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[DnsResolverPolicyVirtualNetworkLink]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                dns_resolver_policy_name: str, 
                dns_resolver_policy_virtual_network_link_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[DnsResolverPolicyVirtualNetworkLink]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                dns_resolver_policy_name: str, 
                dns_resolver_policy_virtual_network_link_name: str, 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                dns_resolver_policy_name: str, 
                dns_resolver_policy_virtual_network_link_name: str, 
                parameters: DnsResolverPolicyVirtualNetworkLinkPatch, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[DnsResolverPolicyVirtualNetworkLink]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                dns_resolver_policy_name: str, 
                dns_resolver_policy_virtual_network_link_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[DnsResolverPolicyVirtualNetworkLink]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                dns_resolver_policy_name: str, 
                dns_resolver_policy_virtual_network_link_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[DnsResolverPolicyVirtualNetworkLink]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                dns_resolver_policy_name: str, 
                dns_resolver_policy_virtual_network_link_name: str, 
                **kwargs: Any
            ) -> DnsResolverPolicyVirtualNetworkLink: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                dns_resolver_policy_name: str, 
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[DnsResolverPolicyVirtualNetworkLink]: ...


    class azure.mgmt.dnsresolver.aio.operations.DnsResolversOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                dns_resolver_name: str, 
                parameters: DnsResolver, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[DnsResolver]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                dns_resolver_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[DnsResolver]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                dns_resolver_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[DnsResolver]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                dns_resolver_name: str, 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                dns_resolver_name: str, 
                parameters: DnsResolverPatch, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[DnsResolver]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                dns_resolver_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[DnsResolver]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                dns_resolver_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[DnsResolver]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                dns_resolver_name: str, 
                **kwargs: Any
            ) -> DnsResolver: ...

        @distributed_trace
        def list(
                self, 
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[DnsResolver]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[DnsResolver]: ...

        @distributed_trace
        def list_by_virtual_network(
                self, 
                resource_group_name: str, 
                virtual_network_name: str, 
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[SubResource]: ...


    class azure.mgmt.dnsresolver.aio.operations.DnsSecurityRulesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                dns_resolver_policy_name: str, 
                dns_security_rule_name: str, 
                parameters: DnsSecurityRule, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[DnsSecurityRule]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                dns_resolver_policy_name: str, 
                dns_security_rule_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[DnsSecurityRule]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                dns_resolver_policy_name: str, 
                dns_security_rule_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[DnsSecurityRule]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                dns_resolver_policy_name: str, 
                dns_security_rule_name: str, 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                dns_resolver_policy_name: str, 
                dns_security_rule_name: str, 
                parameters: DnsSecurityRulePatch, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[DnsSecurityRule]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                dns_resolver_policy_name: str, 
                dns_security_rule_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[DnsSecurityRule]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                dns_resolver_policy_name: str, 
                dns_security_rule_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[DnsSecurityRule]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                dns_resolver_policy_name: str, 
                dns_security_rule_name: str, 
                **kwargs: Any
            ) -> DnsSecurityRule: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                dns_resolver_policy_name: str, 
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[DnsSecurityRule]: ...


    class azure.mgmt.dnsresolver.aio.operations.ForwardingRulesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                dns_forwarding_ruleset_name: str, 
                forwarding_rule_name: str, 
                parameters: ForwardingRule, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> ForwardingRule: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                dns_forwarding_ruleset_name: str, 
                forwarding_rule_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> ForwardingRule: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                dns_forwarding_ruleset_name: str, 
                forwarding_rule_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> ForwardingRule: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                dns_forwarding_ruleset_name: str, 
                forwarding_rule_name: str, 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                dns_forwarding_ruleset_name: str, 
                forwarding_rule_name: str, 
                **kwargs: Any
            ) -> ForwardingRule: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                dns_forwarding_ruleset_name: str, 
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[ForwardingRule]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                dns_forwarding_ruleset_name: str, 
                forwarding_rule_name: str, 
                parameters: ForwardingRulePatch, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> ForwardingRule: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                dns_forwarding_ruleset_name: str, 
                forwarding_rule_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> ForwardingRule: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                dns_forwarding_ruleset_name: str, 
                forwarding_rule_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> ForwardingRule: ...


    class azure.mgmt.dnsresolver.aio.operations.InboundEndpointsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                dns_resolver_name: str, 
                inbound_endpoint_name: str, 
                parameters: InboundEndpoint, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[InboundEndpoint]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                dns_resolver_name: str, 
                inbound_endpoint_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[InboundEndpoint]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                dns_resolver_name: str, 
                inbound_endpoint_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[InboundEndpoint]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                dns_resolver_name: str, 
                inbound_endpoint_name: str, 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                dns_resolver_name: str, 
                inbound_endpoint_name: str, 
                parameters: InboundEndpointPatch, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[InboundEndpoint]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                dns_resolver_name: str, 
                inbound_endpoint_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[InboundEndpoint]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                dns_resolver_name: str, 
                inbound_endpoint_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[InboundEndpoint]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                dns_resolver_name: str, 
                inbound_endpoint_name: str, 
                **kwargs: Any
            ) -> InboundEndpoint: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                dns_resolver_name: str, 
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[InboundEndpoint]: ...


    class azure.mgmt.dnsresolver.aio.operations.OutboundEndpointsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                dns_resolver_name: str, 
                outbound_endpoint_name: str, 
                parameters: OutboundEndpoint, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[OutboundEndpoint]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                dns_resolver_name: str, 
                outbound_endpoint_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[OutboundEndpoint]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                dns_resolver_name: str, 
                outbound_endpoint_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[OutboundEndpoint]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                dns_resolver_name: str, 
                outbound_endpoint_name: str, 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                dns_resolver_name: str, 
                outbound_endpoint_name: str, 
                parameters: OutboundEndpointPatch, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[OutboundEndpoint]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                dns_resolver_name: str, 
                outbound_endpoint_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[OutboundEndpoint]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                dns_resolver_name: str, 
                outbound_endpoint_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[OutboundEndpoint]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                dns_resolver_name: str, 
                outbound_endpoint_name: str, 
                **kwargs: Any
            ) -> OutboundEndpoint: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                dns_resolver_name: str, 
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[OutboundEndpoint]: ...


    class azure.mgmt.dnsresolver.aio.operations.VirtualNetworkLinksOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                dns_forwarding_ruleset_name: str, 
                virtual_network_link_name: str, 
                parameters: VirtualNetworkLink, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualNetworkLink]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                dns_forwarding_ruleset_name: str, 
                virtual_network_link_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualNetworkLink]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                dns_forwarding_ruleset_name: str, 
                virtual_network_link_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualNetworkLink]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                dns_forwarding_ruleset_name: str, 
                virtual_network_link_name: str, 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                dns_forwarding_ruleset_name: str, 
                virtual_network_link_name: str, 
                parameters: VirtualNetworkLinkPatch, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualNetworkLink]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                dns_forwarding_ruleset_name: str, 
                virtual_network_link_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualNetworkLink]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                dns_forwarding_ruleset_name: str, 
                virtual_network_link_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualNetworkLink]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                dns_forwarding_ruleset_name: str, 
                virtual_network_link_name: str, 
                **kwargs: Any
            ) -> VirtualNetworkLink: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                dns_forwarding_ruleset_name: str, 
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[VirtualNetworkLink]: ...


namespace azure.mgmt.dnsresolver.models

    class azure.mgmt.dnsresolver.models.Action(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DOWNLOAD = "Download"
        UPLOAD = "Upload"


    class azure.mgmt.dnsresolver.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALERT = "Alert"
        ALLOW = "Allow"
        BLOCK = "Block"


    class azure.mgmt.dnsresolver.models.CloudError(_Model):
        error: Optional[CloudErrorBody]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[CloudErrorBody] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dnsresolver.models.CloudErrorBody(_Model):
        code: Optional[str]
        details: Optional[list[CloudErrorBody]]
        message: Optional[str]
        target: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                details: Optional[list[CloudErrorBody]] = ..., 
                message: Optional[str] = ..., 
                target: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dnsresolver.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.dnsresolver.models.DnsForwardingRuleset(TrackedResource):
        etag: Optional[str]
        id: str
        location: str
        name: str
        properties: DnsForwardingRulesetProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: DnsForwardingRulesetProperties, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.dnsresolver.models.DnsForwardingRulesetPatch(_Model):
        dns_resolver_outbound_endpoints: Optional[list[SubResource]]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                dns_resolver_outbound_endpoints: Optional[list[SubResource]] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dnsresolver.models.DnsForwardingRulesetProperties(_Model):
        dns_resolver_outbound_endpoints: list[SubResource]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        resource_guid: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                dns_resolver_outbound_endpoints: list[SubResource]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dnsresolver.models.DnsResolver(TrackedResource):
        etag: Optional[str]
        id: str
        location: str
        name: str
        properties: DnsResolverProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: DnsResolverProperties, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.dnsresolver.models.DnsResolverDomainList(TrackedResource):
        etag: Optional[str]
        id: str
        location: str
        name: str
        properties: Optional[DnsResolverDomainListProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[DnsResolverDomainListProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.dnsresolver.models.DnsResolverDomainListBulk(_Model):
        properties: DnsResolverDomainListBulkProperties

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: DnsResolverDomainListBulkProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.dnsresolver.models.DnsResolverDomainListBulkProperties(_Model):
        action: Union[str, Action]
        storage_url: str

        @overload
        def __init__(
                self, 
                *, 
                action: Union[str, Action], 
                storage_url: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dnsresolver.models.DnsResolverDomainListPatch(_Model):
        properties: Optional[DnsResolverDomainListPatchProperties]
        tags: Optional[dict[str, str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[DnsResolverDomainListPatchProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.dnsresolver.models.DnsResolverDomainListPatchProperties(_Model):
        domains: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                domains: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dnsresolver.models.DnsResolverDomainListProperties(_Model):
        domains: Optional[list[str]]
        domains_url: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        resource_guid: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                domains: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dnsresolver.models.DnsResolverPatch(_Model):
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dnsresolver.models.DnsResolverPolicy(TrackedResource):
        etag: Optional[str]
        id: str
        location: str
        name: str
        properties: Optional[DnsResolverPolicyProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[DnsResolverPolicyProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.dnsresolver.models.DnsResolverPolicyPatch(_Model):
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dnsresolver.models.DnsResolverPolicyProperties(_Model):
        provisioning_state: Optional[Union[str, ProvisioningState]]
        resource_guid: Optional[str]


    class azure.mgmt.dnsresolver.models.DnsResolverPolicyVirtualNetworkLink(TrackedResource):
        etag: Optional[str]
        id: str
        location: str
        name: str
        properties: DnsResolverPolicyVirtualNetworkLinkProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: DnsResolverPolicyVirtualNetworkLinkProperties, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.dnsresolver.models.DnsResolverPolicyVirtualNetworkLinkPatch(_Model):
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dnsresolver.models.DnsResolverPolicyVirtualNetworkLinkProperties(_Model):
        provisioning_state: Optional[Union[str, ProvisioningState]]
        virtual_network: SubResource

        @overload
        def __init__(
                self, 
                *, 
                virtual_network: SubResource
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dnsresolver.models.DnsResolverProperties(_Model):
        dns_resolver_state: Optional[Union[str, DnsResolverState]]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        resource_guid: Optional[str]
        virtual_network: SubResource

        @overload
        def __init__(
                self, 
                *, 
                virtual_network: SubResource
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dnsresolver.models.DnsResolverState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONNECTED = "Connected"
        DISCONNECTED = "Disconnected"


    class azure.mgmt.dnsresolver.models.DnsSecurityRule(TrackedResource):
        etag: Optional[str]
        id: str
        location: str
        name: str
        properties: DnsSecurityRuleProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: DnsSecurityRuleProperties, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.dnsresolver.models.DnsSecurityRuleAction(_Model):
        action_type: Optional[Union[str, ActionType]]

        @overload
        def __init__(
                self, 
                *, 
                action_type: Optional[Union[str, ActionType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dnsresolver.models.DnsSecurityRulePatch(_Model):
        properties: Optional[DnsSecurityRulePatchProperties]
        tags: Optional[dict[str, str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[DnsSecurityRulePatchProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.dnsresolver.models.DnsSecurityRulePatchProperties(_Model):
        action: Optional[DnsSecurityRuleAction]
        dns_resolver_domain_lists: Optional[list[SubResource]]
        dns_security_rule_state: Optional[Union[str, DnsSecurityRuleState]]
        managed_domain_lists: Optional[list[Union[str, ManagedDomainList]]]
        priority: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                action: Optional[DnsSecurityRuleAction] = ..., 
                dns_resolver_domain_lists: Optional[list[SubResource]] = ..., 
                dns_security_rule_state: Optional[Union[str, DnsSecurityRuleState]] = ..., 
                managed_domain_lists: Optional[list[Union[str, ManagedDomainList]]] = ..., 
                priority: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dnsresolver.models.DnsSecurityRuleProperties(_Model):
        action: DnsSecurityRuleAction
        dns_resolver_domain_lists: Optional[list[SubResource]]
        dns_security_rule_state: Optional[Union[str, DnsSecurityRuleState]]
        managed_domain_lists: Optional[list[Union[str, ManagedDomainList]]]
        priority: int
        provisioning_state: Optional[Union[str, ProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                action: DnsSecurityRuleAction, 
                dns_resolver_domain_lists: Optional[list[SubResource]] = ..., 
                dns_security_rule_state: Optional[Union[str, DnsSecurityRuleState]] = ..., 
                managed_domain_lists: Optional[list[Union[str, ManagedDomainList]]] = ..., 
                priority: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dnsresolver.models.DnsSecurityRuleState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.dnsresolver.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.dnsresolver.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.dnsresolver.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dnsresolver.models.ForwardingRule(ProxyResource):
        etag: Optional[str]
        id: str
        name: str
        properties: ForwardingRuleProperties
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: ForwardingRuleProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.dnsresolver.models.ForwardingRulePatch(_Model):
        properties: Optional[ForwardingRulePatchProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ForwardingRulePatchProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.dnsresolver.models.ForwardingRulePatchProperties(_Model):
        forwarding_rule_state: Optional[Union[str, ForwardingRuleState]]
        metadata: Optional[dict[str, str]]
        target_dns_servers: Optional[list[TargetDnsServer]]

        @overload
        def __init__(
                self, 
                *, 
                forwarding_rule_state: Optional[Union[str, ForwardingRuleState]] = ..., 
                metadata: Optional[dict[str, str]] = ..., 
                target_dns_servers: Optional[list[TargetDnsServer]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dnsresolver.models.ForwardingRuleProperties(_Model):
        domain_name: str
        forwarding_rule_state: Optional[Union[str, ForwardingRuleState]]
        metadata: Optional[dict[str, str]]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        target_dns_servers: list[TargetDnsServer]

        @overload
        def __init__(
                self, 
                *, 
                domain_name: str, 
                forwarding_rule_state: Optional[Union[str, ForwardingRuleState]] = ..., 
                metadata: Optional[dict[str, str]] = ..., 
                target_dns_servers: list[TargetDnsServer]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dnsresolver.models.ForwardingRuleState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.dnsresolver.models.InboundEndpoint(TrackedResource):
        etag: Optional[str]
        id: str
        location: str
        name: str
        properties: InboundEndpointProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: InboundEndpointProperties, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.dnsresolver.models.InboundEndpointPatch(_Model):
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dnsresolver.models.InboundEndpointProperties(_Model):
        ip_configurations: list[IpConfiguration]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        resource_guid: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                ip_configurations: list[IpConfiguration]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dnsresolver.models.IpAllocationMethod(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DYNAMIC = "Dynamic"
        STATIC = "Static"


    class azure.mgmt.dnsresolver.models.IpConfiguration(_Model):
        private_ip_address: Optional[str]
        private_ip_allocation_method: Optional[Union[str, IpAllocationMethod]]
        subnet: SubResource

        @overload
        def __init__(
                self, 
                *, 
                private_ip_address: Optional[str] = ..., 
                private_ip_allocation_method: Optional[Union[str, IpAllocationMethod]] = ..., 
                subnet: SubResource
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dnsresolver.models.ManagedDomainList(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_DNS_THREAT_INTEL = "AzureDnsThreatIntel"


    class azure.mgmt.dnsresolver.models.OutboundEndpoint(TrackedResource):
        etag: Optional[str]
        id: str
        location: str
        name: str
        properties: OutboundEndpointProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: OutboundEndpointProperties, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.dnsresolver.models.OutboundEndpointPatch(_Model):
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dnsresolver.models.OutboundEndpointProperties(_Model):
        provisioning_state: Optional[Union[str, ProvisioningState]]
        resource_guid: Optional[str]
        subnet: SubResource

        @overload
        def __init__(
                self, 
                *, 
                subnet: SubResource
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dnsresolver.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.dnsresolver.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.dnsresolver.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.dnsresolver.models.SubResource(_Model):
        id: str

        @overload
        def __init__(
                self, 
                *, 
                id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dnsresolver.models.SystemData(_Model):
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


    class azure.mgmt.dnsresolver.models.TargetDnsServer(_Model):
        ip_address: str
        port: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                ip_address: str, 
                port: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dnsresolver.models.TrackedResource(Resource):
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


    class azure.mgmt.dnsresolver.models.VirtualNetworkDnsForwardingRuleset(_Model):
        id: Optional[str]
        properties: Optional[VirtualNetworkLinkSubResourceProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                properties: Optional[VirtualNetworkLinkSubResourceProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.dnsresolver.models.VirtualNetworkLink(ProxyResource):
        etag: Optional[str]
        id: str
        name: str
        properties: VirtualNetworkLinkProperties
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: VirtualNetworkLinkProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.dnsresolver.models.VirtualNetworkLinkPatch(_Model):
        properties: Optional[VirtualNetworkLinkPatchProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[VirtualNetworkLinkPatchProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.dnsresolver.models.VirtualNetworkLinkPatchProperties(_Model):
        metadata: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                metadata: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dnsresolver.models.VirtualNetworkLinkProperties(_Model):
        metadata: Optional[dict[str, str]]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        virtual_network: SubResource

        @overload
        def __init__(
                self, 
                *, 
                metadata: Optional[dict[str, str]] = ..., 
                virtual_network: SubResource
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dnsresolver.models.VirtualNetworkLinkSubResourceProperties(_Model):
        virtual_network_link: Optional[SubResource]

        @overload
        def __init__(
                self, 
                *, 
                virtual_network_link: Optional[SubResource] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


namespace azure.mgmt.dnsresolver.operations

    class azure.mgmt.dnsresolver.operations.DnsForwardingRulesetsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                dns_forwarding_ruleset_name: str, 
                parameters: DnsForwardingRuleset, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[DnsForwardingRuleset]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                dns_forwarding_ruleset_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[DnsForwardingRuleset]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                dns_forwarding_ruleset_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[DnsForwardingRuleset]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                dns_forwarding_ruleset_name: str, 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                dns_forwarding_ruleset_name: str, 
                parameters: DnsForwardingRulesetPatch, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[DnsForwardingRuleset]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                dns_forwarding_ruleset_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[DnsForwardingRuleset]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                dns_forwarding_ruleset_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[DnsForwardingRuleset]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                dns_forwarding_ruleset_name: str, 
                **kwargs: Any
            ) -> DnsForwardingRuleset: ...

        @distributed_trace
        def list(
                self, 
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[DnsForwardingRuleset]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[DnsForwardingRuleset]: ...

        @distributed_trace
        def list_by_virtual_network(
                self, 
                resource_group_name: str, 
                virtual_network_name: str, 
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[VirtualNetworkDnsForwardingRuleset]: ...


    class azure.mgmt.dnsresolver.operations.DnsResolverDomainListsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_bulk(
                self, 
                resource_group_name: str, 
                dns_resolver_domain_list_name: str, 
                parameters: DnsResolverDomainListBulk, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[DnsResolverDomainList]: ...

        @overload
        def begin_bulk(
                self, 
                resource_group_name: str, 
                dns_resolver_domain_list_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[DnsResolverDomainList]: ...

        @overload
        def begin_bulk(
                self, 
                resource_group_name: str, 
                dns_resolver_domain_list_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[DnsResolverDomainList]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                dns_resolver_domain_list_name: str, 
                parameters: DnsResolverDomainList, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[DnsResolverDomainList]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                dns_resolver_domain_list_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[DnsResolverDomainList]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                dns_resolver_domain_list_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[DnsResolverDomainList]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                dns_resolver_domain_list_name: str, 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                dns_resolver_domain_list_name: str, 
                parameters: DnsResolverDomainListPatch, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[DnsResolverDomainList]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                dns_resolver_domain_list_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[DnsResolverDomainList]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                dns_resolver_domain_list_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[DnsResolverDomainList]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                dns_resolver_domain_list_name: str, 
                **kwargs: Any
            ) -> DnsResolverDomainList: ...

        @distributed_trace
        def list(
                self, 
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[DnsResolverDomainList]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[DnsResolverDomainList]: ...


    class azure.mgmt.dnsresolver.operations.DnsResolverPoliciesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                dns_resolver_policy_name: str, 
                parameters: DnsResolverPolicy, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[DnsResolverPolicy]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                dns_resolver_policy_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[DnsResolverPolicy]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                dns_resolver_policy_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[DnsResolverPolicy]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                dns_resolver_policy_name: str, 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                dns_resolver_policy_name: str, 
                parameters: DnsResolverPolicyPatch, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[DnsResolverPolicy]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                dns_resolver_policy_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[DnsResolverPolicy]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                dns_resolver_policy_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[DnsResolverPolicy]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                dns_resolver_policy_name: str, 
                **kwargs: Any
            ) -> DnsResolverPolicy: ...

        @distributed_trace
        def list(
                self, 
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[DnsResolverPolicy]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[DnsResolverPolicy]: ...

        @distributed_trace
        def list_by_virtual_network(
                self, 
                resource_group_name: str, 
                virtual_network_name: str, 
                **kwargs: Any
            ) -> ItemPaged[SubResource]: ...


    class azure.mgmt.dnsresolver.operations.DnsResolverPolicyVirtualNetworkLinksOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                dns_resolver_policy_name: str, 
                dns_resolver_policy_virtual_network_link_name: str, 
                parameters: DnsResolverPolicyVirtualNetworkLink, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[DnsResolverPolicyVirtualNetworkLink]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                dns_resolver_policy_name: str, 
                dns_resolver_policy_virtual_network_link_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[DnsResolverPolicyVirtualNetworkLink]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                dns_resolver_policy_name: str, 
                dns_resolver_policy_virtual_network_link_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[DnsResolverPolicyVirtualNetworkLink]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                dns_resolver_policy_name: str, 
                dns_resolver_policy_virtual_network_link_name: str, 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                dns_resolver_policy_name: str, 
                dns_resolver_policy_virtual_network_link_name: str, 
                parameters: DnsResolverPolicyVirtualNetworkLinkPatch, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[DnsResolverPolicyVirtualNetworkLink]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                dns_resolver_policy_name: str, 
                dns_resolver_policy_virtual_network_link_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[DnsResolverPolicyVirtualNetworkLink]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                dns_resolver_policy_name: str, 
                dns_resolver_policy_virtual_network_link_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[DnsResolverPolicyVirtualNetworkLink]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                dns_resolver_policy_name: str, 
                dns_resolver_policy_virtual_network_link_name: str, 
                **kwargs: Any
            ) -> DnsResolverPolicyVirtualNetworkLink: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                dns_resolver_policy_name: str, 
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[DnsResolverPolicyVirtualNetworkLink]: ...


    class azure.mgmt.dnsresolver.operations.DnsResolversOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                dns_resolver_name: str, 
                parameters: DnsResolver, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[DnsResolver]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                dns_resolver_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[DnsResolver]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                dns_resolver_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[DnsResolver]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                dns_resolver_name: str, 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                dns_resolver_name: str, 
                parameters: DnsResolverPatch, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[DnsResolver]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                dns_resolver_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[DnsResolver]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                dns_resolver_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[DnsResolver]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                dns_resolver_name: str, 
                **kwargs: Any
            ) -> DnsResolver: ...

        @distributed_trace
        def list(
                self, 
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[DnsResolver]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[DnsResolver]: ...

        @distributed_trace
        def list_by_virtual_network(
                self, 
                resource_group_name: str, 
                virtual_network_name: str, 
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[SubResource]: ...


    class azure.mgmt.dnsresolver.operations.DnsSecurityRulesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                dns_resolver_policy_name: str, 
                dns_security_rule_name: str, 
                parameters: DnsSecurityRule, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[DnsSecurityRule]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                dns_resolver_policy_name: str, 
                dns_security_rule_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[DnsSecurityRule]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                dns_resolver_policy_name: str, 
                dns_security_rule_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[DnsSecurityRule]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                dns_resolver_policy_name: str, 
                dns_security_rule_name: str, 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                dns_resolver_policy_name: str, 
                dns_security_rule_name: str, 
                parameters: DnsSecurityRulePatch, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[DnsSecurityRule]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                dns_resolver_policy_name: str, 
                dns_security_rule_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[DnsSecurityRule]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                dns_resolver_policy_name: str, 
                dns_security_rule_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[DnsSecurityRule]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                dns_resolver_policy_name: str, 
                dns_security_rule_name: str, 
                **kwargs: Any
            ) -> DnsSecurityRule: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                dns_resolver_policy_name: str, 
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[DnsSecurityRule]: ...


    class azure.mgmt.dnsresolver.operations.ForwardingRulesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                dns_forwarding_ruleset_name: str, 
                forwarding_rule_name: str, 
                parameters: ForwardingRule, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> ForwardingRule: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                dns_forwarding_ruleset_name: str, 
                forwarding_rule_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> ForwardingRule: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                dns_forwarding_ruleset_name: str, 
                forwarding_rule_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> ForwardingRule: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                dns_forwarding_ruleset_name: str, 
                forwarding_rule_name: str, 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                dns_forwarding_ruleset_name: str, 
                forwarding_rule_name: str, 
                **kwargs: Any
            ) -> ForwardingRule: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                dns_forwarding_ruleset_name: str, 
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[ForwardingRule]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                dns_forwarding_ruleset_name: str, 
                forwarding_rule_name: str, 
                parameters: ForwardingRulePatch, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> ForwardingRule: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                dns_forwarding_ruleset_name: str, 
                forwarding_rule_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> ForwardingRule: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                dns_forwarding_ruleset_name: str, 
                forwarding_rule_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> ForwardingRule: ...


    class azure.mgmt.dnsresolver.operations.InboundEndpointsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                dns_resolver_name: str, 
                inbound_endpoint_name: str, 
                parameters: InboundEndpoint, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[InboundEndpoint]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                dns_resolver_name: str, 
                inbound_endpoint_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[InboundEndpoint]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                dns_resolver_name: str, 
                inbound_endpoint_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[InboundEndpoint]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                dns_resolver_name: str, 
                inbound_endpoint_name: str, 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                dns_resolver_name: str, 
                inbound_endpoint_name: str, 
                parameters: InboundEndpointPatch, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[InboundEndpoint]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                dns_resolver_name: str, 
                inbound_endpoint_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[InboundEndpoint]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                dns_resolver_name: str, 
                inbound_endpoint_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[InboundEndpoint]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                dns_resolver_name: str, 
                inbound_endpoint_name: str, 
                **kwargs: Any
            ) -> InboundEndpoint: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                dns_resolver_name: str, 
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[InboundEndpoint]: ...


    class azure.mgmt.dnsresolver.operations.OutboundEndpointsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                dns_resolver_name: str, 
                outbound_endpoint_name: str, 
                parameters: OutboundEndpoint, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[OutboundEndpoint]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                dns_resolver_name: str, 
                outbound_endpoint_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[OutboundEndpoint]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                dns_resolver_name: str, 
                outbound_endpoint_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[OutboundEndpoint]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                dns_resolver_name: str, 
                outbound_endpoint_name: str, 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                dns_resolver_name: str, 
                outbound_endpoint_name: str, 
                parameters: OutboundEndpointPatch, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[OutboundEndpoint]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                dns_resolver_name: str, 
                outbound_endpoint_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[OutboundEndpoint]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                dns_resolver_name: str, 
                outbound_endpoint_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[OutboundEndpoint]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                dns_resolver_name: str, 
                outbound_endpoint_name: str, 
                **kwargs: Any
            ) -> OutboundEndpoint: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                dns_resolver_name: str, 
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[OutboundEndpoint]: ...


    class azure.mgmt.dnsresolver.operations.VirtualNetworkLinksOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                dns_forwarding_ruleset_name: str, 
                virtual_network_link_name: str, 
                parameters: VirtualNetworkLink, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[VirtualNetworkLink]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                dns_forwarding_ruleset_name: str, 
                virtual_network_link_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[VirtualNetworkLink]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                dns_forwarding_ruleset_name: str, 
                virtual_network_link_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[VirtualNetworkLink]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                dns_forwarding_ruleset_name: str, 
                virtual_network_link_name: str, 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                dns_forwarding_ruleset_name: str, 
                virtual_network_link_name: str, 
                parameters: VirtualNetworkLinkPatch, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[VirtualNetworkLink]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                dns_forwarding_ruleset_name: str, 
                virtual_network_link_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[VirtualNetworkLink]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                dns_forwarding_ruleset_name: str, 
                virtual_network_link_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[VirtualNetworkLink]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                dns_forwarding_ruleset_name: str, 
                virtual_network_link_name: str, 
                **kwargs: Any
            ) -> VirtualNetworkLink: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                dns_forwarding_ruleset_name: str, 
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[VirtualNetworkLink]: ...


```