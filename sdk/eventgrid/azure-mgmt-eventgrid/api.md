```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.eventgrid

    class azure.mgmt.eventgrid.EventGridManagementClient: implements ContextManager 
        ca_certificates: CaCertificatesOperations
        channels: ChannelsOperations
        client_groups: ClientGroupsOperations
        clients: ClientsOperations
        domain_event_subscriptions: DomainEventSubscriptionsOperations
        domain_topic_event_subscriptions: DomainTopicEventSubscriptionsOperations
        domain_topics: DomainTopicsOperations
        domains: DomainsOperations
        event_subscriptions: EventSubscriptionsOperations
        extension_topics: ExtensionTopicsOperations
        namespace_topic_event_subscriptions: NamespaceTopicEventSubscriptionsOperations
        namespace_topics: NamespaceTopicsOperations
        namespaces: NamespacesOperations
        network_security_perimeter_configurations: NetworkSecurityPerimeterConfigurationsOperations
        operations: Operations
        partner_configurations: PartnerConfigurationsOperations
        partner_destinations: PartnerDestinationsOperations
        partner_namespaces: PartnerNamespacesOperations
        partner_registrations: PartnerRegistrationsOperations
        partner_topic_event_subscriptions: PartnerTopicEventSubscriptionsOperations
        partner_topics: PartnerTopicsOperations
        permission_bindings: PermissionBindingsOperations
        private_endpoint_connections: PrivateEndpointConnectionsOperations
        private_link_resources: PrivateLinkResourcesOperations
        system_topic_event_subscriptions: SystemTopicEventSubscriptionsOperations
        system_topics: SystemTopicsOperations
        topic_event_subscriptions: TopicEventSubscriptionsOperations
        topic_spaces: TopicSpacesOperations
        topic_types: TopicTypesOperations
        topics: TopicsOperations
        verified_partners: VerifiedPartnersOperations

        def __init__(
                self, 
                credential: TokenCredential, 
                subscription_id: str, 
                base_url: Optional[str] = None, 
                *, 
                api_version: str = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def close(self) -> None: ...


namespace azure.mgmt.eventgrid.aio

    class azure.mgmt.eventgrid.aio.EventGridManagementClient: implements AsyncContextManager 
        ca_certificates: CaCertificatesOperations
        channels: ChannelsOperations
        client_groups: ClientGroupsOperations
        clients: ClientsOperations
        domain_event_subscriptions: DomainEventSubscriptionsOperations
        domain_topic_event_subscriptions: DomainTopicEventSubscriptionsOperations
        domain_topics: DomainTopicsOperations
        domains: DomainsOperations
        event_subscriptions: EventSubscriptionsOperations
        extension_topics: ExtensionTopicsOperations
        namespace_topic_event_subscriptions: NamespaceTopicEventSubscriptionsOperations
        namespace_topics: NamespaceTopicsOperations
        namespaces: NamespacesOperations
        network_security_perimeter_configurations: NetworkSecurityPerimeterConfigurationsOperations
        operations: Operations
        partner_configurations: PartnerConfigurationsOperations
        partner_destinations: PartnerDestinationsOperations
        partner_namespaces: PartnerNamespacesOperations
        partner_registrations: PartnerRegistrationsOperations
        partner_topic_event_subscriptions: PartnerTopicEventSubscriptionsOperations
        partner_topics: PartnerTopicsOperations
        permission_bindings: PermissionBindingsOperations
        private_endpoint_connections: PrivateEndpointConnectionsOperations
        private_link_resources: PrivateLinkResourcesOperations
        system_topic_event_subscriptions: SystemTopicEventSubscriptionsOperations
        system_topics: SystemTopicsOperations
        topic_event_subscriptions: TopicEventSubscriptionsOperations
        topic_spaces: TopicSpacesOperations
        topic_types: TopicTypesOperations
        topics: TopicsOperations
        verified_partners: VerifiedPartnersOperations

        def __init__(
                self, 
                credential: AsyncTokenCredential, 
                subscription_id: str, 
                base_url: Optional[str] = None, 
                *, 
                api_version: str = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        async def close(self) -> None: ...


namespace azure.mgmt.eventgrid.aio.operations

    class azure.mgmt.eventgrid.aio.operations.CaCertificatesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                ca_certificate_name: str, 
                ca_certificate_info: CaCertificate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CaCertificate]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                ca_certificate_name: str, 
                ca_certificate_info: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CaCertificate]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                ca_certificate_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                ca_certificate_name: str, 
                **kwargs: Any
            ) -> CaCertificate: ...

        @distributed_trace
        def list_by_namespace(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[CaCertificate]: ...


    class azure.mgmt.eventgrid.aio.operations.ChannelsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                partner_namespace_name: str, 
                channel_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                partner_namespace_name: str, 
                channel_name: str, 
                channel_info: Channel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Channel: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                partner_namespace_name: str, 
                channel_name: str, 
                channel_info: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Channel: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                partner_namespace_name: str, 
                channel_name: str, 
                **kwargs: Any
            ) -> Channel: ...

        @distributed_trace_async
        async def get_full_url(
                self, 
                resource_group_name: str, 
                partner_namespace_name: str, 
                channel_name: str, 
                **kwargs: Any
            ) -> EventSubscriptionFullUrl: ...

        @distributed_trace
        def list_by_partner_namespace(
                self, 
                resource_group_name: str, 
                partner_namespace_name: str, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[Channel]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                partner_namespace_name: str, 
                channel_name: str, 
                channel_update_parameters: ChannelUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                partner_namespace_name: str, 
                channel_name: str, 
                channel_update_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.eventgrid.aio.operations.ClientGroupsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                client_group_name: str, 
                client_group_info: ClientGroup, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ClientGroup]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                client_group_name: str, 
                client_group_info: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ClientGroup]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                client_group_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                client_group_name: str, 
                **kwargs: Any
            ) -> ClientGroup: ...

        @distributed_trace
        def list_by_namespace(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[ClientGroup]: ...


    class azure.mgmt.eventgrid.aio.operations.ClientsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                client_name: str, 
                client_info: Client, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Client]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                client_name: str, 
                client_info: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Client]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                client_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                client_name: str, 
                **kwargs: Any
            ) -> Client: ...

        @distributed_trace
        def list_by_namespace(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[Client]: ...


    class azure.mgmt.eventgrid.aio.operations.DomainEventSubscriptionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                event_subscription_name: str, 
                event_subscription_info: EventSubscription, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EventSubscription]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                event_subscription_name: str, 
                event_subscription_info: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EventSubscription]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                event_subscription_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                event_subscription_name: str, 
                event_subscription_update_parameters: EventSubscriptionUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EventSubscription]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                event_subscription_name: str, 
                event_subscription_update_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EventSubscription]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                event_subscription_name: str, 
                **kwargs: Any
            ) -> EventSubscription: ...

        @distributed_trace_async
        async def get_delivery_attributes(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                event_subscription_name: str, 
                **kwargs: Any
            ) -> DeliveryAttributeListResult: ...

        @distributed_trace_async
        async def get_full_url(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                event_subscription_name: str, 
                **kwargs: Any
            ) -> EventSubscriptionFullUrl: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[EventSubscription]: ...


    class azure.mgmt.eventgrid.aio.operations.DomainTopicEventSubscriptionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                topic_name: str, 
                event_subscription_name: str, 
                event_subscription_info: EventSubscription, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EventSubscription]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                topic_name: str, 
                event_subscription_name: str, 
                event_subscription_info: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EventSubscription]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                topic_name: str, 
                event_subscription_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                topic_name: str, 
                event_subscription_name: str, 
                event_subscription_update_parameters: EventSubscriptionUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EventSubscription]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                topic_name: str, 
                event_subscription_name: str, 
                event_subscription_update_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EventSubscription]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                topic_name: str, 
                event_subscription_name: str, 
                **kwargs: Any
            ) -> EventSubscription: ...

        @distributed_trace_async
        async def get_delivery_attributes(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                topic_name: str, 
                event_subscription_name: str, 
                **kwargs: Any
            ) -> DeliveryAttributeListResult: ...

        @distributed_trace_async
        async def get_full_url(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                topic_name: str, 
                event_subscription_name: str, 
                **kwargs: Any
            ) -> EventSubscriptionFullUrl: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                topic_name: str, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[EventSubscription]: ...


    class azure.mgmt.eventgrid.aio.operations.DomainTopicsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                domain_topic_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[DomainTopic]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                domain_topic_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                domain_topic_name: str, 
                **kwargs: Any
            ) -> DomainTopic: ...

        @distributed_trace
        def list_by_domain(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[DomainTopic]: ...


    class azure.mgmt.eventgrid.aio.operations.DomainsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                domain_info: Domain, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Domain]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                domain_info: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Domain]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                domain_update_parameters: DomainUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Domain]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                domain_update_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Domain]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                **kwargs: Any
            ) -> Domain: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[Domain]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[Domain]: ...

        @distributed_trace_async
        async def list_shared_access_keys(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                **kwargs: Any
            ) -> DomainSharedAccessKeys: ...

        @overload
        async def regenerate_key(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                regenerate_key_request: DomainRegenerateKeyRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DomainSharedAccessKeys: ...

        @overload
        async def regenerate_key(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                regenerate_key_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DomainSharedAccessKeys: ...


    class azure.mgmt.eventgrid.aio.operations.EventSubscriptionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                scope: str, 
                event_subscription_name: str, 
                event_subscription_info: EventSubscription, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EventSubscription]: ...

        @overload
        async def begin_create_or_update(
                self, 
                scope: str, 
                event_subscription_name: str, 
                event_subscription_info: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EventSubscription]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                scope: str, 
                event_subscription_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                scope: str, 
                event_subscription_name: str, 
                event_subscription_update_parameters: EventSubscriptionUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EventSubscription]: ...

        @overload
        async def begin_update(
                self, 
                scope: str, 
                event_subscription_name: str, 
                event_subscription_update_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EventSubscription]: ...

        @distributed_trace_async
        async def get(
                self, 
                scope: str, 
                event_subscription_name: str, 
                **kwargs: Any
            ) -> EventSubscription: ...

        @distributed_trace_async
        async def get_delivery_attributes(
                self, 
                scope: str, 
                event_subscription_name: str, 
                **kwargs: Any
            ) -> DeliveryAttributeListResult: ...

        @distributed_trace_async
        async def get_full_url(
                self, 
                scope: str, 
                event_subscription_name: str, 
                **kwargs: Any
            ) -> EventSubscriptionFullUrl: ...

        @distributed_trace
        def list_by_domain_topic(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                topic_name: str, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[EventSubscription]: ...

        @distributed_trace
        def list_by_resource(
                self, 
                resource_group_name: str, 
                provider_namespace: str, 
                resource_type_name: str, 
                resource_name: str, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[EventSubscription]: ...

        @distributed_trace
        def list_global_by_resource_group(
                self, 
                resource_group_name: str, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[EventSubscription]: ...

        @distributed_trace
        def list_global_by_resource_group_for_topic_type(
                self, 
                resource_group_name: str, 
                topic_type_name: str, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[EventSubscription]: ...

        @distributed_trace
        def list_global_by_subscription(
                self, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[EventSubscription]: ...

        @distributed_trace
        def list_global_by_subscription_for_topic_type(
                self, 
                topic_type_name: str, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[EventSubscription]: ...

        @distributed_trace
        def list_regional_by_resource_group(
                self, 
                resource_group_name: str, 
                location: str, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[EventSubscription]: ...

        @distributed_trace
        def list_regional_by_resource_group_for_topic_type(
                self, 
                resource_group_name: str, 
                location: str, 
                topic_type_name: str, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[EventSubscription]: ...

        @distributed_trace
        def list_regional_by_subscription(
                self, 
                location: str, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[EventSubscription]: ...

        @distributed_trace
        def list_regional_by_subscription_for_topic_type(
                self, 
                location: str, 
                topic_type_name: str, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[EventSubscription]: ...


    class azure.mgmt.eventgrid.aio.operations.ExtensionTopicsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                scope: str, 
                **kwargs: Any
            ) -> ExtensionTopic: ...


    class azure.mgmt.eventgrid.aio.operations.NamespaceTopicEventSubscriptionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_name: str, 
                event_subscription_name: str, 
                event_subscription_info: Subscription, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Subscription]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_name: str, 
                event_subscription_name: str, 
                event_subscription_info: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Subscription]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_name: str, 
                event_subscription_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_name: str, 
                event_subscription_name: str, 
                event_subscription_update_parameters: SubscriptionUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Subscription]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_name: str, 
                event_subscription_name: str, 
                event_subscription_update_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Subscription]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_name: str, 
                event_subscription_name: str, 
                **kwargs: Any
            ) -> Subscription: ...

        @distributed_trace_async
        async def get_delivery_attributes(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_name: str, 
                event_subscription_name: str, 
                **kwargs: Any
            ) -> DeliveryAttributeListResult: ...

        @distributed_trace_async
        async def get_full_url(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_name: str, 
                event_subscription_name: str, 
                **kwargs: Any
            ) -> SubscriptionFullUrl: ...

        @distributed_trace
        def list_by_namespace_topic(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_name: str, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[Subscription]: ...


    class azure.mgmt.eventgrid.aio.operations.NamespaceTopicsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_name: str, 
                namespace_topic_info: NamespaceTopic, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NamespaceTopic]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_name: str, 
                namespace_topic_info: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NamespaceTopic]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_regenerate_key(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_name: str, 
                regenerate_key_request: TopicRegenerateKeyRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[TopicSharedAccessKeys]: ...

        @overload
        async def begin_regenerate_key(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_name: str, 
                regenerate_key_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[TopicSharedAccessKeys]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_name: str, 
                namespace_topic_update_parameters: NamespaceTopicUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NamespaceTopic]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_name: str, 
                namespace_topic_update_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NamespaceTopic]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_name: str, 
                **kwargs: Any
            ) -> NamespaceTopic: ...

        @distributed_trace
        def list_by_namespace(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[NamespaceTopic]: ...

        @distributed_trace_async
        async def list_shared_access_keys(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_name: str, 
                **kwargs: Any
            ) -> TopicSharedAccessKeys: ...


    class azure.mgmt.eventgrid.aio.operations.NamespacesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                namespace_info: Namespace, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Namespace]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                namespace_info: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Namespace]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_regenerate_key(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                regenerate_key_request: NamespaceRegenerateKeyRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NamespaceSharedAccessKeys]: ...

        @overload
        async def begin_regenerate_key(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                regenerate_key_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NamespaceSharedAccessKeys]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                namespace_update_parameters: NamespaceUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Namespace]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                namespace_update_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Namespace]: ...

        @distributed_trace_async
        async def begin_validate_custom_domain_ownership(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[CustomDomainOwnershipValidationResult]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                **kwargs: Any
            ) -> Namespace: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[Namespace]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[Namespace]: ...

        @distributed_trace_async
        async def list_shared_access_keys(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                **kwargs: Any
            ) -> NamespaceSharedAccessKeys: ...


    class azure.mgmt.eventgrid.aio.operations.NetworkSecurityPerimeterConfigurationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_reconcile(
                self, 
                resource_group_name: str, 
                resource_type: Union[str, NetworkSecurityPerimeterResourceType], 
                resource_name: str, 
                perimeter_guid: str, 
                association_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkSecurityPerimeterConfiguration]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                resource_type: Union[str, NetworkSecurityPerimeterResourceType], 
                resource_name: str, 
                perimeter_guid: str, 
                association_name: str, 
                **kwargs: Any
            ) -> NetworkSecurityPerimeterConfiguration: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                resource_type: Union[str, NetworkSecurityPerimeterResourceType], 
                resource_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[NetworkSecurityPerimeterConfiguration]: ...


    class azure.mgmt.eventgrid.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


    class azure.mgmt.eventgrid.aio.operations.PartnerConfigurationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def authorize_partner(
                self, 
                resource_group_name: str, 
                partner_info: Partner, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PartnerConfiguration: ...

        @overload
        async def authorize_partner(
                self, 
                resource_group_name: str, 
                partner_info: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PartnerConfiguration: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                partner_configuration_info: PartnerConfiguration, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PartnerConfiguration]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                partner_configuration_info: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PartnerConfiguration]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                partner_configuration_update_parameters: PartnerConfigurationUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PartnerConfiguration]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                partner_configuration_update_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PartnerConfiguration]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> PartnerConfiguration: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[PartnerConfiguration]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[PartnerConfiguration]: ...

        @overload
        async def unauthorize_partner(
                self, 
                resource_group_name: str, 
                partner_info: Partner, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PartnerConfiguration: ...

        @overload
        async def unauthorize_partner(
                self, 
                resource_group_name: str, 
                partner_info: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PartnerConfiguration: ...


    class azure.mgmt.eventgrid.aio.operations.PartnerDestinationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def activate(
                self, 
                resource_group_name: str, 
                partner_destination_name: str, 
                **kwargs: Any
            ) -> PartnerDestination: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                partner_destination_name: str, 
                partner_destination: PartnerDestination, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PartnerDestination]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                partner_destination_name: str, 
                partner_destination: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PartnerDestination]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                partner_destination_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                partner_destination_name: str, 
                partner_destination_update_parameters: PartnerDestinationUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PartnerDestination]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                partner_destination_name: str, 
                partner_destination_update_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PartnerDestination]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                partner_destination_name: str, 
                **kwargs: Any
            ) -> PartnerDestination: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[PartnerDestination]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[PartnerDestination]: ...


    class azure.mgmt.eventgrid.aio.operations.PartnerNamespacesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                partner_namespace_name: str, 
                partner_namespace_info: PartnerNamespace, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PartnerNamespace]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                partner_namespace_name: str, 
                partner_namespace_info: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PartnerNamespace]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                partner_namespace_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                partner_namespace_name: str, 
                partner_namespace_update_parameters: PartnerNamespaceUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PartnerNamespace]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                partner_namespace_name: str, 
                partner_namespace_update_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PartnerNamespace]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                partner_namespace_name: str, 
                **kwargs: Any
            ) -> PartnerNamespace: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[PartnerNamespace]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[PartnerNamespace]: ...

        @distributed_trace_async
        async def list_shared_access_keys(
                self, 
                resource_group_name: str, 
                partner_namespace_name: str, 
                **kwargs: Any
            ) -> PartnerNamespaceSharedAccessKeys: ...

        @overload
        async def regenerate_key(
                self, 
                resource_group_name: str, 
                partner_namespace_name: str, 
                regenerate_key_request: PartnerNamespaceRegenerateKeyRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PartnerNamespaceSharedAccessKeys: ...

        @overload
        async def regenerate_key(
                self, 
                resource_group_name: str, 
                partner_namespace_name: str, 
                regenerate_key_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PartnerNamespaceSharedAccessKeys: ...


    class azure.mgmt.eventgrid.aio.operations.PartnerRegistrationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                partner_registration_name: str, 
                partner_registration_info: PartnerRegistration, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PartnerRegistration]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                partner_registration_name: str, 
                partner_registration_info: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PartnerRegistration]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                partner_registration_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                partner_registration_name: str, 
                partner_registration_update_parameters: PartnerRegistrationUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PartnerRegistration]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                partner_registration_name: str, 
                partner_registration_update_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PartnerRegistration]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                partner_registration_name: str, 
                **kwargs: Any
            ) -> PartnerRegistration: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[PartnerRegistration]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[PartnerRegistration]: ...


    class azure.mgmt.eventgrid.aio.operations.PartnerTopicEventSubscriptionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                partner_topic_name: str, 
                event_subscription_name: str, 
                event_subscription_info: EventSubscription, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EventSubscription]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                partner_topic_name: str, 
                event_subscription_name: str, 
                event_subscription_info: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EventSubscription]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                partner_topic_name: str, 
                event_subscription_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                partner_topic_name: str, 
                event_subscription_name: str, 
                event_subscription_update_parameters: EventSubscriptionUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EventSubscription]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                partner_topic_name: str, 
                event_subscription_name: str, 
                event_subscription_update_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EventSubscription]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                partner_topic_name: str, 
                event_subscription_name: str, 
                **kwargs: Any
            ) -> EventSubscription: ...

        @distributed_trace_async
        async def get_delivery_attributes(
                self, 
                resource_group_name: str, 
                partner_topic_name: str, 
                event_subscription_name: str, 
                **kwargs: Any
            ) -> DeliveryAttributeListResult: ...

        @distributed_trace_async
        async def get_full_url(
                self, 
                resource_group_name: str, 
                partner_topic_name: str, 
                event_subscription_name: str, 
                **kwargs: Any
            ) -> EventSubscriptionFullUrl: ...

        @distributed_trace
        def list_by_partner_topic(
                self, 
                resource_group_name: str, 
                partner_topic_name: str, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[EventSubscription]: ...


    class azure.mgmt.eventgrid.aio.operations.PartnerTopicsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def activate(
                self, 
                resource_group_name: str, 
                partner_topic_name: str, 
                **kwargs: Any
            ) -> PartnerTopic: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                partner_topic_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                partner_topic_name: str, 
                partner_topic_info: PartnerTopic, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PartnerTopic: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                partner_topic_name: str, 
                partner_topic_info: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PartnerTopic: ...

        @distributed_trace_async
        async def deactivate(
                self, 
                resource_group_name: str, 
                partner_topic_name: str, 
                **kwargs: Any
            ) -> PartnerTopic: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                partner_topic_name: str, 
                **kwargs: Any
            ) -> PartnerTopic: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[PartnerTopic]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[PartnerTopic]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                partner_topic_name: str, 
                partner_topic_update_parameters: PartnerTopicUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Optional[PartnerTopic]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                partner_topic_name: str, 
                partner_topic_update_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Optional[PartnerTopic]: ...


    class azure.mgmt.eventgrid.aio.operations.PermissionBindingsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                permission_binding_name: str, 
                permission_binding_info: PermissionBinding, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PermissionBinding]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                permission_binding_name: str, 
                permission_binding_info: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PermissionBinding]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                permission_binding_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                permission_binding_name: str, 
                **kwargs: Any
            ) -> PermissionBinding: ...

        @distributed_trace
        def list_by_namespace(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[PermissionBinding]: ...


    class azure.mgmt.eventgrid.aio.operations.PrivateEndpointConnectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                parent_type: Union[str, PrivateEndpointConnectionsParentType], 
                parent_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                parent_type: Union[str, PrivateEndpointConnectionsParentType], 
                parent_name: str, 
                private_endpoint_connection_name: str, 
                private_endpoint_connection: PrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateEndpointConnection]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                parent_type: Union[str, PrivateEndpointConnectionsParentType], 
                parent_name: str, 
                private_endpoint_connection_name: str, 
                private_endpoint_connection: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateEndpointConnection]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                parent_type: Union[str, PrivateEndpointConnectionsParentType], 
                parent_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @distributed_trace
        def list_by_resource(
                self, 
                resource_group_name: str, 
                parent_type: Union[str, PrivateEndpointConnectionsParentType], 
                parent_name: str, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[PrivateEndpointConnection]: ...


    class azure.mgmt.eventgrid.aio.operations.PrivateLinkResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                parent_type: str, 
                parent_name: str, 
                private_link_resource_name: str, 
                **kwargs: Any
            ) -> PrivateLinkResource: ...

        @distributed_trace
        def list_by_resource(
                self, 
                resource_group_name: str, 
                parent_type: str, 
                parent_name: str, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[PrivateLinkResource]: ...


    class azure.mgmt.eventgrid.aio.operations.SystemTopicEventSubscriptionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                system_topic_name: str, 
                event_subscription_name: str, 
                event_subscription_info: EventSubscription, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EventSubscription]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                system_topic_name: str, 
                event_subscription_name: str, 
                event_subscription_info: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EventSubscription]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                system_topic_name: str, 
                event_subscription_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                system_topic_name: str, 
                event_subscription_name: str, 
                event_subscription_update_parameters: EventSubscriptionUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EventSubscription]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                system_topic_name: str, 
                event_subscription_name: str, 
                event_subscription_update_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EventSubscription]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                system_topic_name: str, 
                event_subscription_name: str, 
                **kwargs: Any
            ) -> EventSubscription: ...

        @distributed_trace_async
        async def get_delivery_attributes(
                self, 
                resource_group_name: str, 
                system_topic_name: str, 
                event_subscription_name: str, 
                **kwargs: Any
            ) -> DeliveryAttributeListResult: ...

        @distributed_trace_async
        async def get_full_url(
                self, 
                resource_group_name: str, 
                system_topic_name: str, 
                event_subscription_name: str, 
                **kwargs: Any
            ) -> EventSubscriptionFullUrl: ...

        @distributed_trace
        def list_by_system_topic(
                self, 
                resource_group_name: str, 
                system_topic_name: str, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[EventSubscription]: ...


    class azure.mgmt.eventgrid.aio.operations.SystemTopicsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                system_topic_name: str, 
                system_topic_info: SystemTopic, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SystemTopic]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                system_topic_name: str, 
                system_topic_info: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SystemTopic]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                system_topic_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                system_topic_name: str, 
                system_topic_update_parameters: SystemTopicUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SystemTopic]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                system_topic_name: str, 
                system_topic_update_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SystemTopic]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                system_topic_name: str, 
                **kwargs: Any
            ) -> SystemTopic: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[SystemTopic]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[SystemTopic]: ...


    class azure.mgmt.eventgrid.aio.operations.TopicEventSubscriptionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                topic_name: str, 
                event_subscription_name: str, 
                event_subscription_info: EventSubscription, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EventSubscription]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                topic_name: str, 
                event_subscription_name: str, 
                event_subscription_info: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EventSubscription]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                topic_name: str, 
                event_subscription_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                topic_name: str, 
                event_subscription_name: str, 
                event_subscription_update_parameters: EventSubscriptionUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EventSubscription]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                topic_name: str, 
                event_subscription_name: str, 
                event_subscription_update_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EventSubscription]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                topic_name: str, 
                event_subscription_name: str, 
                **kwargs: Any
            ) -> EventSubscription: ...

        @distributed_trace_async
        async def get_delivery_attributes(
                self, 
                resource_group_name: str, 
                topic_name: str, 
                event_subscription_name: str, 
                **kwargs: Any
            ) -> DeliveryAttributeListResult: ...

        @distributed_trace_async
        async def get_full_url(
                self, 
                resource_group_name: str, 
                topic_name: str, 
                event_subscription_name: str, 
                **kwargs: Any
            ) -> EventSubscriptionFullUrl: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                topic_name: str, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[EventSubscription]: ...


    class azure.mgmt.eventgrid.aio.operations.TopicSpacesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_space_name: str, 
                topic_space_info: TopicSpace, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[TopicSpace]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_space_name: str, 
                topic_space_info: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[TopicSpace]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_space_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_space_name: str, 
                **kwargs: Any
            ) -> TopicSpace: ...

        @distributed_trace
        def list_by_namespace(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[TopicSpace]: ...


    class azure.mgmt.eventgrid.aio.operations.TopicTypesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                topic_type_name: str, 
                **kwargs: Any
            ) -> TopicTypeInfo: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[TopicTypeInfo]: ...

        @distributed_trace
        def list_event_types(
                self, 
                topic_type_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[EventType]: ...


    class azure.mgmt.eventgrid.aio.operations.TopicsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                topic_name: str, 
                topic_info: Topic, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Topic]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                topic_name: str, 
                topic_info: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Topic]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                topic_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_regenerate_key(
                self, 
                resource_group_name: str, 
                topic_name: str, 
                regenerate_key_request: TopicRegenerateKeyRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[TopicSharedAccessKeys]: ...

        @overload
        async def begin_regenerate_key(
                self, 
                resource_group_name: str, 
                topic_name: str, 
                regenerate_key_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[TopicSharedAccessKeys]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                topic_name: str, 
                topic_update_parameters: TopicUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Topic]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                topic_name: str, 
                topic_update_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Topic]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                topic_name: str, 
                **kwargs: Any
            ) -> Topic: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[Topic]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[Topic]: ...

        @distributed_trace
        def list_event_types(
                self, 
                resource_group_name: str, 
                provider_namespace: str, 
                resource_type_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[EventType]: ...

        @distributed_trace_async
        async def list_shared_access_keys(
                self, 
                resource_group_name: str, 
                topic_name: str, 
                **kwargs: Any
            ) -> TopicSharedAccessKeys: ...


    class azure.mgmt.eventgrid.aio.operations.VerifiedPartnersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                verified_partner_name: str, 
                **kwargs: Any
            ) -> VerifiedPartner: ...

        @distributed_trace
        def list(
                self, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[VerifiedPartner]: ...


namespace azure.mgmt.eventgrid.models

    class azure.mgmt.eventgrid.models.AdvancedFilter(Model):
        key: str
        operator_type: Union[str, AdvancedFilterOperatorType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                key: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.AdvancedFilterOperatorType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BOOL_EQUALS = "BoolEquals"
        IS_NOT_NULL = "IsNotNull"
        IS_NULL_OR_UNDEFINED = "IsNullOrUndefined"
        NUMBER_GREATER_THAN = "NumberGreaterThan"
        NUMBER_GREATER_THAN_OR_EQUALS = "NumberGreaterThanOrEquals"
        NUMBER_IN = "NumberIn"
        NUMBER_IN_RANGE = "NumberInRange"
        NUMBER_LESS_THAN = "NumberLessThan"
        NUMBER_LESS_THAN_OR_EQUALS = "NumberLessThanOrEquals"
        NUMBER_NOT_IN = "NumberNotIn"
        NUMBER_NOT_IN_RANGE = "NumberNotInRange"
        STRING_BEGINS_WITH = "StringBeginsWith"
        STRING_CONTAINS = "StringContains"
        STRING_ENDS_WITH = "StringEndsWith"
        STRING_IN = "StringIn"
        STRING_NOT_BEGINS_WITH = "StringNotBeginsWith"
        STRING_NOT_CONTAINS = "StringNotContains"
        STRING_NOT_ENDS_WITH = "StringNotEndsWith"
        STRING_NOT_IN = "StringNotIn"


    class azure.mgmt.eventgrid.models.AlternativeAuthenticationNameSource(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CLIENT_CERTIFICATE_DNS = "ClientCertificateDns"
        CLIENT_CERTIFICATE_EMAIL = "ClientCertificateEmail"
        CLIENT_CERTIFICATE_IP = "ClientCertificateIp"
        CLIENT_CERTIFICATE_SUBJECT = "ClientCertificateSubject"
        CLIENT_CERTIFICATE_URI = "ClientCertificateUri"


    class azure.mgmt.eventgrid.models.AzureADPartnerClientAuthentication(PartnerClientAuthentication):
        azure_active_directory_application_id_or_uri: str
        azure_active_directory_tenant_id: str
        client_authentication_type: Union[str, PartnerClientAuthenticationType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                azure_active_directory_application_id_or_uri: Optional[str] = ..., 
                azure_active_directory_tenant_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.AzureFunctionEventSubscriptionDestination(EventSubscriptionDestination):
        delivery_attribute_mappings: list[DeliveryAttributeMapping]
        endpoint_type: Union[str, EndpointType]
        max_events_per_batch: int
        preferred_batch_size_in_kilobytes: int
        resource_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                delivery_attribute_mappings: Optional[List[DeliveryAttributeMapping]] = ..., 
                max_events_per_batch: int = 1, 
                preferred_batch_size_in_kilobytes: int = 64, 
                resource_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.BoolEqualsAdvancedFilter(AdvancedFilter):
        key: str
        operator_type: Union[str, AdvancedFilterOperatorType]
        value: bool

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                key: Optional[str] = ..., 
                value: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.BoolEqualsFilter(Filter):
        key: str
        operator_type: Union[str, FilterOperatorType]
        value: bool

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                key: Optional[str] = ..., 
                value: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.CaCertificate(Resource):
        description: str
        encoded_certificate: str
        expiry_time_in_utc: datetime
        id: str
        issue_time_in_utc: datetime
        name: str
        provisioning_state: Union[str, CaCertificateProvisioningState]
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                encoded_certificate: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.CaCertificateProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETED = "Deleted"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.eventgrid.models.CaCertificatesListResult(Model):
        next_link: str
        value: list[CaCertificate]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[CaCertificate]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.Channel(Resource):
        channel_type: Union[str, ChannelType]
        expiration_time_if_not_activated_utc: datetime
        id: str
        message_for_activation: str
        name: str
        partner_destination_info: PartnerDestinationInfo
        partner_topic_info: PartnerTopicInfo
        provisioning_state: Union[str, ChannelProvisioningState]
        readiness_state: Union[str, ReadinessState]
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                channel_type: Optional[Union[str, ChannelType]] = ..., 
                expiration_time_if_not_activated_utc: Optional[datetime] = ..., 
                message_for_activation: Optional[str] = ..., 
                partner_destination_info: Optional[PartnerDestinationInfo] = ..., 
                partner_topic_info: Optional[PartnerTopicInfo] = ..., 
                provisioning_state: Optional[Union[str, ChannelProvisioningState]] = ..., 
                readiness_state: Optional[Union[str, ReadinessState]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.ChannelProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        IDLE_DUE_TO_MIRRORED_PARTNER_DESTINATION_DELETION = "IdleDueToMirroredPartnerDestinationDeletion"
        IDLE_DUE_TO_MIRRORED_PARTNER_TOPIC_DELETION = "IdleDueToMirroredPartnerTopicDeletion"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.eventgrid.models.ChannelType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PARTNER_DESTINATION = "PartnerDestination"
        PARTNER_TOPIC = "PartnerTopic"


    class azure.mgmt.eventgrid.models.ChannelUpdateParameters(Model):
        expiration_time_if_not_activated_utc: datetime
        partner_destination_info: PartnerUpdateDestinationInfo
        partner_topic_info: PartnerUpdateTopicInfo

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                expiration_time_if_not_activated_utc: Optional[datetime] = ..., 
                partner_destination_info: Optional[PartnerUpdateDestinationInfo] = ..., 
                partner_topic_info: Optional[PartnerUpdateTopicInfo] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.ChannelsListResult(Model):
        next_link: str
        value: list[Channel]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[Channel]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.Client(Resource):
        attributes: dict[str, any]
        authentication_name: str
        client_certificate_authentication: ClientCertificateAuthentication
        description: str
        id: str
        name: str
        provisioning_state: Union[str, ClientProvisioningState]
        state: Union[str, ClientState]
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                attributes: Optional[Dict[str, Any]] = ..., 
                authentication_name: Optional[str] = ..., 
                client_certificate_authentication: Optional[ClientCertificateAuthentication] = ..., 
                description: Optional[str] = ..., 
                state: Union[str, ClientState] = "Enabled", 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.ClientAuthenticationSettings(Model):
        alternative_authentication_name_sources: Union[list[str, AlternativeAuthenticationNameSource]]
        custom_jwt_authentication: CustomJwtAuthenticationSettings
        webhook_authentication: WebhookAuthenticationSettings

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                alternative_authentication_name_sources: Optional[List[Union[str, AlternativeAuthenticationNameSource]]] = ..., 
                custom_jwt_authentication: Optional[CustomJwtAuthenticationSettings] = ..., 
                webhook_authentication: Optional[WebhookAuthenticationSettings] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.ClientCertificateAuthentication(Model):
        allowed_thumbprints: list[str]
        validation_scheme: Union[str, ClientCertificateValidationScheme]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                allowed_thumbprints: Optional[List[str]] = ..., 
                validation_scheme: Optional[Union[str, ClientCertificateValidationScheme]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.ClientCertificateValidationScheme(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DNS_MATCHES_AUTHENTICATION_NAME = "DnsMatchesAuthenticationName"
        EMAIL_MATCHES_AUTHENTICATION_NAME = "EmailMatchesAuthenticationName"
        IP_MATCHES_AUTHENTICATION_NAME = "IpMatchesAuthenticationName"
        SUBJECT_MATCHES_AUTHENTICATION_NAME = "SubjectMatchesAuthenticationName"
        THUMBPRINT_MATCH = "ThumbprintMatch"
        URI_MATCHES_AUTHENTICATION_NAME = "UriMatchesAuthenticationName"


    class azure.mgmt.eventgrid.models.ClientGroup(Resource):
        description: str
        id: str
        name: str
        provisioning_state: Union[str, ClientGroupProvisioningState]
        query: str
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                query: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.ClientGroupProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETED = "Deleted"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.eventgrid.models.ClientGroupsListResult(Model):
        next_link: str
        value: list[ClientGroup]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[ClientGroup]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.ClientProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETED = "Deleted"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.eventgrid.models.ClientState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.eventgrid.models.ClientsListResult(Model):
        next_link: str
        value: list[Client]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[Client]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.ConnectionState(Model):
        actions_required: str
        description: str
        status: Union[str, PersistedConnectionStatus]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                actions_required: Optional[str] = ..., 
                description: Optional[str] = ..., 
                status: Optional[Union[str, PersistedConnectionStatus]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.eventgrid.models.CustomDomainConfiguration(Model):
        certificate_url: str
        expected_txt_record_name: str
        expected_txt_record_value: str
        fully_qualified_domain_name: str
        identity: CustomDomainIdentity
        validation_state: Union[str, CustomDomainValidationState]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                certificate_url: Optional[str] = ..., 
                expected_txt_record_name: Optional[str] = ..., 
                expected_txt_record_value: Optional[str] = ..., 
                fully_qualified_domain_name: str, 
                identity: Optional[CustomDomainIdentity] = ..., 
                validation_state: Optional[Union[str, CustomDomainValidationState]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.CustomDomainIdentity(Model):
        type: Union[str, CustomDomainIdentityType]
        user_assigned_identity: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                type: Optional[Union[str, CustomDomainIdentityType]] = ..., 
                user_assigned_identity: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.CustomDomainIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM_ASSIGNED = "SystemAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.eventgrid.models.CustomDomainOwnershipValidationResult(Model):
        custom_domains_for_topic_spaces_configuration: list[CustomDomainConfiguration]
        custom_domains_for_topics_configuration: list[CustomDomainConfiguration]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                custom_domains_for_topic_spaces_configuration: Optional[List[CustomDomainConfiguration]] = ..., 
                custom_domains_for_topics_configuration: Optional[List[CustomDomainConfiguration]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.CustomDomainValidationState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPROVED = "Approved"
        ERROR_RETRIEVING_DNS_RECORD = "ErrorRetrievingDnsRecord"
        PENDING = "Pending"


    class azure.mgmt.eventgrid.models.CustomJwtAuthenticationManagedIdentity(Model):
        type: Union[str, CustomJwtAuthenticationManagedIdentityType]
        user_assigned_identity: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                type: Union[str, CustomJwtAuthenticationManagedIdentityType], 
                user_assigned_identity: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.CustomJwtAuthenticationManagedIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM_ASSIGNED = "SystemAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.eventgrid.models.CustomJwtAuthenticationSettings(Model):
        encoded_issuer_certificates: list[EncodedIssuerCertificateInfo]
        issuer_certificates: list[IssuerCertificateInfo]
        token_issuer: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                encoded_issuer_certificates: Optional[List[EncodedIssuerCertificateInfo]] = ..., 
                issuer_certificates: Optional[List[IssuerCertificateInfo]] = ..., 
                token_issuer: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.CustomWebhookAuthenticationManagedIdentity(Model):
        type: Union[str, CustomWebhookAuthenticationManagedIdentityType]
        user_assigned_identity: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                type: Union[str, CustomWebhookAuthenticationManagedIdentityType], 
                user_assigned_identity: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.CustomWebhookAuthenticationManagedIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM_ASSIGNED = "SystemAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.eventgrid.models.DataResidencyBoundary(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        WITHIN_GEOPAIR = "WithinGeopair"
        WITHIN_REGION = "WithinRegion"


    class azure.mgmt.eventgrid.models.DeadLetterDestination(Model):
        endpoint_type: Union[str, DeadLetterEndPointType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.DeadLetterEndPointType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        STORAGE_BLOB = "StorageBlob"


    class azure.mgmt.eventgrid.models.DeadLetterWithResourceIdentity(Model):
        dead_letter_destination: DeadLetterDestination
        identity: EventSubscriptionIdentity

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                dead_letter_destination: Optional[DeadLetterDestination] = ..., 
                identity: Optional[EventSubscriptionIdentity] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.DeliveryAttributeListResult(Model):
        value: list[DeliveryAttributeMapping]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[DeliveryAttributeMapping]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.DeliveryAttributeMapping(Model):
        name: str
        type: Union[str, DeliveryAttributeMappingType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.DeliveryAttributeMappingType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DYNAMIC = "Dynamic"
        STATIC = "Static"


    class azure.mgmt.eventgrid.models.DeliveryConfiguration(Model):
        delivery_mode: Union[str, DeliveryMode]
        push: PushInfo
        queue: QueueInfo

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                delivery_mode: Optional[Union[str, DeliveryMode]] = ..., 
                push: Optional[PushInfo] = ..., 
                queue: Optional[QueueInfo] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.DeliveryMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PUSH = "Push"
        QUEUE = "Queue"


    class azure.mgmt.eventgrid.models.DeliverySchema(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CLOUD_EVENT_SCHEMA_V1_0 = "CloudEventSchemaV1_0"


    class azure.mgmt.eventgrid.models.DeliveryWithResourceIdentity(Model):
        destination: EventSubscriptionDestination
        identity: EventSubscriptionIdentity

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                destination: Optional[EventSubscriptionDestination] = ..., 
                identity: Optional[EventSubscriptionIdentity] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.Domain(TrackedResource):
        auto_create_topic_with_first_subscription: bool
        auto_delete_topic_with_last_subscription: bool
        data_residency_boundary: Union[str, DataResidencyBoundary]
        disable_local_auth: bool
        endpoint: str
        event_type_info: EventTypeInfo
        id: str
        identity: IdentityInfo
        inbound_ip_rules: list[InboundIpRule]
        input_schema: Union[str, InputSchema]
        input_schema_mapping: InputSchemaMapping
        location: str
        metric_resource_id: str
        minimum_tls_version_allowed: Union[str, TlsVersion]
        name: str
        private_endpoint_connections: list[PrivateEndpointConnection]
        provisioning_state: Union[str, DomainProvisioningState]
        public_network_access: Union[str, PublicNetworkAccess]
        sku: ResourceSku
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                auto_create_topic_with_first_subscription: bool = True, 
                auto_delete_topic_with_last_subscription: bool = True, 
                data_residency_boundary: Optional[Union[str, DataResidencyBoundary]] = ..., 
                disable_local_auth: bool = False, 
                event_type_info: Optional[EventTypeInfo] = ..., 
                identity: Optional[IdentityInfo] = ..., 
                inbound_ip_rules: Optional[List[InboundIpRule]] = ..., 
                input_schema: Optional[Union[str, InputSchema]] = ..., 
                input_schema_mapping: Optional[InputSchemaMapping] = ..., 
                location: str, 
                minimum_tls_version_allowed: Optional[Union[str, TlsVersion]] = ..., 
                public_network_access: Optional[Union[str, PublicNetworkAccess]] = ..., 
                sku: Optional[ResourceSku] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.DomainProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.eventgrid.models.DomainRegenerateKeyRequest(Model):
        key_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                key_name: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.DomainSharedAccessKeys(Model):
        key1: str
        key2: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                key1: Optional[str] = ..., 
                key2: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.DomainTopic(Resource):
        id: str
        name: str
        provisioning_state: Union[str, DomainTopicProvisioningState]
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.DomainTopicProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.eventgrid.models.DomainTopicsListResult(Model):
        next_link: str
        value: list[DomainTopic]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[DomainTopic]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.DomainUpdateParameters(Model):
        auto_create_topic_with_first_subscription: bool
        auto_delete_topic_with_last_subscription: bool
        data_residency_boundary: Union[str, DataResidencyBoundary]
        disable_local_auth: bool
        event_type_info: EventTypeInfo
        identity: IdentityInfo
        inbound_ip_rules: list[InboundIpRule]
        minimum_tls_version_allowed: Union[str, TlsVersion]
        public_network_access: Union[str, PublicNetworkAccess]
        sku: ResourceSku
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                auto_create_topic_with_first_subscription: Optional[bool] = ..., 
                auto_delete_topic_with_last_subscription: Optional[bool] = ..., 
                data_residency_boundary: Optional[Union[str, DataResidencyBoundary]] = ..., 
                disable_local_auth: Optional[bool] = ..., 
                event_type_info: Optional[EventTypeInfo] = ..., 
                identity: Optional[IdentityInfo] = ..., 
                inbound_ip_rules: Optional[List[InboundIpRule]] = ..., 
                minimum_tls_version_allowed: Optional[Union[str, TlsVersion]] = ..., 
                public_network_access: Optional[Union[str, PublicNetworkAccess]] = ..., 
                sku: Optional[ResourceSku] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.DomainsListResult(Model):
        next_link: str
        value: list[Domain]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[Domain]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.DynamicDeliveryAttributeMapping(DeliveryAttributeMapping):
        name: str
        source_field: str
        type: Union[str, DeliveryAttributeMappingType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                source_field: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.DynamicRoutingEnrichment(Model):
        key: str
        value: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                key: Optional[str] = ..., 
                value: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.EncodedIssuerCertificateInfo(Model):
        encoded_certificate: str
        kid: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                encoded_certificate: str, 
                kid: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.EndpointType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_FUNCTION = "AzureFunction"
        EVENT_HUB = "EventHub"
        HYBRID_CONNECTION = "HybridConnection"
        MONITOR_ALERT = "MonitorAlert"
        NAMESPACE_TOPIC = "NamespaceTopic"
        PARTNER_DESTINATION = "PartnerDestination"
        SERVICE_BUS_QUEUE = "ServiceBusQueue"
        SERVICE_BUS_TOPIC = "ServiceBusTopic"
        STORAGE_QUEUE = "StorageQueue"
        WEB_HOOK = "WebHook"


    class azure.mgmt.eventgrid.models.ErrorAdditionalInfo(Model):
        info: JSON
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.ErrorDetail(Model):
        additional_info: list[ErrorAdditionalInfo]
        code: str
        details: list[ErrorDetail]
        message: str
        target: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.ErrorResponse(Model):
        error: ErrorDetail

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.EventDefinitionKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INLINE = "Inline"


    class azure.mgmt.eventgrid.models.EventDeliverySchema(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CLOUD_EVENT_SCHEMA_V1_0 = "CloudEventSchemaV1_0"
        CUSTOM_INPUT_SCHEMA = "CustomInputSchema"
        EVENT_GRID_SCHEMA = "EventGridSchema"


    class azure.mgmt.eventgrid.models.EventHubEventSubscriptionDestination(EventSubscriptionDestination):
        delivery_attribute_mappings: list[DeliveryAttributeMapping]
        endpoint_type: Union[str, EndpointType]
        resource_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                delivery_attribute_mappings: Optional[List[DeliveryAttributeMapping]] = ..., 
                resource_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.EventInputSchema(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CLOUD_EVENT_SCHEMA_V1_0 = "CloudEventSchemaV1_0"


    class azure.mgmt.eventgrid.models.EventSubscription(Resource):
        dead_letter_destination: DeadLetterDestination
        dead_letter_with_resource_identity: DeadLetterWithResourceIdentity
        delivery_with_resource_identity: DeliveryWithResourceIdentity
        destination: EventSubscriptionDestination
        event_delivery_schema: Union[str, EventDeliverySchema]
        expiration_time_utc: datetime
        filter: EventSubscriptionFilter
        id: str
        labels: list[str]
        name: str
        provisioning_state: Union[str, EventSubscriptionProvisioningState]
        retry_policy: RetryPolicy
        system_data: SystemData
        topic: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                dead_letter_destination: Optional[DeadLetterDestination] = ..., 
                dead_letter_with_resource_identity: Optional[DeadLetterWithResourceIdentity] = ..., 
                delivery_with_resource_identity: Optional[DeliveryWithResourceIdentity] = ..., 
                destination: Optional[EventSubscriptionDestination] = ..., 
                event_delivery_schema: Optional[Union[str, EventDeliverySchema]] = ..., 
                expiration_time_utc: Optional[datetime] = ..., 
                filter: Optional[EventSubscriptionFilter] = ..., 
                labels: Optional[List[str]] = ..., 
                retry_policy: Optional[RetryPolicy] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.EventSubscriptionDestination(Model):
        endpoint_type: Union[str, EndpointType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.EventSubscriptionFilter(Model):
        advanced_filters: list[AdvancedFilter]
        enable_advanced_filtering_on_arrays: bool
        included_event_types: list[str]
        is_subject_case_sensitive: bool
        subject_begins_with: str
        subject_ends_with: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                advanced_filters: Optional[List[AdvancedFilter]] = ..., 
                enable_advanced_filtering_on_arrays: Optional[bool] = ..., 
                included_event_types: Optional[List[str]] = ..., 
                is_subject_case_sensitive: bool = False, 
                subject_begins_with: Optional[str] = ..., 
                subject_ends_with: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.EventSubscriptionFullUrl(Model):
        endpoint_url: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                endpoint_url: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.EventSubscriptionIdentity(Model):
        federated_identity_credential_info: FederatedIdentityCredentialInfo
        type: Union[str, EventSubscriptionIdentityType]
        user_assigned_identity: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                federated_identity_credential_info: Optional[FederatedIdentityCredentialInfo] = ..., 
                type: Optional[Union[str, EventSubscriptionIdentityType]] = ..., 
                user_assigned_identity: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.EventSubscriptionIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM_ASSIGNED = "SystemAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.eventgrid.models.EventSubscriptionProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AWAITING_MANUAL_ACTION = "AwaitingManualAction"
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.eventgrid.models.EventSubscriptionUpdateParameters(Model):
        dead_letter_destination: DeadLetterDestination
        dead_letter_with_resource_identity: DeadLetterWithResourceIdentity
        delivery_with_resource_identity: DeliveryWithResourceIdentity
        destination: EventSubscriptionDestination
        event_delivery_schema: Union[str, EventDeliverySchema]
        expiration_time_utc: datetime
        filter: EventSubscriptionFilter
        labels: list[str]
        retry_policy: RetryPolicy

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                dead_letter_destination: Optional[DeadLetterDestination] = ..., 
                dead_letter_with_resource_identity: Optional[DeadLetterWithResourceIdentity] = ..., 
                delivery_with_resource_identity: Optional[DeliveryWithResourceIdentity] = ..., 
                destination: Optional[EventSubscriptionDestination] = ..., 
                event_delivery_schema: Optional[Union[str, EventDeliverySchema]] = ..., 
                expiration_time_utc: Optional[datetime] = ..., 
                filter: Optional[EventSubscriptionFilter] = ..., 
                labels: Optional[List[str]] = ..., 
                retry_policy: Optional[RetryPolicy] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.EventSubscriptionsListResult(Model):
        next_link: str
        value: list[EventSubscription]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[EventSubscription]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.EventType(Resource):
        description: str
        display_name: str
        id: str
        is_in_default_set: bool
        name: str
        schema_url: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                is_in_default_set: Optional[bool] = ..., 
                schema_url: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.EventTypeInfo(Model):
        inline_event_types: dict[str, InlineEventProperties]
        kind: Union[str, EventDefinitionKind]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                inline_event_types: Optional[Dict[str, InlineEventProperties]] = ..., 
                kind: Optional[Union[str, EventDefinitionKind]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.EventTypesListResult(Model):
        value: list[EventType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[EventType]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.ExtendedLocation(Model):
        name: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                type: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.ExtensionTopic(Resource):
        description: str
        id: str
        name: str
        system_data: SystemData
        system_topic: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                system_topic: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.FederatedIdentityCredentialInfo(Model):
        federated_client_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                federated_client_id: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.Filter(Model):
        key: str
        operator_type: Union[str, FilterOperatorType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                key: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.FilterOperatorType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BOOL_EQUALS = "BoolEquals"
        IS_NOT_NULL = "IsNotNull"
        IS_NULL_OR_UNDEFINED = "IsNullOrUndefined"
        NUMBER_GREATER_THAN = "NumberGreaterThan"
        NUMBER_GREATER_THAN_OR_EQUALS = "NumberGreaterThanOrEquals"
        NUMBER_IN = "NumberIn"
        NUMBER_IN_RANGE = "NumberInRange"
        NUMBER_LESS_THAN = "NumberLessThan"
        NUMBER_LESS_THAN_OR_EQUALS = "NumberLessThanOrEquals"
        NUMBER_NOT_IN = "NumberNotIn"
        NUMBER_NOT_IN_RANGE = "NumberNotInRange"
        STRING_BEGINS_WITH = "StringBeginsWith"
        STRING_CONTAINS = "StringContains"
        STRING_ENDS_WITH = "StringEndsWith"
        STRING_IN = "StringIn"
        STRING_NOT_BEGINS_WITH = "StringNotBeginsWith"
        STRING_NOT_CONTAINS = "StringNotContains"
        STRING_NOT_ENDS_WITH = "StringNotEndsWith"
        STRING_NOT_IN = "StringNotIn"


    class azure.mgmt.eventgrid.models.FiltersConfiguration(Model):
        filters: list[Filter]
        included_event_types: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                filters: Optional[List[Filter]] = ..., 
                included_event_types: Optional[List[str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.HybridConnectionEventSubscriptionDestination(EventSubscriptionDestination):
        delivery_attribute_mappings: list[DeliveryAttributeMapping]
        endpoint_type: Union[str, EndpointType]
        resource_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                delivery_attribute_mappings: Optional[List[DeliveryAttributeMapping]] = ..., 
                resource_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.IdentityInfo(Model):
        principal_id: str
        tenant_id: str
        type: Union[str, IdentityType]
        user_assigned_identities: dict[str, UserIdentityProperties]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                principal_id: Optional[str] = ..., 
                tenant_id: Optional[str] = ..., 
                type: Optional[Union[str, IdentityType]] = ..., 
                user_assigned_identities: Optional[Dict[str, UserIdentityProperties]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.IdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        SYSTEM_ASSIGNED_USER_ASSIGNED = "SystemAssigned, UserAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.eventgrid.models.InboundIpRule(Model):
        action: Union[str, IpActionType]
        ip_mask: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                action: Optional[Union[str, IpActionType]] = ..., 
                ip_mask: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.InlineEventProperties(Model):
        data_schema_url: str
        description: str
        display_name: str
        documentation_url: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                data_schema_url: Optional[str] = ..., 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                documentation_url: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.InputSchema(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CLOUD_EVENT_SCHEMA_V1_0 = "CloudEventSchemaV1_0"
        CUSTOM_EVENT_SCHEMA = "CustomEventSchema"
        EVENT_GRID_SCHEMA = "EventGridSchema"


    class azure.mgmt.eventgrid.models.InputSchemaMapping(Model):
        input_schema_mapping_type: Union[str, InputSchemaMappingType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.InputSchemaMappingType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        JSON = "Json"


    class azure.mgmt.eventgrid.models.IpActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALLOW = "Allow"


    class azure.mgmt.eventgrid.models.IsNotNullAdvancedFilter(AdvancedFilter):
        key: str
        operator_type: Union[str, AdvancedFilterOperatorType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                key: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.IsNotNullFilter(Filter):
        key: str
        operator_type: Union[str, FilterOperatorType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                key: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.IsNullOrUndefinedAdvancedFilter(AdvancedFilter):
        key: str
        operator_type: Union[str, AdvancedFilterOperatorType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                key: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.IsNullOrUndefinedFilter(Filter):
        key: str
        operator_type: Union[str, FilterOperatorType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                key: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.IssuerCertificateInfo(Model):
        certificate_url: str
        identity: CustomJwtAuthenticationManagedIdentity

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                certificate_url: str, 
                identity: Optional[CustomJwtAuthenticationManagedIdentity] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.JsonField(Model):
        source_field: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                source_field: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.JsonFieldWithDefault(Model):
        default_value: str
        source_field: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                default_value: Optional[str] = ..., 
                source_field: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.JsonInputSchemaMapping(InputSchemaMapping):
        data_version: JsonFieldWithDefault
        event_time: JsonField
        event_type: JsonFieldWithDefault
        id: JsonField
        input_schema_mapping_type: Union[str, InputSchemaMappingType]
        subject: JsonFieldWithDefault
        topic: JsonField

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                data_version: Optional[JsonFieldWithDefault] = ..., 
                event_time: Optional[JsonField] = ..., 
                event_type: Optional[JsonFieldWithDefault] = ..., 
                id: Optional[JsonField] = ..., 
                subject: Optional[JsonFieldWithDefault] = ..., 
                topic: Optional[JsonField] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.MonitorAlertEventSubscriptionDestination(EventSubscriptionDestination):
        action_groups: list[str]
        description: str
        endpoint_type: Union[str, EndpointType]
        severity: Union[str, MonitorAlertSeverity]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                action_groups: Optional[List[str]] = ..., 
                description: Optional[str] = ..., 
                severity: Optional[Union[str, MonitorAlertSeverity]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.MonitorAlertSeverity(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SEV0 = "Sev0"
        SEV1 = "Sev1"
        SEV2 = "Sev2"
        SEV3 = "Sev3"
        SEV4 = "Sev4"


    class azure.mgmt.eventgrid.models.Namespace(TrackedResource):
        id: str
        identity: IdentityInfo
        inbound_ip_rules: list[InboundIpRule]
        is_zone_redundant: bool
        location: str
        minimum_tls_version_allowed: Union[str, TlsVersion]
        name: str
        private_endpoint_connections: list[PrivateEndpointConnection]
        provisioning_state: Union[str, NamespaceProvisioningState]
        public_network_access: Union[str, PublicNetworkAccess]
        sku: NamespaceSku
        system_data: SystemData
        tags: dict[str, str]
        topic_spaces_configuration: TopicSpacesConfiguration
        topics_configuration: TopicsConfiguration
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                identity: Optional[IdentityInfo] = ..., 
                inbound_ip_rules: Optional[List[InboundIpRule]] = ..., 
                is_zone_redundant: Optional[bool] = ..., 
                location: str, 
                minimum_tls_version_allowed: Optional[Union[str, TlsVersion]] = ..., 
                private_endpoint_connections: Optional[List[PrivateEndpointConnection]] = ..., 
                public_network_access: Optional[Union[str, PublicNetworkAccess]] = ..., 
                sku: Optional[NamespaceSku] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                topic_spaces_configuration: Optional[TopicSpacesConfiguration] = ..., 
                topics_configuration: Optional[TopicsConfiguration] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.NamespaceProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CREATE_FAILED = "CreateFailed"
        CREATING = "Creating"
        DELETED = "Deleted"
        DELETE_FAILED = "DeleteFailed"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATED_FAILED = "UpdatedFailed"
        UPDATING = "Updating"


    class azure.mgmt.eventgrid.models.NamespaceRegenerateKeyRequest(Model):
        key_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                key_name: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.NamespaceSharedAccessKeys(Model):
        key1: str
        key2: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                key1: Optional[str] = ..., 
                key2: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.NamespaceSku(Model):
        capacity: int
        name: Union[str, SkuName]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                capacity: Optional[int] = ..., 
                name: Optional[Union[str, SkuName]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.NamespaceTopic(Resource):
        event_retention_in_days: int
        id: str
        input_schema: Union[str, EventInputSchema]
        name: str
        provisioning_state: Union[str, NamespaceTopicProvisioningState]
        publisher_type: Union[str, PublisherType]
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                event_retention_in_days: Optional[int] = ..., 
                input_schema: Union[str, EventInputSchema] = "CloudEventSchemaV1_0", 
                publisher_type: Optional[Union[str, PublisherType]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.NamespaceTopicEventSubscriptionDestination(EventSubscriptionDestination):
        endpoint_type: Union[str, EndpointType]
        resource_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                resource_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.NamespaceTopicProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CREATE_FAILED = "CreateFailed"
        CREATING = "Creating"
        DELETED = "Deleted"
        DELETE_FAILED = "DeleteFailed"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATED_FAILED = "UpdatedFailed"
        UPDATING = "Updating"


    class azure.mgmt.eventgrid.models.NamespaceTopicUpdateParameters(Model):
        event_retention_in_days: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                event_retention_in_days: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.NamespaceTopicsListResult(Model):
        next_link: str
        value: list[NamespaceTopic]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[NamespaceTopic]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.NamespaceUpdateParameters(Model):
        identity: IdentityInfo
        inbound_ip_rules: list[InboundIpRule]
        public_network_access: Union[str, PublicNetworkAccess]
        sku: NamespaceSku
        tags: dict[str, str]
        topic_spaces_configuration: UpdateTopicSpacesConfigurationInfo
        topics_configuration: UpdateTopicsConfigurationInfo

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                identity: Optional[IdentityInfo] = ..., 
                inbound_ip_rules: Optional[List[InboundIpRule]] = ..., 
                public_network_access: Optional[Union[str, PublicNetworkAccess]] = ..., 
                sku: Optional[NamespaceSku] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                topic_spaces_configuration: Optional[UpdateTopicSpacesConfigurationInfo] = ..., 
                topics_configuration: Optional[UpdateTopicsConfigurationInfo] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.NamespacesListResult(Model):
        next_link: str
        value: list[Namespace]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[Namespace]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.NetworkSecurityPerimeterAssociationAccessMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUDIT = "Audit"
        ENFORCED = "Enforced"
        LEARNING = "Learning"


    class azure.mgmt.eventgrid.models.NetworkSecurityPerimeterConfigProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETED = "Deleted"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.eventgrid.models.NetworkSecurityPerimeterConfiguration(Resource):
        id: str
        name: str
        network_security_perimeter: NetworkSecurityPerimeterInfo
        profile: NetworkSecurityPerimeterConfigurationProfile
        provisioning_issues: list[NetworkSecurityPerimeterConfigurationIssues]
        provisioning_state: Union[str, NetworkSecurityPerimeterConfigProvisioningState]
        resource_association: ResourceAssociation
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                network_security_perimeter: Optional[NetworkSecurityPerimeterInfo] = ..., 
                profile: Optional[NetworkSecurityPerimeterConfigurationProfile] = ..., 
                provisioning_issues: Optional[List[NetworkSecurityPerimeterConfigurationIssues]] = ..., 
                provisioning_state: Optional[Union[str, NetworkSecurityPerimeterConfigProvisioningState]] = ..., 
                resource_association: Optional[ResourceAssociation] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.NetworkSecurityPerimeterConfigurationIssueSeverity(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ERROR = "Error"
        WARNING = "Warning"


    class azure.mgmt.eventgrid.models.NetworkSecurityPerimeterConfigurationIssueType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONFIGURATION_PROPAGATION_FAILURE = "ConfigurationPropagationFailure"
        MISSING_IDENTITY_CONFIGURATION = "MissingIdentityConfiguration"
        MISSING_PERIMETER_CONFIGURATION = "MissingPerimeterConfiguration"
        OTHER = "Other"


    class azure.mgmt.eventgrid.models.NetworkSecurityPerimeterConfigurationIssues(Model):
        description: str
        issue_type: Union[str, NetworkSecurityPerimeterConfigurationIssueType]
        name: str
        severity: Union[str, NetworkSecurityPerimeterConfigurationIssueSeverity]
        suggested_access_rules: list[str]
        suggested_resource_ids: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                issue_type: Optional[Union[str, NetworkSecurityPerimeterConfigurationIssueType]] = ..., 
                name: Optional[str] = ..., 
                severity: Optional[Union[str, NetworkSecurityPerimeterConfigurationIssueSeverity]] = ..., 
                suggested_access_rules: Optional[List[str]] = ..., 
                suggested_resource_ids: Optional[List[str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.NetworkSecurityPerimeterConfigurationList(Model):
        next_link: str
        value: list[NetworkSecurityPerimeterConfiguration]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[NetworkSecurityPerimeterConfiguration]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.NetworkSecurityPerimeterConfigurationProfile(Model):
        access_rules: list[NetworkSecurityPerimeterProfileAccessRule]
        access_rules_version: str
        diagnostic_settings_version: str
        enabled_log_categories: list[str]
        name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                access_rules: Optional[List[NetworkSecurityPerimeterProfileAccessRule]] = ..., 
                access_rules_version: Optional[str] = ..., 
                diagnostic_settings_version: Optional[str] = ..., 
                enabled_log_categories: Optional[List[str]] = ..., 
                name: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.NetworkSecurityPerimeterInfo(Model):
        id: str
        location: str
        perimeter_guid: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                location: Optional[str] = ..., 
                perimeter_guid: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.NetworkSecurityPerimeterProfileAccessRule(Model):
        address_prefixes: list[str]
        direction: Union[str, NetworkSecurityPerimeterProfileAccessRuleDirection]
        email_addresses: list[str]
        fully_qualified_arm_id: str
        fully_qualified_domain_names: list[str]
        name: str
        network_security_perimeters: list[NetworkSecurityPerimeterInfo]
        phone_numbers: list[str]
        subscriptions: list[NetworkSecurityPerimeterSubscription]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                address_prefixes: Optional[List[str]] = ..., 
                direction: Optional[Union[str, NetworkSecurityPerimeterProfileAccessRuleDirection]] = ..., 
                email_addresses: Optional[List[str]] = ..., 
                fully_qualified_arm_id: Optional[str] = ..., 
                fully_qualified_domain_names: Optional[List[str]] = ..., 
                name: Optional[str] = ..., 
                network_security_perimeters: Optional[List[NetworkSecurityPerimeterInfo]] = ..., 
                phone_numbers: Optional[List[str]] = ..., 
                subscriptions: Optional[List[NetworkSecurityPerimeterSubscription]] = ..., 
                type: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.NetworkSecurityPerimeterProfileAccessRuleDirection(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INBOUND = "Inbound"
        OUTBOUND = "Outbound"


    class azure.mgmt.eventgrid.models.NetworkSecurityPerimeterResourceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DOMAINS = "domains"
        TOPICS = "topics"


    class azure.mgmt.eventgrid.models.NetworkSecurityPerimeterSubscription(Model):
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
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.NumberGreaterThanAdvancedFilter(AdvancedFilter):
        key: str
        operator_type: Union[str, AdvancedFilterOperatorType]
        value: float

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                key: Optional[str] = ..., 
                value: Optional[float] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.NumberGreaterThanFilter(Filter):
        key: str
        operator_type: Union[str, FilterOperatorType]
        value: float

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                key: Optional[str] = ..., 
                value: Optional[float] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.NumberGreaterThanOrEqualsAdvancedFilter(AdvancedFilter):
        key: str
        operator_type: Union[str, AdvancedFilterOperatorType]
        value: float

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                key: Optional[str] = ..., 
                value: Optional[float] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.NumberGreaterThanOrEqualsFilter(Filter):
        key: str
        operator_type: Union[str, FilterOperatorType]
        value: float

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                key: Optional[str] = ..., 
                value: Optional[float] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.NumberInAdvancedFilter(AdvancedFilter):
        key: str
        operator_type: Union[str, AdvancedFilterOperatorType]
        values: list[float]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                key: Optional[str] = ..., 
                values: Optional[List[float]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.NumberInFilter(Filter):
        key: str
        operator_type: Union[str, FilterOperatorType]
        values: list[float]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                key: Optional[str] = ..., 
                values: Optional[List[float]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.NumberInRangeAdvancedFilter(AdvancedFilter):
        key: str
        operator_type: Union[str, AdvancedFilterOperatorType]
        values: list[list[float]]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                key: Optional[str] = ..., 
                values: Optional[List[List[float]]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.NumberInRangeFilter(Filter):
        key: str
        operator_type: Union[str, FilterOperatorType]
        values: list[list[float]]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                key: Optional[str] = ..., 
                values: Optional[List[List[float]]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.NumberLessThanAdvancedFilter(AdvancedFilter):
        key: str
        operator_type: Union[str, AdvancedFilterOperatorType]
        value: float

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                key: Optional[str] = ..., 
                value: Optional[float] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.NumberLessThanFilter(Filter):
        key: str
        operator_type: Union[str, FilterOperatorType]
        value: float

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                key: Optional[str] = ..., 
                value: Optional[float] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.NumberLessThanOrEqualsAdvancedFilter(AdvancedFilter):
        key: str
        operator_type: Union[str, AdvancedFilterOperatorType]
        value: float

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                key: Optional[str] = ..., 
                value: Optional[float] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.NumberLessThanOrEqualsFilter(Filter):
        key: str
        operator_type: Union[str, FilterOperatorType]
        value: float

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                key: Optional[str] = ..., 
                value: Optional[float] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.NumberNotInAdvancedFilter(AdvancedFilter):
        key: str
        operator_type: Union[str, AdvancedFilterOperatorType]
        values: list[float]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                key: Optional[str] = ..., 
                values: Optional[List[float]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.NumberNotInFilter(Filter):
        key: str
        operator_type: Union[str, FilterOperatorType]
        values: list[float]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                key: Optional[str] = ..., 
                values: Optional[List[float]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.NumberNotInRangeAdvancedFilter(AdvancedFilter):
        key: str
        operator_type: Union[str, AdvancedFilterOperatorType]
        values: list[list[float]]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                key: Optional[str] = ..., 
                values: Optional[List[List[float]]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.NumberNotInRangeFilter(Filter):
        key: str
        operator_type: Union[str, FilterOperatorType]
        values: list[list[float]]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                key: Optional[str] = ..., 
                values: Optional[List[List[float]]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.Operation(Model):
        display: OperationInfo
        is_data_action: bool
        name: str
        origin: str
        properties: JSON

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                display: Optional[OperationInfo] = ..., 
                is_data_action: Optional[bool] = ..., 
                name: Optional[str] = ..., 
                origin: Optional[str] = ..., 
                properties: Optional[JSON] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.OperationInfo(Model):
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
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.OperationsListResult(Model):
        value: list[Operation]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[Operation]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.Partner(Model):
        authorization_expiration_time_in_utc: datetime
        partner_name: str
        partner_registration_immutable_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                authorization_expiration_time_in_utc: Optional[datetime] = ..., 
                partner_name: Optional[str] = ..., 
                partner_registration_immutable_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.PartnerAuthorization(Model):
        authorized_partners_list: list[Partner]
        default_maximum_expiration_time_in_days: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                authorized_partners_list: Optional[List[Partner]] = ..., 
                default_maximum_expiration_time_in_days: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.PartnerClientAuthentication(Model):
        client_authentication_type: Union[str, PartnerClientAuthenticationType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.PartnerClientAuthenticationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_AD = "AzureAD"


    class azure.mgmt.eventgrid.models.PartnerConfiguration(Resource):
        id: str
        location: str
        name: str
        partner_authorization: PartnerAuthorization
        provisioning_state: Union[str, PartnerConfigurationProvisioningState]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                partner_authorization: Optional[PartnerAuthorization] = ..., 
                provisioning_state: Optional[Union[str, PartnerConfigurationProvisioningState]] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.PartnerConfigurationProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.eventgrid.models.PartnerConfigurationUpdateParameters(Model):
        default_maximum_expiration_time_in_days: int
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                default_maximum_expiration_time_in_days: Optional[int] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.PartnerConfigurationsListResult(Model):
        next_link: str
        value: list[PartnerConfiguration]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[PartnerConfiguration]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.PartnerDestination(TrackedResource):
        activation_state: Union[str, PartnerDestinationActivationState]
        endpoint_base_url: str
        endpoint_service_context: str
        expiration_time_if_not_activated_utc: datetime
        id: str
        location: str
        message_for_activation: str
        name: str
        partner_registration_immutable_id: str
        provisioning_state: Union[str, PartnerDestinationProvisioningState]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                activation_state: Optional[Union[str, PartnerDestinationActivationState]] = ..., 
                endpoint_base_url: Optional[str] = ..., 
                endpoint_service_context: Optional[str] = ..., 
                expiration_time_if_not_activated_utc: Optional[datetime] = ..., 
                location: str, 
                message_for_activation: Optional[str] = ..., 
                partner_registration_immutable_id: Optional[str] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.PartnerDestinationActivationState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVATED = "Activated"
        NEVER_ACTIVATED = "NeverActivated"


    class azure.mgmt.eventgrid.models.PartnerDestinationInfo(Model):
        azure_subscription_id: str
        endpoint_service_context: str
        endpoint_type: Union[str, PartnerEndpointType]
        name: str
        resource_group_name: str
        resource_move_change_history: list[ResourceMoveChangeHistory]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                azure_subscription_id: Optional[str] = ..., 
                endpoint_service_context: Optional[str] = ..., 
                name: Optional[str] = ..., 
                resource_group_name: Optional[str] = ..., 
                resource_move_change_history: Optional[List[ResourceMoveChangeHistory]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.PartnerDestinationProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        IDLE_DUE_TO_MIRRORED_CHANNEL_RESOURCE_DELETION = "IdleDueToMirroredChannelResourceDeletion"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.eventgrid.models.PartnerDestinationUpdateParameters(Model):
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
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.PartnerDestinationsListResult(Model):
        next_link: str
        value: list[PartnerDestination]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[PartnerDestination]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.PartnerDetails(Model):
        description: str
        long_description: str
        setup_uri: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                long_description: Optional[str] = ..., 
                setup_uri: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.PartnerEndpointType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        WEB_HOOK = "WebHook"


    class azure.mgmt.eventgrid.models.PartnerEventSubscriptionDestination(EventSubscriptionDestination):
        endpoint_type: Union[str, EndpointType]
        resource_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                resource_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.PartnerNamespace(TrackedResource):
        disable_local_auth: bool
        endpoint: str
        id: str
        inbound_ip_rules: list[InboundIpRule]
        location: str
        minimum_tls_version_allowed: Union[str, TlsVersion]
        name: str
        partner_registration_fully_qualified_id: str
        partner_topic_routing_mode: Union[str, PartnerTopicRoutingMode]
        private_endpoint_connections: list[PrivateEndpointConnection]
        provisioning_state: Union[str, PartnerNamespaceProvisioningState]
        public_network_access: Union[str, PublicNetworkAccess]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                disable_local_auth: bool = False, 
                inbound_ip_rules: Optional[List[InboundIpRule]] = ..., 
                location: str, 
                minimum_tls_version_allowed: Optional[Union[str, TlsVersion]] = ..., 
                partner_registration_fully_qualified_id: Optional[str] = ..., 
                partner_topic_routing_mode: Union[str, PartnerTopicRoutingMode] = "SourceEventAttribute", 
                public_network_access: Optional[Union[str, PublicNetworkAccess]] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.PartnerNamespaceProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.eventgrid.models.PartnerNamespaceRegenerateKeyRequest(Model):
        key_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                key_name: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.PartnerNamespaceSharedAccessKeys(Model):
        key1: str
        key2: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                key1: Optional[str] = ..., 
                key2: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.PartnerNamespaceUpdateParameters(Model):
        disable_local_auth: bool
        inbound_ip_rules: list[InboundIpRule]
        minimum_tls_version_allowed: Union[str, TlsVersion]
        public_network_access: Union[str, PublicNetworkAccess]
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                disable_local_auth: Optional[bool] = ..., 
                inbound_ip_rules: Optional[List[InboundIpRule]] = ..., 
                minimum_tls_version_allowed: Optional[Union[str, TlsVersion]] = ..., 
                public_network_access: Optional[Union[str, PublicNetworkAccess]] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.PartnerNamespacesListResult(Model):
        next_link: str
        value: list[PartnerNamespace]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[PartnerNamespace]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.PartnerRegistration(TrackedResource):
        id: str
        location: str
        name: str
        partner_registration_immutable_id: str
        provisioning_state: Union[str, PartnerRegistrationProvisioningState]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                location: str, 
                partner_registration_immutable_id: Optional[str] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.PartnerRegistrationProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.eventgrid.models.PartnerRegistrationUpdateParameters(Model):
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
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.PartnerRegistrationsListResult(Model):
        next_link: str
        value: list[PartnerRegistration]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[PartnerRegistration]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.PartnerTopic(TrackedResource):
        activation_state: Union[str, PartnerTopicActivationState]
        event_type_info: EventTypeInfo
        expiration_time_if_not_activated_utc: datetime
        id: str
        identity: IdentityInfo
        location: str
        message_for_activation: str
        name: str
        partner_registration_immutable_id: str
        partner_topic_friendly_description: str
        provisioning_state: Union[str, PartnerTopicProvisioningState]
        source: str
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                activation_state: Optional[Union[str, PartnerTopicActivationState]] = ..., 
                event_type_info: Optional[EventTypeInfo] = ..., 
                expiration_time_if_not_activated_utc: Optional[datetime] = ..., 
                identity: Optional[IdentityInfo] = ..., 
                location: str, 
                message_for_activation: Optional[str] = ..., 
                partner_registration_immutable_id: Optional[str] = ..., 
                partner_topic_friendly_description: Optional[str] = ..., 
                source: Optional[str] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.PartnerTopicActivationState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVATED = "Activated"
        DEACTIVATED = "Deactivated"
        NEVER_ACTIVATED = "NeverActivated"


    class azure.mgmt.eventgrid.models.PartnerTopicInfo(Model):
        azure_subscription_id: str
        event_type_info: EventTypeInfo
        name: str
        resource_group_name: str
        source: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                azure_subscription_id: Optional[str] = ..., 
                event_type_info: Optional[EventTypeInfo] = ..., 
                name: Optional[str] = ..., 
                resource_group_name: Optional[str] = ..., 
                source: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.PartnerTopicProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        IDLE_DUE_TO_MIRRORED_CHANNEL_RESOURCE_DELETION = "IdleDueToMirroredChannelResourceDeletion"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.eventgrid.models.PartnerTopicRoutingMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CHANNEL_NAME_HEADER = "ChannelNameHeader"
        SOURCE_EVENT_ATTRIBUTE = "SourceEventAttribute"


    class azure.mgmt.eventgrid.models.PartnerTopicUpdateParameters(Model):
        identity: IdentityInfo
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                identity: Optional[IdentityInfo] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.PartnerTopicsListResult(Model):
        next_link: str
        value: list[PartnerTopic]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[PartnerTopic]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.PartnerUpdateDestinationInfo(Model):
        endpoint_type: Union[str, PartnerEndpointType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.PartnerUpdateTopicInfo(Model):
        event_type_info: EventTypeInfo

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                event_type_info: Optional[EventTypeInfo] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.PermissionBinding(Resource):
        client_group_name: str
        description: str
        id: str
        name: str
        permission: Union[str, PermissionType]
        provisioning_state: Union[str, PermissionBindingProvisioningState]
        system_data: SystemData
        topic_space_name: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                client_group_name: Optional[str] = ..., 
                description: Optional[str] = ..., 
                permission: Optional[Union[str, PermissionType]] = ..., 
                topic_space_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.PermissionBindingProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETED = "Deleted"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.eventgrid.models.PermissionBindingsListResult(Model):
        next_link: str
        value: list[PermissionBinding]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[PermissionBinding]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.PermissionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PUBLISHER = "Publisher"
        SUBSCRIBER = "Subscriber"


    class azure.mgmt.eventgrid.models.PersistedConnectionStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPROVED = "Approved"
        DISCONNECTED = "Disconnected"
        PENDING = "Pending"
        REJECTED = "Rejected"


    class azure.mgmt.eventgrid.models.PrivateEndpoint(Model):
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
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.PrivateEndpointConnection(Resource):
        group_ids: list[str]
        id: str
        name: str
        private_endpoint: PrivateEndpoint
        private_link_service_connection_state: ConnectionState
        provisioning_state: Union[str, ResourceProvisioningState]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                group_ids: Optional[List[str]] = ..., 
                private_endpoint: Optional[PrivateEndpoint] = ..., 
                private_link_service_connection_state: Optional[ConnectionState] = ..., 
                provisioning_state: Optional[Union[str, ResourceProvisioningState]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.PrivateEndpointConnectionListResult(Model):
        next_link: str
        value: list[PrivateEndpointConnection]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[PrivateEndpointConnection]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.PrivateEndpointConnectionsParentType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DOMAINS = "domains"
        NAMESPACES = "namespaces"
        PARTNER_NAMESPACES = "partnerNamespaces"
        TOPICS = "topics"


    class azure.mgmt.eventgrid.models.PrivateLinkResource(Model):
        display_name: str
        group_id: str
        id: str
        name: str
        required_members: list[str]
        required_zone_names: list[str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                display_name: Optional[str] = ..., 
                group_id: Optional[str] = ..., 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                required_members: Optional[List[str]] = ..., 
                required_zone_names: Optional[List[str]] = ..., 
                type: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.PrivateLinkResourcesListResult(Model):
        next_link: str
        value: list[PrivateLinkResource]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[PrivateLinkResource]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.PublicNetworkAccess(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"
        SECURED_BY_PERIMETER = "SecuredByPerimeter"


    class azure.mgmt.eventgrid.models.PublisherType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CUSTOM = "Custom"


    class azure.mgmt.eventgrid.models.PushInfo(Model):
        dead_letter_destination_with_resource_identity: DeadLetterWithResourceIdentity
        delivery_with_resource_identity: DeliveryWithResourceIdentity
        destination: EventSubscriptionDestination
        event_time_to_live: str
        max_delivery_count: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                dead_letter_destination_with_resource_identity: Optional[DeadLetterWithResourceIdentity] = ..., 
                delivery_with_resource_identity: Optional[DeliveryWithResourceIdentity] = ..., 
                destination: Optional[EventSubscriptionDestination] = ..., 
                event_time_to_live: Optional[str] = ..., 
                max_delivery_count: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.QueueInfo(Model):
        dead_letter_destination_with_resource_identity: DeadLetterWithResourceIdentity
        event_time_to_live: timedelta
        max_delivery_count: int
        receive_lock_duration_in_seconds: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                dead_letter_destination_with_resource_identity: Optional[DeadLetterWithResourceIdentity] = ..., 
                event_time_to_live: Optional[timedelta] = ..., 
                max_delivery_count: Optional[int] = ..., 
                receive_lock_duration_in_seconds: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.ReadinessState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVATED = "Activated"
        NEVER_ACTIVATED = "NeverActivated"


    class azure.mgmt.eventgrid.models.Resource(Model):
        id: str
        name: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.ResourceAssociation(Model):
        access_mode: Union[str, NetworkSecurityPerimeterAssociationAccessMode]
        name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                access_mode: Optional[Union[str, NetworkSecurityPerimeterAssociationAccessMode]] = ..., 
                name: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.ResourceKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE = "Azure"
        AZURE_ARC = "AzureArc"


    class azure.mgmt.eventgrid.models.ResourceMoveChangeHistory(Model):
        azure_subscription_id: str
        changed_time_utc: datetime
        resource_group_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                azure_subscription_id: Optional[str] = ..., 
                changed_time_utc: Optional[datetime] = ..., 
                resource_group_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.ResourceProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.eventgrid.models.ResourceRegionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        GLOBAL_RESOURCE = "GlobalResource"
        REGIONAL_RESOURCE = "RegionalResource"


    class azure.mgmt.eventgrid.models.ResourceSku(Model):
        name: Union[str, Sku]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                name: Union[str, Sku] = "Basic", 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.RetryPolicy(Model):
        event_time_to_live_in_minutes: int
        max_delivery_attempts: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                event_time_to_live_in_minutes: int = 1440, 
                max_delivery_attempts: int = 30, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.RoutingEnrichments(Model):
        dynamic: list[DynamicRoutingEnrichment]
        static: list[StaticRoutingEnrichment]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                dynamic: Optional[List[DynamicRoutingEnrichment]] = ..., 
                static: Optional[List[StaticRoutingEnrichment]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.RoutingIdentityInfo(Model):
        type: Union[str, RoutingIdentityType]
        user_assigned_identity: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                type: Optional[Union[str, RoutingIdentityType]] = ..., 
                user_assigned_identity: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.RoutingIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.eventgrid.models.ServiceBusQueueEventSubscriptionDestination(EventSubscriptionDestination):
        delivery_attribute_mappings: list[DeliveryAttributeMapping]
        endpoint_type: Union[str, EndpointType]
        resource_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                delivery_attribute_mappings: Optional[List[DeliveryAttributeMapping]] = ..., 
                resource_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.ServiceBusTopicEventSubscriptionDestination(EventSubscriptionDestination):
        delivery_attribute_mappings: list[DeliveryAttributeMapping]
        endpoint_type: Union[str, EndpointType]
        resource_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                delivery_attribute_mappings: Optional[List[DeliveryAttributeMapping]] = ..., 
                resource_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.Sku(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BASIC = "Basic"
        PREMIUM = "Premium"


    class azure.mgmt.eventgrid.models.SkuName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        STANDARD = "Standard"


    class azure.mgmt.eventgrid.models.StaticDeliveryAttributeMapping(DeliveryAttributeMapping):
        is_secret: bool
        name: str
        type: Union[str, DeliveryAttributeMappingType]
        value: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                is_secret: bool = False, 
                name: Optional[str] = ..., 
                value: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.StaticRoutingEnrichment(Model):
        key: str
        value_type: Union[str, StaticRoutingEnrichmentType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                key: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.StaticRoutingEnrichmentType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        STRING = "String"


    class azure.mgmt.eventgrid.models.StaticStringRoutingEnrichment(StaticRoutingEnrichment):
        key: str
        value: str
        value_type: Union[str, StaticRoutingEnrichmentType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                key: Optional[str] = ..., 
                value: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.StorageBlobDeadLetterDestination(DeadLetterDestination):
        blob_container_name: str
        endpoint_type: Union[str, DeadLetterEndPointType]
        resource_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                blob_container_name: Optional[str] = ..., 
                resource_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.StorageQueueEventSubscriptionDestination(EventSubscriptionDestination):
        endpoint_type: Union[str, EndpointType]
        queue_message_time_to_live_in_seconds: int
        queue_name: str
        resource_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                queue_message_time_to_live_in_seconds: Optional[int] = ..., 
                queue_name: Optional[str] = ..., 
                resource_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.StringBeginsWithAdvancedFilter(AdvancedFilter):
        key: str
        operator_type: Union[str, AdvancedFilterOperatorType]
        values: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                key: Optional[str] = ..., 
                values: Optional[List[str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.StringBeginsWithFilter(Filter):
        key: str
        operator_type: Union[str, FilterOperatorType]
        values: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                key: Optional[str] = ..., 
                values: Optional[List[str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.StringContainsAdvancedFilter(AdvancedFilter):
        key: str
        operator_type: Union[str, AdvancedFilterOperatorType]
        values: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                key: Optional[str] = ..., 
                values: Optional[List[str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.StringContainsFilter(Filter):
        key: str
        operator_type: Union[str, FilterOperatorType]
        values: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                key: Optional[str] = ..., 
                values: Optional[List[str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.StringEndsWithAdvancedFilter(AdvancedFilter):
        key: str
        operator_type: Union[str, AdvancedFilterOperatorType]
        values: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                key: Optional[str] = ..., 
                values: Optional[List[str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.StringEndsWithFilter(Filter):
        key: str
        operator_type: Union[str, FilterOperatorType]
        values: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                key: Optional[str] = ..., 
                values: Optional[List[str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.StringInAdvancedFilter(AdvancedFilter):
        key: str
        operator_type: Union[str, AdvancedFilterOperatorType]
        values: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                key: Optional[str] = ..., 
                values: Optional[List[str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.StringInFilter(Filter):
        key: str
        operator_type: Union[str, FilterOperatorType]
        values: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                key: Optional[str] = ..., 
                values: Optional[List[str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.StringNotBeginsWithAdvancedFilter(AdvancedFilter):
        key: str
        operator_type: Union[str, AdvancedFilterOperatorType]
        values: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                key: Optional[str] = ..., 
                values: Optional[List[str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.StringNotBeginsWithFilter(Filter):
        key: str
        operator_type: Union[str, FilterOperatorType]
        values: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                key: Optional[str] = ..., 
                values: Optional[List[str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.StringNotContainsAdvancedFilter(AdvancedFilter):
        key: str
        operator_type: Union[str, AdvancedFilterOperatorType]
        values: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                key: Optional[str] = ..., 
                values: Optional[List[str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.StringNotContainsFilter(Filter):
        key: str
        operator_type: Union[str, FilterOperatorType]
        values: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                key: Optional[str] = ..., 
                values: Optional[List[str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.StringNotEndsWithAdvancedFilter(AdvancedFilter):
        key: str
        operator_type: Union[str, AdvancedFilterOperatorType]
        values: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                key: Optional[str] = ..., 
                values: Optional[List[str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.StringNotEndsWithFilter(Filter):
        key: str
        operator_type: Union[str, FilterOperatorType]
        values: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                key: Optional[str] = ..., 
                values: Optional[List[str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.StringNotInAdvancedFilter(AdvancedFilter):
        key: str
        operator_type: Union[str, AdvancedFilterOperatorType]
        values: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                key: Optional[str] = ..., 
                values: Optional[List[str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.StringNotInFilter(Filter):
        key: str
        operator_type: Union[str, FilterOperatorType]
        values: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                key: Optional[str] = ..., 
                values: Optional[List[str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.Subscription(Resource):
        delivery_configuration: DeliveryConfiguration
        event_delivery_schema: Union[str, DeliverySchema]
        expiration_time_utc: datetime
        filters_configuration: FiltersConfiguration
        id: str
        name: str
        provisioning_state: Union[str, SubscriptionProvisioningState]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                delivery_configuration: Optional[DeliveryConfiguration] = ..., 
                event_delivery_schema: Optional[Union[str, DeliverySchema]] = ..., 
                expiration_time_utc: Optional[datetime] = ..., 
                filters_configuration: Optional[FiltersConfiguration] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.SubscriptionFullUrl(Model):
        endpoint_url: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                endpoint_url: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.SubscriptionProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AWAITING_MANUAL_ACTION = "AwaitingManualAction"
        CANCELED = "Canceled"
        CREATE_FAILED = "CreateFailed"
        CREATING = "Creating"
        DELETED = "Deleted"
        DELETE_FAILED = "DeleteFailed"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATED_FAILED = "UpdatedFailed"
        UPDATING = "Updating"


    class azure.mgmt.eventgrid.models.SubscriptionUpdateParameters(Model):
        delivery_configuration: DeliveryConfiguration
        event_delivery_schema: Union[str, DeliverySchema]
        expiration_time_utc: datetime
        filters_configuration: FiltersConfiguration
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                delivery_configuration: Optional[DeliveryConfiguration] = ..., 
                event_delivery_schema: Optional[Union[str, DeliverySchema]] = ..., 
                expiration_time_utc: Optional[datetime] = ..., 
                filters_configuration: Optional[FiltersConfiguration] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.SubscriptionsListResult(Model):
        next_link: str
        value: list[Subscription]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[Subscription]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.SystemData(Model):
        created_at: datetime
        created_by: str
        created_by_type: Union[str, CreatedByType]
        last_modified_at: datetime
        last_modified_by: str
        last_modified_by_type: Union[str, CreatedByType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                created_at: Optional[datetime] = ..., 
                created_by: Optional[str] = ..., 
                created_by_type: Optional[Union[str, CreatedByType]] = ..., 
                last_modified_at: Optional[datetime] = ..., 
                last_modified_by: Optional[str] = ..., 
                last_modified_by_type: Optional[Union[str, CreatedByType]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.SystemTopic(TrackedResource):
        id: str
        identity: IdentityInfo
        location: str
        metric_resource_id: str
        name: str
        provisioning_state: Union[str, ResourceProvisioningState]
        source: str
        system_data: SystemData
        tags: dict[str, str]
        topic_type: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                identity: Optional[IdentityInfo] = ..., 
                location: str, 
                source: Optional[str] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                topic_type: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.SystemTopicUpdateParameters(Model):
        identity: IdentityInfo
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                identity: Optional[IdentityInfo] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.SystemTopicsListResult(Model):
        next_link: str
        value: list[SystemTopic]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[SystemTopic]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.TlsVersion(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ONE0 = "1.0"
        ONE1 = "1.1"
        ONE2 = "1.2"


    class azure.mgmt.eventgrid.models.Topic(TrackedResource):
        data_residency_boundary: Union[str, DataResidencyBoundary]
        disable_local_auth: bool
        endpoint: str
        event_type_info: EventTypeInfo
        extended_location: ExtendedLocation
        id: str
        identity: IdentityInfo
        inbound_ip_rules: list[InboundIpRule]
        input_schema: Union[str, InputSchema]
        input_schema_mapping: InputSchemaMapping
        kind: Union[str, ResourceKind]
        location: str
        metric_resource_id: str
        minimum_tls_version_allowed: Union[str, TlsVersion]
        name: str
        private_endpoint_connections: list[PrivateEndpointConnection]
        provisioning_state: Union[str, TopicProvisioningState]
        public_network_access: Union[str, PublicNetworkAccess]
        sku: ResourceSku
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                data_residency_boundary: Optional[Union[str, DataResidencyBoundary]] = ..., 
                disable_local_auth: bool = False, 
                event_type_info: Optional[EventTypeInfo] = ..., 
                extended_location: Optional[ExtendedLocation] = ..., 
                identity: Optional[IdentityInfo] = ..., 
                inbound_ip_rules: Optional[List[InboundIpRule]] = ..., 
                input_schema: Optional[Union[str, InputSchema]] = ..., 
                input_schema_mapping: Optional[InputSchemaMapping] = ..., 
                kind: Union[str, ResourceKind] = "Azure", 
                location: str, 
                minimum_tls_version_allowed: Optional[Union[str, TlsVersion]] = ..., 
                public_network_access: Optional[Union[str, PublicNetworkAccess]] = ..., 
                sku: Optional[ResourceSku] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.TopicProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.eventgrid.models.TopicRegenerateKeyRequest(Model):
        key_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                key_name: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.TopicSharedAccessKeys(Model):
        key1: str
        key2: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                key1: Optional[str] = ..., 
                key2: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.TopicSpace(Resource):
        description: str
        id: str
        name: str
        provisioning_state: Union[str, TopicSpaceProvisioningState]
        system_data: SystemData
        topic_templates: list[str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                topic_templates: Optional[List[str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.TopicSpaceProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETED = "Deleted"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.eventgrid.models.TopicSpacesConfiguration(Model):
        client_authentication: ClientAuthenticationSettings
        custom_domains: list[CustomDomainConfiguration]
        hostname: str
        maximum_client_sessions_per_authentication_name: int
        maximum_session_expiry_in_hours: int
        route_topic_resource_id: str
        routing_enrichments: RoutingEnrichments
        routing_identity_info: RoutingIdentityInfo
        state: Union[str, TopicSpacesConfigurationState]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                client_authentication: Optional[ClientAuthenticationSettings] = ..., 
                custom_domains: Optional[List[CustomDomainConfiguration]] = ..., 
                maximum_client_sessions_per_authentication_name: Optional[int] = ..., 
                maximum_session_expiry_in_hours: Optional[int] = ..., 
                route_topic_resource_id: Optional[str] = ..., 
                routing_enrichments: Optional[RoutingEnrichments] = ..., 
                routing_identity_info: Optional[RoutingIdentityInfo] = ..., 
                state: Optional[Union[str, TopicSpacesConfigurationState]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.TopicSpacesConfigurationState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.eventgrid.models.TopicSpacesListResult(Model):
        next_link: str
        value: list[TopicSpace]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[TopicSpace]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.TopicTypeAdditionalEnforcedPermission(Model):
        is_data_action: bool
        permission_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                is_data_action: Optional[bool] = ..., 
                permission_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.TopicTypeInfo(Resource):
        additional_enforced_permissions: list[TopicTypeAdditionalEnforcedPermission]
        are_regional_and_global_sources_supported: bool
        description: str
        display_name: str
        id: str
        name: str
        provider: str
        provisioning_state: Union[str, TopicTypeProvisioningState]
        resource_region_type: Union[str, ResourceRegionType]
        source_resource_format: str
        supported_locations: list[str]
        supported_scopes_for_source: Union[list[str, TopicTypeSourceScope]]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                additional_enforced_permissions: Optional[List[TopicTypeAdditionalEnforcedPermission]] = ..., 
                are_regional_and_global_sources_supported: Optional[bool] = ..., 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                provider: Optional[str] = ..., 
                provisioning_state: Optional[Union[str, TopicTypeProvisioningState]] = ..., 
                resource_region_type: Optional[Union[str, ResourceRegionType]] = ..., 
                source_resource_format: Optional[str] = ..., 
                supported_locations: Optional[List[str]] = ..., 
                supported_scopes_for_source: Optional[List[Union[str, TopicTypeSourceScope]]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.TopicTypeProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.eventgrid.models.TopicTypeSourceScope(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_SUBSCRIPTION = "AzureSubscription"
        MANAGEMENT_GROUP = "ManagementGroup"
        RESOURCE = "Resource"
        RESOURCE_GROUP = "ResourceGroup"


    class azure.mgmt.eventgrid.models.TopicTypesListResult(Model):
        value: list[TopicTypeInfo]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[TopicTypeInfo]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.TopicUpdateParameters(Model):
        data_residency_boundary: Union[str, DataResidencyBoundary]
        disable_local_auth: bool
        event_type_info: EventTypeInfo
        identity: IdentityInfo
        inbound_ip_rules: list[InboundIpRule]
        minimum_tls_version_allowed: Union[str, TlsVersion]
        public_network_access: Union[str, PublicNetworkAccess]
        sku: ResourceSku
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                data_residency_boundary: Optional[Union[str, DataResidencyBoundary]] = ..., 
                disable_local_auth: Optional[bool] = ..., 
                event_type_info: Optional[EventTypeInfo] = ..., 
                identity: Optional[IdentityInfo] = ..., 
                inbound_ip_rules: Optional[List[InboundIpRule]] = ..., 
                minimum_tls_version_allowed: Optional[Union[str, TlsVersion]] = ..., 
                public_network_access: Optional[Union[str, PublicNetworkAccess]] = ..., 
                sku: Optional[ResourceSku] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.TopicsConfiguration(Model):
        custom_domains: list[CustomDomainConfiguration]
        hostname: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                custom_domains: Optional[List[CustomDomainConfiguration]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.TopicsListResult(Model):
        next_link: str
        value: list[Topic]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[Topic]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.TrackedResource(Resource):
        id: str
        location: str
        name: str
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                location: str, 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.UpdateTopicSpacesConfigurationInfo(Model):
        client_authentication: ClientAuthenticationSettings
        custom_domains: list[CustomDomainConfiguration]
        maximum_client_sessions_per_authentication_name: int
        maximum_session_expiry_in_hours: int
        route_topic_resource_id: str
        routing_enrichments: RoutingEnrichments
        routing_identity_info: RoutingIdentityInfo
        state: Union[str, TopicSpacesConfigurationState]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                client_authentication: Optional[ClientAuthenticationSettings] = ..., 
                custom_domains: Optional[List[CustomDomainConfiguration]] = ..., 
                maximum_client_sessions_per_authentication_name: Optional[int] = ..., 
                maximum_session_expiry_in_hours: Optional[int] = ..., 
                route_topic_resource_id: Optional[str] = ..., 
                routing_enrichments: Optional[RoutingEnrichments] = ..., 
                routing_identity_info: Optional[RoutingIdentityInfo] = ..., 
                state: Optional[Union[str, TopicSpacesConfigurationState]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.UpdateTopicsConfigurationInfo(Model):
        custom_domains: list[CustomDomainConfiguration]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                custom_domains: Optional[List[CustomDomainConfiguration]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.UserIdentityProperties(Model):
        client_id: str
        principal_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                client_id: Optional[str] = ..., 
                principal_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.VerifiedPartner(Resource):
        id: str
        name: str
        organization_name: str
        partner_destination_details: PartnerDetails
        partner_display_name: str
        partner_registration_immutable_id: str
        partner_topic_details: PartnerDetails
        provisioning_state: Union[str, VerifiedPartnerProvisioningState]
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                organization_name: Optional[str] = ..., 
                partner_destination_details: Optional[PartnerDetails] = ..., 
                partner_display_name: Optional[str] = ..., 
                partner_registration_immutable_id: Optional[str] = ..., 
                partner_topic_details: Optional[PartnerDetails] = ..., 
                provisioning_state: Optional[Union[str, VerifiedPartnerProvisioningState]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.VerifiedPartnerProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.eventgrid.models.VerifiedPartnersListResult(Model):
        next_link: str
        value: list[VerifiedPartner]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[VerifiedPartner]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.WebHookEventSubscriptionDestination(EventSubscriptionDestination):
        azure_active_directory_application_id_or_uri: str
        azure_active_directory_tenant_id: str
        delivery_attribute_mappings: list[DeliveryAttributeMapping]
        endpoint_base_url: str
        endpoint_type: Union[str, EndpointType]
        endpoint_url: str
        max_events_per_batch: int
        minimum_tls_version_allowed: Union[str, TlsVersion]
        preferred_batch_size_in_kilobytes: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                azure_active_directory_application_id_or_uri: Optional[str] = ..., 
                azure_active_directory_tenant_id: Optional[str] = ..., 
                delivery_attribute_mappings: Optional[List[DeliveryAttributeMapping]] = ..., 
                endpoint_url: Optional[str] = ..., 
                max_events_per_batch: int = 1, 
                minimum_tls_version_allowed: Optional[Union[str, TlsVersion]] = ..., 
                preferred_batch_size_in_kilobytes: int = 64, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.WebhookAuthenticationSettings(Model):
        azure_active_directory_application_id_or_uri: str
        azure_active_directory_tenant_id: str
        endpoint_base_url: str
        endpoint_url: str
        identity: CustomWebhookAuthenticationManagedIdentity

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                azure_active_directory_application_id_or_uri: str, 
                azure_active_directory_tenant_id: str, 
                endpoint_base_url: Optional[str] = ..., 
                endpoint_url: str, 
                identity: CustomWebhookAuthenticationManagedIdentity, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.WebhookPartnerDestinationInfo(PartnerDestinationInfo):
        azure_subscription_id: str
        client_authentication: PartnerClientAuthentication
        endpoint_base_url: str
        endpoint_service_context: str
        endpoint_type: Union[str, PartnerEndpointType]
        endpoint_url: str
        name: str
        resource_group_name: str
        resource_move_change_history: list[ResourceMoveChangeHistory]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                azure_subscription_id: Optional[str] = ..., 
                client_authentication: Optional[PartnerClientAuthentication] = ..., 
                endpoint_base_url: Optional[str] = ..., 
                endpoint_service_context: Optional[str] = ..., 
                endpoint_url: Optional[str] = ..., 
                name: Optional[str] = ..., 
                resource_group_name: Optional[str] = ..., 
                resource_move_change_history: Optional[List[ResourceMoveChangeHistory]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.eventgrid.models.WebhookUpdatePartnerDestinationInfo(PartnerUpdateDestinationInfo):
        client_authentication: PartnerClientAuthentication
        endpoint_base_url: str
        endpoint_type: Union[str, PartnerEndpointType]
        endpoint_url: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                client_authentication: Optional[PartnerClientAuthentication] = ..., 
                endpoint_base_url: Optional[str] = ..., 
                endpoint_url: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


namespace azure.mgmt.eventgrid.operations

    class azure.mgmt.eventgrid.operations.CaCertificatesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                ca_certificate_name: str, 
                ca_certificate_info: CaCertificate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CaCertificate]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                ca_certificate_name: str, 
                ca_certificate_info: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CaCertificate]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                ca_certificate_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                ca_certificate_name: str, 
                **kwargs: Any
            ) -> CaCertificate: ...

        @distributed_trace
        def list_by_namespace(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> ItemPaged[CaCertificate]: ...


    class azure.mgmt.eventgrid.operations.ChannelsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                partner_namespace_name: str, 
                channel_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                partner_namespace_name: str, 
                channel_name: str, 
                channel_info: Channel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Channel: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                partner_namespace_name: str, 
                channel_name: str, 
                channel_info: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Channel: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                partner_namespace_name: str, 
                channel_name: str, 
                **kwargs: Any
            ) -> Channel: ...

        @distributed_trace
        def get_full_url(
                self, 
                resource_group_name: str, 
                partner_namespace_name: str, 
                channel_name: str, 
                **kwargs: Any
            ) -> EventSubscriptionFullUrl: ...

        @distributed_trace
        def list_by_partner_namespace(
                self, 
                resource_group_name: str, 
                partner_namespace_name: str, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> ItemPaged[Channel]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                partner_namespace_name: str, 
                channel_name: str, 
                channel_update_parameters: ChannelUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                partner_namespace_name: str, 
                channel_name: str, 
                channel_update_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.eventgrid.operations.ClientGroupsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                client_group_name: str, 
                client_group_info: ClientGroup, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ClientGroup]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                client_group_name: str, 
                client_group_info: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ClientGroup]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                client_group_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                client_group_name: str, 
                **kwargs: Any
            ) -> ClientGroup: ...

        @distributed_trace
        def list_by_namespace(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> ItemPaged[ClientGroup]: ...


    class azure.mgmt.eventgrid.operations.ClientsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                client_name: str, 
                client_info: Client, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Client]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                client_name: str, 
                client_info: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Client]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                client_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                client_name: str, 
                **kwargs: Any
            ) -> Client: ...

        @distributed_trace
        def list_by_namespace(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> ItemPaged[Client]: ...


    class azure.mgmt.eventgrid.operations.DomainEventSubscriptionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                event_subscription_name: str, 
                event_subscription_info: EventSubscription, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EventSubscription]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                event_subscription_name: str, 
                event_subscription_info: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EventSubscription]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                event_subscription_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                event_subscription_name: str, 
                event_subscription_update_parameters: EventSubscriptionUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EventSubscription]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                event_subscription_name: str, 
                event_subscription_update_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EventSubscription]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                event_subscription_name: str, 
                **kwargs: Any
            ) -> EventSubscription: ...

        @distributed_trace
        def get_delivery_attributes(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                event_subscription_name: str, 
                **kwargs: Any
            ) -> DeliveryAttributeListResult: ...

        @distributed_trace
        def get_full_url(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                event_subscription_name: str, 
                **kwargs: Any
            ) -> EventSubscriptionFullUrl: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> ItemPaged[EventSubscription]: ...


    class azure.mgmt.eventgrid.operations.DomainTopicEventSubscriptionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                topic_name: str, 
                event_subscription_name: str, 
                event_subscription_info: EventSubscription, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EventSubscription]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                topic_name: str, 
                event_subscription_name: str, 
                event_subscription_info: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EventSubscription]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                topic_name: str, 
                event_subscription_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                topic_name: str, 
                event_subscription_name: str, 
                event_subscription_update_parameters: EventSubscriptionUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EventSubscription]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                topic_name: str, 
                event_subscription_name: str, 
                event_subscription_update_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EventSubscription]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                topic_name: str, 
                event_subscription_name: str, 
                **kwargs: Any
            ) -> EventSubscription: ...

        @distributed_trace
        def get_delivery_attributes(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                topic_name: str, 
                event_subscription_name: str, 
                **kwargs: Any
            ) -> DeliveryAttributeListResult: ...

        @distributed_trace
        def get_full_url(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                topic_name: str, 
                event_subscription_name: str, 
                **kwargs: Any
            ) -> EventSubscriptionFullUrl: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                topic_name: str, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> ItemPaged[EventSubscription]: ...


    class azure.mgmt.eventgrid.operations.DomainTopicsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                domain_topic_name: str, 
                **kwargs: Any
            ) -> LROPoller[DomainTopic]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                domain_topic_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                domain_topic_name: str, 
                **kwargs: Any
            ) -> DomainTopic: ...

        @distributed_trace
        def list_by_domain(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> ItemPaged[DomainTopic]: ...


    class azure.mgmt.eventgrid.operations.DomainsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                domain_info: Domain, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Domain]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                domain_info: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Domain]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                domain_update_parameters: DomainUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Domain]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                domain_update_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Domain]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                **kwargs: Any
            ) -> Domain: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> ItemPaged[Domain]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> ItemPaged[Domain]: ...

        @distributed_trace
        def list_shared_access_keys(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                **kwargs: Any
            ) -> DomainSharedAccessKeys: ...

        @overload
        def regenerate_key(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                regenerate_key_request: DomainRegenerateKeyRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DomainSharedAccessKeys: ...

        @overload
        def regenerate_key(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                regenerate_key_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DomainSharedAccessKeys: ...


    class azure.mgmt.eventgrid.operations.EventSubscriptionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                scope: str, 
                event_subscription_name: str, 
                event_subscription_info: EventSubscription, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EventSubscription]: ...

        @overload
        def begin_create_or_update(
                self, 
                scope: str, 
                event_subscription_name: str, 
                event_subscription_info: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EventSubscription]: ...

        @distributed_trace
        def begin_delete(
                self, 
                scope: str, 
                event_subscription_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                scope: str, 
                event_subscription_name: str, 
                event_subscription_update_parameters: EventSubscriptionUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EventSubscription]: ...

        @overload
        def begin_update(
                self, 
                scope: str, 
                event_subscription_name: str, 
                event_subscription_update_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EventSubscription]: ...

        @distributed_trace
        def get(
                self, 
                scope: str, 
                event_subscription_name: str, 
                **kwargs: Any
            ) -> EventSubscription: ...

        @distributed_trace
        def get_delivery_attributes(
                self, 
                scope: str, 
                event_subscription_name: str, 
                **kwargs: Any
            ) -> DeliveryAttributeListResult: ...

        @distributed_trace
        def get_full_url(
                self, 
                scope: str, 
                event_subscription_name: str, 
                **kwargs: Any
            ) -> EventSubscriptionFullUrl: ...

        @distributed_trace
        def list_by_domain_topic(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                topic_name: str, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> ItemPaged[EventSubscription]: ...

        @distributed_trace
        def list_by_resource(
                self, 
                resource_group_name: str, 
                provider_namespace: str, 
                resource_type_name: str, 
                resource_name: str, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> ItemPaged[EventSubscription]: ...

        @distributed_trace
        def list_global_by_resource_group(
                self, 
                resource_group_name: str, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> ItemPaged[EventSubscription]: ...

        @distributed_trace
        def list_global_by_resource_group_for_topic_type(
                self, 
                resource_group_name: str, 
                topic_type_name: str, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> ItemPaged[EventSubscription]: ...

        @distributed_trace
        def list_global_by_subscription(
                self, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> ItemPaged[EventSubscription]: ...

        @distributed_trace
        def list_global_by_subscription_for_topic_type(
                self, 
                topic_type_name: str, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> ItemPaged[EventSubscription]: ...

        @distributed_trace
        def list_regional_by_resource_group(
                self, 
                resource_group_name: str, 
                location: str, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> ItemPaged[EventSubscription]: ...

        @distributed_trace
        def list_regional_by_resource_group_for_topic_type(
                self, 
                resource_group_name: str, 
                location: str, 
                topic_type_name: str, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> ItemPaged[EventSubscription]: ...

        @distributed_trace
        def list_regional_by_subscription(
                self, 
                location: str, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> ItemPaged[EventSubscription]: ...

        @distributed_trace
        def list_regional_by_subscription_for_topic_type(
                self, 
                location: str, 
                topic_type_name: str, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> ItemPaged[EventSubscription]: ...


    class azure.mgmt.eventgrid.operations.ExtensionTopicsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                scope: str, 
                **kwargs: Any
            ) -> ExtensionTopic: ...


    class azure.mgmt.eventgrid.operations.NamespaceTopicEventSubscriptionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_name: str, 
                event_subscription_name: str, 
                event_subscription_info: Subscription, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Subscription]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_name: str, 
                event_subscription_name: str, 
                event_subscription_info: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Subscription]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_name: str, 
                event_subscription_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_name: str, 
                event_subscription_name: str, 
                event_subscription_update_parameters: SubscriptionUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Subscription]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_name: str, 
                event_subscription_name: str, 
                event_subscription_update_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Subscription]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_name: str, 
                event_subscription_name: str, 
                **kwargs: Any
            ) -> Subscription: ...

        @distributed_trace
        def get_delivery_attributes(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_name: str, 
                event_subscription_name: str, 
                **kwargs: Any
            ) -> DeliveryAttributeListResult: ...

        @distributed_trace
        def get_full_url(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_name: str, 
                event_subscription_name: str, 
                **kwargs: Any
            ) -> SubscriptionFullUrl: ...

        @distributed_trace
        def list_by_namespace_topic(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_name: str, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> ItemPaged[Subscription]: ...


    class azure.mgmt.eventgrid.operations.NamespaceTopicsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_name: str, 
                namespace_topic_info: NamespaceTopic, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NamespaceTopic]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_name: str, 
                namespace_topic_info: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NamespaceTopic]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_regenerate_key(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_name: str, 
                regenerate_key_request: TopicRegenerateKeyRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[TopicSharedAccessKeys]: ...

        @overload
        def begin_regenerate_key(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_name: str, 
                regenerate_key_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[TopicSharedAccessKeys]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_name: str, 
                namespace_topic_update_parameters: NamespaceTopicUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NamespaceTopic]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_name: str, 
                namespace_topic_update_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NamespaceTopic]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_name: str, 
                **kwargs: Any
            ) -> NamespaceTopic: ...

        @distributed_trace
        def list_by_namespace(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> ItemPaged[NamespaceTopic]: ...

        @distributed_trace
        def list_shared_access_keys(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_name: str, 
                **kwargs: Any
            ) -> TopicSharedAccessKeys: ...


    class azure.mgmt.eventgrid.operations.NamespacesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                namespace_info: Namespace, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Namespace]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                namespace_info: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Namespace]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_regenerate_key(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                regenerate_key_request: NamespaceRegenerateKeyRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NamespaceSharedAccessKeys]: ...

        @overload
        def begin_regenerate_key(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                regenerate_key_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NamespaceSharedAccessKeys]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                namespace_update_parameters: NamespaceUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Namespace]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                namespace_update_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Namespace]: ...

        @distributed_trace
        def begin_validate_custom_domain_ownership(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                **kwargs: Any
            ) -> LROPoller[CustomDomainOwnershipValidationResult]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                **kwargs: Any
            ) -> Namespace: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> ItemPaged[Namespace]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> ItemPaged[Namespace]: ...

        @distributed_trace
        def list_shared_access_keys(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                **kwargs: Any
            ) -> NamespaceSharedAccessKeys: ...


    class azure.mgmt.eventgrid.operations.NetworkSecurityPerimeterConfigurationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_reconcile(
                self, 
                resource_group_name: str, 
                resource_type: Union[str, NetworkSecurityPerimeterResourceType], 
                resource_name: str, 
                perimeter_guid: str, 
                association_name: str, 
                **kwargs: Any
            ) -> LROPoller[NetworkSecurityPerimeterConfiguration]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                resource_type: Union[str, NetworkSecurityPerimeterResourceType], 
                resource_name: str, 
                perimeter_guid: str, 
                association_name: str, 
                **kwargs: Any
            ) -> NetworkSecurityPerimeterConfiguration: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                resource_type: Union[str, NetworkSecurityPerimeterResourceType], 
                resource_name: str, 
                **kwargs: Any
            ) -> ItemPaged[NetworkSecurityPerimeterConfiguration]: ...


    class azure.mgmt.eventgrid.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


    class azure.mgmt.eventgrid.operations.PartnerConfigurationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def authorize_partner(
                self, 
                resource_group_name: str, 
                partner_info: Partner, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PartnerConfiguration: ...

        @overload
        def authorize_partner(
                self, 
                resource_group_name: str, 
                partner_info: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PartnerConfiguration: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                partner_configuration_info: PartnerConfiguration, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PartnerConfiguration]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                partner_configuration_info: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PartnerConfiguration]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                partner_configuration_update_parameters: PartnerConfigurationUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PartnerConfiguration]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                partner_configuration_update_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PartnerConfiguration]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> PartnerConfiguration: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[PartnerConfiguration]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> ItemPaged[PartnerConfiguration]: ...

        @overload
        def unauthorize_partner(
                self, 
                resource_group_name: str, 
                partner_info: Partner, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PartnerConfiguration: ...

        @overload
        def unauthorize_partner(
                self, 
                resource_group_name: str, 
                partner_info: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PartnerConfiguration: ...


    class azure.mgmt.eventgrid.operations.PartnerDestinationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def activate(
                self, 
                resource_group_name: str, 
                partner_destination_name: str, 
                **kwargs: Any
            ) -> PartnerDestination: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                partner_destination_name: str, 
                partner_destination: PartnerDestination, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PartnerDestination]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                partner_destination_name: str, 
                partner_destination: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PartnerDestination]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                partner_destination_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                partner_destination_name: str, 
                partner_destination_update_parameters: PartnerDestinationUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PartnerDestination]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                partner_destination_name: str, 
                partner_destination_update_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PartnerDestination]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                partner_destination_name: str, 
                **kwargs: Any
            ) -> PartnerDestination: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> ItemPaged[PartnerDestination]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> ItemPaged[PartnerDestination]: ...


    class azure.mgmt.eventgrid.operations.PartnerNamespacesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                partner_namespace_name: str, 
                partner_namespace_info: PartnerNamespace, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PartnerNamespace]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                partner_namespace_name: str, 
                partner_namespace_info: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PartnerNamespace]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                partner_namespace_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                partner_namespace_name: str, 
                partner_namespace_update_parameters: PartnerNamespaceUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PartnerNamespace]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                partner_namespace_name: str, 
                partner_namespace_update_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PartnerNamespace]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                partner_namespace_name: str, 
                **kwargs: Any
            ) -> PartnerNamespace: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> ItemPaged[PartnerNamespace]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> ItemPaged[PartnerNamespace]: ...

        @distributed_trace
        def list_shared_access_keys(
                self, 
                resource_group_name: str, 
                partner_namespace_name: str, 
                **kwargs: Any
            ) -> PartnerNamespaceSharedAccessKeys: ...

        @overload
        def regenerate_key(
                self, 
                resource_group_name: str, 
                partner_namespace_name: str, 
                regenerate_key_request: PartnerNamespaceRegenerateKeyRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PartnerNamespaceSharedAccessKeys: ...

        @overload
        def regenerate_key(
                self, 
                resource_group_name: str, 
                partner_namespace_name: str, 
                regenerate_key_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PartnerNamespaceSharedAccessKeys: ...


    class azure.mgmt.eventgrid.operations.PartnerRegistrationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                partner_registration_name: str, 
                partner_registration_info: PartnerRegistration, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PartnerRegistration]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                partner_registration_name: str, 
                partner_registration_info: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PartnerRegistration]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                partner_registration_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                partner_registration_name: str, 
                partner_registration_update_parameters: PartnerRegistrationUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PartnerRegistration]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                partner_registration_name: str, 
                partner_registration_update_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PartnerRegistration]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                partner_registration_name: str, 
                **kwargs: Any
            ) -> PartnerRegistration: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> ItemPaged[PartnerRegistration]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> ItemPaged[PartnerRegistration]: ...


    class azure.mgmt.eventgrid.operations.PartnerTopicEventSubscriptionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                partner_topic_name: str, 
                event_subscription_name: str, 
                event_subscription_info: EventSubscription, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EventSubscription]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                partner_topic_name: str, 
                event_subscription_name: str, 
                event_subscription_info: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EventSubscription]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                partner_topic_name: str, 
                event_subscription_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                partner_topic_name: str, 
                event_subscription_name: str, 
                event_subscription_update_parameters: EventSubscriptionUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EventSubscription]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                partner_topic_name: str, 
                event_subscription_name: str, 
                event_subscription_update_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EventSubscription]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                partner_topic_name: str, 
                event_subscription_name: str, 
                **kwargs: Any
            ) -> EventSubscription: ...

        @distributed_trace
        def get_delivery_attributes(
                self, 
                resource_group_name: str, 
                partner_topic_name: str, 
                event_subscription_name: str, 
                **kwargs: Any
            ) -> DeliveryAttributeListResult: ...

        @distributed_trace
        def get_full_url(
                self, 
                resource_group_name: str, 
                partner_topic_name: str, 
                event_subscription_name: str, 
                **kwargs: Any
            ) -> EventSubscriptionFullUrl: ...

        @distributed_trace
        def list_by_partner_topic(
                self, 
                resource_group_name: str, 
                partner_topic_name: str, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> ItemPaged[EventSubscription]: ...


    class azure.mgmt.eventgrid.operations.PartnerTopicsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def activate(
                self, 
                resource_group_name: str, 
                partner_topic_name: str, 
                **kwargs: Any
            ) -> PartnerTopic: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                partner_topic_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                partner_topic_name: str, 
                partner_topic_info: PartnerTopic, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PartnerTopic: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                partner_topic_name: str, 
                partner_topic_info: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PartnerTopic: ...

        @distributed_trace
        def deactivate(
                self, 
                resource_group_name: str, 
                partner_topic_name: str, 
                **kwargs: Any
            ) -> PartnerTopic: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                partner_topic_name: str, 
                **kwargs: Any
            ) -> PartnerTopic: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> ItemPaged[PartnerTopic]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> ItemPaged[PartnerTopic]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                partner_topic_name: str, 
                partner_topic_update_parameters: PartnerTopicUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Optional[PartnerTopic]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                partner_topic_name: str, 
                partner_topic_update_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Optional[PartnerTopic]: ...


    class azure.mgmt.eventgrid.operations.PermissionBindingsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                permission_binding_name: str, 
                permission_binding_info: PermissionBinding, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PermissionBinding]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                permission_binding_name: str, 
                permission_binding_info: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PermissionBinding]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                permission_binding_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                permission_binding_name: str, 
                **kwargs: Any
            ) -> PermissionBinding: ...

        @distributed_trace
        def list_by_namespace(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> ItemPaged[PermissionBinding]: ...


    class azure.mgmt.eventgrid.operations.PrivateEndpointConnectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                parent_type: Union[str, PrivateEndpointConnectionsParentType], 
                parent_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                parent_type: Union[str, PrivateEndpointConnectionsParentType], 
                parent_name: str, 
                private_endpoint_connection_name: str, 
                private_endpoint_connection: PrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrivateEndpointConnection]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                parent_type: Union[str, PrivateEndpointConnectionsParentType], 
                parent_name: str, 
                private_endpoint_connection_name: str, 
                private_endpoint_connection: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrivateEndpointConnection]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                parent_type: Union[str, PrivateEndpointConnectionsParentType], 
                parent_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @distributed_trace
        def list_by_resource(
                self, 
                resource_group_name: str, 
                parent_type: Union[str, PrivateEndpointConnectionsParentType], 
                parent_name: str, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> ItemPaged[PrivateEndpointConnection]: ...


    class azure.mgmt.eventgrid.operations.PrivateLinkResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                parent_type: str, 
                parent_name: str, 
                private_link_resource_name: str, 
                **kwargs: Any
            ) -> PrivateLinkResource: ...

        @distributed_trace
        def list_by_resource(
                self, 
                resource_group_name: str, 
                parent_type: str, 
                parent_name: str, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> ItemPaged[PrivateLinkResource]: ...


    class azure.mgmt.eventgrid.operations.SystemTopicEventSubscriptionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                system_topic_name: str, 
                event_subscription_name: str, 
                event_subscription_info: EventSubscription, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EventSubscription]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                system_topic_name: str, 
                event_subscription_name: str, 
                event_subscription_info: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EventSubscription]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                system_topic_name: str, 
                event_subscription_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                system_topic_name: str, 
                event_subscription_name: str, 
                event_subscription_update_parameters: EventSubscriptionUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EventSubscription]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                system_topic_name: str, 
                event_subscription_name: str, 
                event_subscription_update_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EventSubscription]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                system_topic_name: str, 
                event_subscription_name: str, 
                **kwargs: Any
            ) -> EventSubscription: ...

        @distributed_trace
        def get_delivery_attributes(
                self, 
                resource_group_name: str, 
                system_topic_name: str, 
                event_subscription_name: str, 
                **kwargs: Any
            ) -> DeliveryAttributeListResult: ...

        @distributed_trace
        def get_full_url(
                self, 
                resource_group_name: str, 
                system_topic_name: str, 
                event_subscription_name: str, 
                **kwargs: Any
            ) -> EventSubscriptionFullUrl: ...

        @distributed_trace
        def list_by_system_topic(
                self, 
                resource_group_name: str, 
                system_topic_name: str, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> ItemPaged[EventSubscription]: ...


    class azure.mgmt.eventgrid.operations.SystemTopicsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                system_topic_name: str, 
                system_topic_info: SystemTopic, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SystemTopic]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                system_topic_name: str, 
                system_topic_info: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SystemTopic]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                system_topic_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                system_topic_name: str, 
                system_topic_update_parameters: SystemTopicUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SystemTopic]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                system_topic_name: str, 
                system_topic_update_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SystemTopic]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                system_topic_name: str, 
                **kwargs: Any
            ) -> SystemTopic: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> ItemPaged[SystemTopic]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> ItemPaged[SystemTopic]: ...


    class azure.mgmt.eventgrid.operations.TopicEventSubscriptionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                topic_name: str, 
                event_subscription_name: str, 
                event_subscription_info: EventSubscription, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EventSubscription]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                topic_name: str, 
                event_subscription_name: str, 
                event_subscription_info: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EventSubscription]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                topic_name: str, 
                event_subscription_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                topic_name: str, 
                event_subscription_name: str, 
                event_subscription_update_parameters: EventSubscriptionUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EventSubscription]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                topic_name: str, 
                event_subscription_name: str, 
                event_subscription_update_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EventSubscription]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                topic_name: str, 
                event_subscription_name: str, 
                **kwargs: Any
            ) -> EventSubscription: ...

        @distributed_trace
        def get_delivery_attributes(
                self, 
                resource_group_name: str, 
                topic_name: str, 
                event_subscription_name: str, 
                **kwargs: Any
            ) -> DeliveryAttributeListResult: ...

        @distributed_trace
        def get_full_url(
                self, 
                resource_group_name: str, 
                topic_name: str, 
                event_subscription_name: str, 
                **kwargs: Any
            ) -> EventSubscriptionFullUrl: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                topic_name: str, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> ItemPaged[EventSubscription]: ...


    class azure.mgmt.eventgrid.operations.TopicSpacesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_space_name: str, 
                topic_space_info: TopicSpace, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[TopicSpace]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_space_name: str, 
                topic_space_info: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[TopicSpace]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_space_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_space_name: str, 
                **kwargs: Any
            ) -> TopicSpace: ...

        @distributed_trace
        def list_by_namespace(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> ItemPaged[TopicSpace]: ...


    class azure.mgmt.eventgrid.operations.TopicTypesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                topic_type_name: str, 
                **kwargs: Any
            ) -> TopicTypeInfo: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[TopicTypeInfo]: ...

        @distributed_trace
        def list_event_types(
                self, 
                topic_type_name: str, 
                **kwargs: Any
            ) -> ItemPaged[EventType]: ...


    class azure.mgmt.eventgrid.operations.TopicsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                topic_name: str, 
                topic_info: Topic, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Topic]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                topic_name: str, 
                topic_info: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Topic]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                topic_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_regenerate_key(
                self, 
                resource_group_name: str, 
                topic_name: str, 
                regenerate_key_request: TopicRegenerateKeyRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[TopicSharedAccessKeys]: ...

        @overload
        def begin_regenerate_key(
                self, 
                resource_group_name: str, 
                topic_name: str, 
                regenerate_key_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[TopicSharedAccessKeys]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                topic_name: str, 
                topic_update_parameters: TopicUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Topic]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                topic_name: str, 
                topic_update_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Topic]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                topic_name: str, 
                **kwargs: Any
            ) -> Topic: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> ItemPaged[Topic]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> ItemPaged[Topic]: ...

        @distributed_trace
        def list_event_types(
                self, 
                resource_group_name: str, 
                provider_namespace: str, 
                resource_type_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> ItemPaged[EventType]: ...

        @distributed_trace
        def list_shared_access_keys(
                self, 
                resource_group_name: str, 
                topic_name: str, 
                **kwargs: Any
            ) -> TopicSharedAccessKeys: ...


    class azure.mgmt.eventgrid.operations.VerifiedPartnersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                verified_partner_name: str, 
                **kwargs: Any
            ) -> VerifiedPartner: ...

        @distributed_trace
        def list(
                self, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> ItemPaged[VerifiedPartner]: ...


```