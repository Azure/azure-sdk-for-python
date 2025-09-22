# Release History

## 39.1.0 (2025-08-20)

### Features Added

  - Model `ManagedCluster` added property `kind`
  - Enum `ManagedClusterSKUName` added member `AUTOMATIC`
  - Enum `OSSKU` added member `AZURE_LINUX3`

## 39.0.0 (2025-07-21)

### Features Added

  - Added enum `IpFamily`

### Breaking Changes

  - This package now only targets the latest Api-Version available on Azure and removes APIs of other Api-Version. After this change, the package can have much smaller size. If your application requires a specific and non-latest Api-Version, it's recommended to pin this package to the previous released version; If your application always only use latest Api-Version, please ignore this change.
  - Deleted or renamed client operation group `ContainerServiceClient.container_service`
  - Deleted or renamed client operation group `ContainerServiceClient.managed_namespaces`
  - Deleted or renamed client operation group `ContainerServiceClient.operation_status_result`
  - Deleted or renamed client operation group `ContainerServiceClient.managed_cluster_snapshots`
  - Deleted or renamed client operation group `ContainerServiceClient.load_balancers`
  - Model `AdvancedNetworkingSecurity` deleted or renamed its instance variable `advanced_network_policies`
  - Model `AdvancedNetworkingSecurity` deleted or renamed its instance variable `transit_encryption`
  - Model `AgentPool` deleted or renamed its instance variable `enable_custom_ca_trust`
  - Model `AgentPool` deleted or renamed its instance variable `node_initialization_taints`
  - Model `AgentPool` deleted or renamed its instance variable `artifact_streaming_profile`
  - Model `AgentPool` deleted or renamed its instance variable `local_dns_profile`
  - Deleted or renamed enum value `AgentPoolMode.MACHINES`
  - Deleted or renamed enum value `AgentPoolMode.MANAGED_SYSTEM`
  - Model `AgentPoolSecurityProfile` deleted or renamed its instance variable `ssh_access`
  - Model `AgentPoolUpgradeProfile` deleted or renamed its instance variable `components_by_releases`
  - Model `AgentPoolUpgradeProfilePropertiesUpgradesItem` deleted or renamed its instance variable `is_out_of_support`
  - Model `AgentPoolUpgradeSettings` deleted or renamed its instance variable `max_blocked_nodes`
  - Model `ContainerServiceNetworkProfile` deleted or renamed its instance variable `pod_link_local_access`
  - Model `ContainerServiceNetworkProfile` deleted or renamed its instance variable `kube_proxy_config`
  - Model `GPUProfile` deleted or renamed its instance variable `driver_type`
  - Model `IstioEgressGateway` deleted or renamed its instance variable `name`
  - Model `IstioEgressGateway` deleted or renamed its instance variable `namespace`
  - Model `IstioEgressGateway` deleted or renamed its instance variable `gateway_configuration_name`
  - Model `KubeletConfig` deleted or renamed its instance variable `seccomp_default`
  - Model `MachineNetworkProperties` deleted or renamed its instance variable `vnet_subnet_id`
  - Model `MachineNetworkProperties` deleted or renamed its instance variable `pod_subnet_id`
  - Model `MachineNetworkProperties` deleted or renamed its instance variable `enable_node_public_ip`
  - Model `MachineNetworkProperties` deleted or renamed its instance variable `node_public_ip_prefix_id`
  - Model `MachineNetworkProperties` deleted or renamed its instance variable `node_public_ip_tags`
  - Model `MachineProperties` deleted or renamed its instance variable `hardware`
  - Model `MachineProperties` deleted or renamed its instance variable `operating_system`
  - Model `MachineProperties` deleted or renamed its instance variable `kubernetes`
  - Model `MachineProperties` deleted or renamed its instance variable `mode`
  - Model `MachineProperties` deleted or renamed its instance variable `security`
  - Model `MachineProperties` deleted or renamed its instance variable `priority`
  - Model `MachineProperties` deleted or renamed its instance variable `node_image_version`
  - Model `MachineProperties` deleted or renamed its instance variable `provisioning_state`
  - Model `MachineProperties` deleted or renamed its instance variable `tags`
  - Model `MachineProperties` deleted or renamed its instance variable `e_tag`
  - Model `MachineProperties` deleted or renamed its instance variable `status`
  - Model `ManagedCluster` deleted or renamed its instance variable `kind`
  - Model `ManagedCluster` deleted or renamed its instance variable `creation_data`
  - Model `ManagedCluster` deleted or renamed its instance variable `enable_namespace_resources`
  - Model `ManagedCluster` deleted or renamed its instance variable `scheduler_profile`
  - Model `ManagedClusterAgentPoolProfile` deleted or renamed its instance variable `enable_custom_ca_trust`
  - Model `ManagedClusterAgentPoolProfile` deleted or renamed its instance variable `node_initialization_taints`
  - Model `ManagedClusterAgentPoolProfile` deleted or renamed its instance variable `artifact_streaming_profile`
  - Model `ManagedClusterAgentPoolProfile` deleted or renamed its instance variable `local_dns_profile`
  - Model `ManagedClusterAgentPoolProfileProperties` deleted or renamed its instance variable `enable_custom_ca_trust`
  - Model `ManagedClusterAgentPoolProfileProperties` deleted or renamed its instance variable `node_initialization_taints`
  - Model `ManagedClusterAgentPoolProfileProperties` deleted or renamed its instance variable `artifact_streaming_profile`
  - Model `ManagedClusterAgentPoolProfileProperties` deleted or renamed its instance variable `local_dns_profile`
  - Model `ManagedClusterAzureMonitorProfile` deleted or renamed its instance variable `container_insights`
  - Model `ManagedClusterAzureMonitorProfile` deleted or renamed its instance variable `app_monitoring`
  - Model `ManagedClusterHTTPProxyConfig` deleted or renamed its instance variable `effective_no_proxy`
  - Model `ManagedClusterHTTPProxyConfig` deleted or renamed its instance variable `enabled`
  - Model `ManagedClusterLoadBalancerProfile` deleted or renamed its instance variable `cluster_service_load_balancer_health_probe_mode`
  - Model `ManagedClusterPoolUpgradeProfile` deleted or renamed its instance variable `components_by_releases`
  - Model `ManagedClusterPoolUpgradeProfileUpgradesItem` deleted or renamed its instance variable `is_out_of_support`
  - Deleted or renamed enum value `ManagedClusterSKUName.AUTOMATIC`
  - Model `ManagedClusterSecurityProfile` deleted or renamed its instance variable `image_integrity`
  - Model `ManagedClusterSecurityProfile` deleted or renamed its instance variable `node_restriction`
  - Model `ManagedClusterSecurityProfileDefender` deleted or renamed its instance variable `security_gating`
  - Model `ManagedClusterStorageProfileDiskCSIDriver` deleted or renamed its instance variable `version`
  - Model `ManagedClusterWorkloadAutoScalerProfileVerticalPodAutoscaler` deleted or renamed its instance variable `addon_autoscaling`
  - Deleted or renamed enum value `OSSKU.MARINER`
  - Deleted or renamed enum value `OSSKU.UBUNTU2404`
  - Deleted or renamed enum value `OSSKU.WINDOWS_ANNUAL`
  - Deleted or renamed enum value `PublicNetworkAccess.SECURED_BY_PERIMETER`
  - Model `ScaleProfile` deleted or renamed its instance variable `autoscale`
  - Deleted or renamed enum value `SnapshotType.MANAGED_CLUSTER`
  - Deleted or renamed enum value `WorkloadRuntime.KATA_MSHV_VM_ISOLATION`
  - Deleted or renamed model `AddonAutoscaling`
  - Deleted or renamed model `AdoptionPolicy`
  - Deleted or renamed model `AdvancedNetworkPolicies`
  - Deleted or renamed model `AdvancedNetworkingSecurityTransitEncryption`
  - Deleted or renamed model `AgentPoolArtifactStreamingProfile`
  - Deleted or renamed model `AgentPoolSSHAccess`
  - Deleted or renamed model `AutoScaleProfile`
  - Deleted or renamed model `ClusterServiceLoadBalancerHealthProbeMode`
  - Deleted or renamed model `Component`
  - Deleted or renamed model `ComponentsByRelease`
  - Deleted or renamed model `ContainerServiceNetworkProfileKubeProxyConfig`
  - Deleted or renamed model `ContainerServiceNetworkProfileKubeProxyConfigIpvsConfig`
  - Deleted or renamed model `DeletePolicy`
  - Deleted or renamed model `DriftAction`
  - Deleted or renamed model `DriverType`
  - Deleted or renamed model `GuardrailsAvailableVersion`
  - Deleted or renamed model `GuardrailsAvailableVersionsList`
  - Deleted or renamed model `GuardrailsAvailableVersionsProperties`
  - Deleted or renamed model `GuardrailsSupport`
  - Deleted or renamed model `IPFamily`
  - Deleted or renamed model `IpvsScheduler`
  - Deleted or renamed model `LabelSelector`
  - Deleted or renamed model `LabelSelectorRequirement`
  - Deleted or renamed model `LoadBalancer`
  - Deleted or renamed model `LocalDNSForwardDestination`
  - Deleted or renamed model `LocalDNSForwardPolicy`
  - Deleted or renamed model `LocalDNSMode`
  - Deleted or renamed model `LocalDNSOverride`
  - Deleted or renamed model `LocalDNSProfile`
  - Deleted or renamed model `LocalDNSProtocol`
  - Deleted or renamed model `LocalDNSQueryLogging`
  - Deleted or renamed model `LocalDNSServeStale`
  - Deleted or renamed model `LocalDNSState`
  - Deleted or renamed model `MachineHardwareProfile`
  - Deleted or renamed model `MachineKubernetesProfile`
  - Deleted or renamed model `MachineOSProfile`
  - Deleted or renamed model `MachineOSProfileLinuxProfile`
  - Deleted or renamed model `MachineStatus`
  - Deleted or renamed model `ManagedClusterAzureMonitorProfileAppMonitoring`
  - Deleted or renamed model `ManagedClusterAzureMonitorProfileAppMonitoringAutoInstrumentation`
  - Deleted or renamed model `ManagedClusterAzureMonitorProfileAppMonitoringOpenTelemetryLogs`
  - Deleted or renamed model `ManagedClusterAzureMonitorProfileAppMonitoringOpenTelemetryMetrics`
  - Deleted or renamed model `ManagedClusterAzureMonitorProfileContainerInsights`
  - Deleted or renamed model `ManagedClusterPropertiesForSnapshot`
  - Deleted or renamed model `ManagedClusterSecurityProfileDefenderSecurityGating`
  - Deleted or renamed model `ManagedClusterSecurityProfileDefenderSecurityGatingIdentitiesItem`
  - Deleted or renamed model `ManagedClusterSecurityProfileImageIntegrity`
  - Deleted or renamed model `ManagedClusterSecurityProfileNodeRestriction`
  - Deleted or renamed model `ManagedClusterSnapshot`
  - Deleted or renamed model `ManagedNamespace`
  - Deleted or renamed model `Mode`
  - Deleted or renamed model `NamespaceProperties`
  - Deleted or renamed model `NamespaceProvisioningState`
  - Deleted or renamed model `NetworkPolicies`
  - Deleted or renamed model `NetworkProfileForSnapshot`
  - Deleted or renamed model `NodeImageVersion`
  - Deleted or renamed model `OperationStatusResult`
  - Deleted or renamed model `OperationStatusResultList`
  - Deleted or renamed model `Operator`
  - Deleted or renamed model `PodLinkLocalAccess`
  - Deleted or renamed model `PolicyRule`
  - Deleted or renamed model `RebalanceLoadBalancersRequestBody`
  - Deleted or renamed model `ResourceQuota`
  - Deleted or renamed model `SafeguardsAvailableVersion`
  - Deleted or renamed model `SafeguardsAvailableVersionsList`
  - Deleted or renamed model `SafeguardsAvailableVersionsProperties`
  - Deleted or renamed model `SafeguardsSupport`
  - Deleted or renamed model `SchedulerConfigMode`
  - Deleted or renamed model `SchedulerInstanceProfile`
  - Deleted or renamed model `SchedulerProfile`
  - Deleted or renamed model `SchedulerProfileSchedulerInstanceProfiles`
  - Deleted or renamed model `SeccompDefault`
  - Deleted or renamed model `TransitEncryptionType`
  - Deleted or renamed model `VmState`
  - Deleted or renamed method `MachinesOperations.begin_create_or_update`
  - Method `ManagedClustersOperations.begin_delete` deleted or renamed its parameter `ignore_pod_disruption_budget` of kind `positional_or_keyword`
  - Deleted or renamed method `ManagedClustersOperations.begin_rebalance_load_balancers`
  - Deleted or renamed method `ManagedClustersOperations.get_guardrails_versions`
  - Deleted or renamed method `ManagedClustersOperations.get_safeguards_versions`
  - Deleted or renamed method `ManagedClustersOperations.list_guardrails_versions`
  - Deleted or renamed method `ManagedClustersOperations.list_safeguards_versions`
  - Deleted or renamed operation group `ContainerServiceOperations`
  - Deleted or renamed operation group `LoadBalancersOperations`
  - Deleted or renamed operation group `ManagedClusterSnapshotsOperations`
  - Deleted or renamed operation group `ManagedNamespacesOperations`
  - Deleted or renamed operation group `OperationStatusResultOperations`

## 38.0.0 (2025-07-15)

### Features Added

  - Added operation MachinesOperations.begin_create_or_update
  - Added operation ManagedClustersOperations.begin_rebalance_load_balancers
  - Added operation ManagedClustersOperations.get_guardrails_versions
  - Added operation ManagedClustersOperations.get_safeguards_versions
  - Added operation ManagedClustersOperations.list_guardrails_versions
  - Added operation ManagedClustersOperations.list_safeguards_versions
  - Model AdvancedNetworkingSecurity has a new parameter advanced_network_policies
  - Model AdvancedNetworkingSecurity has a new parameter transit_encryption
  - Model AgentPool has a new parameter artifact_streaming_profile
  - Model AgentPool has a new parameter enable_custom_ca_trust
  - Model AgentPool has a new parameter local_dns_profile
  - Model AgentPool has a new parameter node_initialization_taints
  - Model AgentPoolSecurityProfile has a new parameter ssh_access
  - Model AgentPoolUpgradeProfile has a new parameter components_by_releases
  - Model AgentPoolUpgradeProfilePropertiesUpgradesItem has a new parameter is_out_of_support
  - Model AgentPoolUpgradeSettings has a new parameter max_blocked_nodes
  - Model ContainerServiceNetworkProfile has a new parameter kube_proxy_config
  - Model ContainerServiceNetworkProfile has a new parameter pod_link_local_access
  - Model GPUProfile has a new parameter driver_type
  - Model IstioEgressGateway has a new parameter gateway_configuration_name
  - Model IstioEgressGateway has a new parameter namespace
  - Model KubeletConfig has a new parameter seccomp_default
  - Model MachineNetworkProperties has a new parameter enable_node_public_ip
  - Model MachineNetworkProperties has a new parameter node_public_ip_prefix_id
  - Model MachineNetworkProperties has a new parameter node_public_ip_tags
  - Model MachineNetworkProperties has a new parameter pod_subnet_id
  - Model MachineNetworkProperties has a new parameter vnet_subnet_id
  - Model MachineProperties has a new parameter e_tag
  - Model MachineProperties has a new parameter hardware
  - Model MachineProperties has a new parameter kubernetes
  - Model MachineProperties has a new parameter mode
  - Model MachineProperties has a new parameter node_image_version
  - Model MachineProperties has a new parameter operating_system
  - Model MachineProperties has a new parameter priority
  - Model MachineProperties has a new parameter provisioning_state
  - Model MachineProperties has a new parameter security
  - Model MachineProperties has a new parameter status
  - Model MachineProperties has a new parameter tags
  - Model ManagedCluster has a new parameter ai_toolchain_operator_profile
  - Model ManagedCluster has a new parameter creation_data
  - Model ManagedCluster has a new parameter enable_namespace_resources
  - Model ManagedCluster has a new parameter kind
  - Model ManagedCluster has a new parameter node_provisioning_profile
  - Model ManagedCluster has a new parameter scheduler_profile
  - Model ManagedClusterAgentPoolProfile has a new parameter artifact_streaming_profile
  - Model ManagedClusterAgentPoolProfile has a new parameter enable_custom_ca_trust
  - Model ManagedClusterAgentPoolProfile has a new parameter local_dns_profile
  - Model ManagedClusterAgentPoolProfile has a new parameter node_initialization_taints
  - Model ManagedClusterAgentPoolProfileProperties has a new parameter artifact_streaming_profile
  - Model ManagedClusterAgentPoolProfileProperties has a new parameter enable_custom_ca_trust
  - Model ManagedClusterAgentPoolProfileProperties has a new parameter local_dns_profile
  - Model ManagedClusterAgentPoolProfileProperties has a new parameter node_initialization_taints
  - Model ManagedClusterAzureMonitorProfile has a new parameter app_monitoring
  - Model ManagedClusterAzureMonitorProfile has a new parameter container_insights
  - Model ManagedClusterHTTPProxyConfig has a new parameter effective_no_proxy
  - Model ManagedClusterHTTPProxyConfig has a new parameter enabled
  - Model ManagedClusterLoadBalancerProfile has a new parameter cluster_service_load_balancer_health_probe_mode
  - Model ManagedClusterPoolUpgradeProfile has a new parameter components_by_releases
  - Model ManagedClusterPoolUpgradeProfileUpgradesItem has a new parameter is_out_of_support
  - Model ManagedClusterSecurityProfile has a new parameter image_integrity
  - Model ManagedClusterSecurityProfile has a new parameter node_restriction
  - Model ManagedClusterSecurityProfileDefender has a new parameter security_gating
  - Model ManagedClusterStorageProfileDiskCSIDriver has a new parameter version
  - Model ManagedClusterWorkloadAutoScalerProfileVerticalPodAutoscaler has a new parameter addon_autoscaling
  - Model NamespaceProperties has a new parameter portal_fqdn
  - Model ScaleProfile has a new parameter autoscale
  - Operation ManagedClustersOperations.begin_delete has a new optional parameter ignore_pod_disruption_budget

### Breaking Changes

  - Model IstioEgressGateway has a new required parameter name

## 37.0.0 (2025-06-11)

### Features Added

  - Added operation group ManagedNamespacesOperations
  - Model AgentPool has a new parameter gateway_profile
  - Model AgentPool has a new parameter pod_ip_allocation_mode
  - Model AgentPool has a new parameter status
  - Model AgentPool has a new parameter virtual_machine_nodes_status
  - Model AgentPool has a new parameter virtual_machines_profile
  - Model ContainerServiceNetworkProfile has a new parameter static_egress_gateway_profile
  - Model Machine has a new parameter zones
  - Model ManagedCluster has a new parameter status
  - Model ManagedClusterAgentPoolProfile has a new parameter gateway_profile
  - Model ManagedClusterAgentPoolProfile has a new parameter pod_ip_allocation_mode
  - Model ManagedClusterAgentPoolProfile has a new parameter status
  - Model ManagedClusterAgentPoolProfile has a new parameter virtual_machine_nodes_status
  - Model ManagedClusterAgentPoolProfile has a new parameter virtual_machines_profile
  - Model ManagedClusterAgentPoolProfileProperties has a new parameter gateway_profile
  - Model ManagedClusterAgentPoolProfileProperties has a new parameter pod_ip_allocation_mode
  - Model ManagedClusterAgentPoolProfileProperties has a new parameter status
  - Model ManagedClusterAgentPoolProfileProperties has a new parameter virtual_machine_nodes_status
  - Model ManagedClusterAgentPoolProfileProperties has a new parameter virtual_machines_profile
  - Model ManagedClusterNodeProvisioningProfile has a new parameter default_node_pools

### Breaking Changes

  - Model ScaleProfile no longer has parameter autoscale
  - Removed operation group NamespacesOperations

## 36.0.0 (2025-05-15)

### Features Added

  - Added operation group NamespacesOperations
  - Model AgentPoolUpgradeSettings has a new parameter max_unavailable
  - Model AgentPoolUpgradeSettings has a new parameter undrainable_node_behavior
  - Model AutoScaleProfile has a new parameter size
  - Model ManagedClusterAPIServerAccessProfile has a new parameter enable_vnet_integration
  - Model ManagedClusterAPIServerAccessProfile has a new parameter subnet_id
  - Model ManualScaleProfile has a new parameter size

### Breaking Changes

  - Model AutoScaleProfile no longer has parameter os_disk_size_gb
  - Model AutoScaleProfile no longer has parameter os_disk_type
  - Model AutoScaleProfile no longer has parameter sizes
  - Model ManagedCluster no longer has parameter enable_pod_security_policy
  - Model ManualScaleProfile no longer has parameter os_disk_size_gb
  - Model ManualScaleProfile no longer has parameter os_disk_type
  - Model ManualScaleProfile no longer has parameter sizes

## 35.0.0 (2025-04-14)

### Features Added

  - Model ManagedClusterIngressProfileWebAppRouting has a new parameter nginx

### Breaking Changes

  - Model LoadBalancer no longer has parameter name_properties_name
  - Operation LoadBalancersOperations.create_or_update has a new required parameter parameters
  - Operation LoadBalancersOperations.create_or_update no longer has parameter allow_service_placement
  - Operation LoadBalancersOperations.create_or_update no longer has parameter name
  - Operation LoadBalancersOperations.create_or_update no longer has parameter node_selector
  - Operation LoadBalancersOperations.create_or_update no longer has parameter primary_agent_pool_name
  - Operation LoadBalancersOperations.create_or_update no longer has parameter service_label_selector
  - Operation LoadBalancersOperations.create_or_update no longer has parameter service_namespace_selector

## 34.2.0 (2025-03-18)

### Features Added

  - Added operation group ContainerServiceOperations
  - Added operation group LoadBalancersOperations
  - Added operation group ManagedClusterSnapshotsOperations
  - Added operation group OperationStatusResultOperations
  - Model AgentPool has a new parameter gpu_profile
  - Model ManagedCluster has a new parameter bootstrap_profile
  - Model ManagedClusterAgentPoolProfile has a new parameter gpu_profile
  - Model ManagedClusterAgentPoolProfileProperties has a new parameter gpu_profile
  - Model ManagedClusterSecurityProfile has a new parameter custom_ca_trust_certificates

## 34.1.0 (2025-02-19)

### Features Added

  - Model AgentPool has a new parameter message_of_the_day
  - Model ManagedClusterAgentPoolProfile has a new parameter message_of_the_day
  - Model ManagedClusterAgentPoolProfileProperties has a new parameter message_of_the_day

## 34.0.0 (2025-01-20)

### Features Added

  - Added operation ContainerServicesOperations.begin_create_or_update
  - Added operation ContainerServicesOperations.begin_delete
  - Added operation ContainerServicesOperations.get
  - Added operation ContainerServicesOperations.list
  - Added operation ContainerServicesOperations.list_by_resource_group
  - Model NetworkProfile has a new parameter peer_vnet_id
  - Model OpenShiftManagedClusterMasterPoolProfile has a new parameter name
  - Model OpenShiftManagedClusterMasterPoolProfile has a new parameter os_type

### Breaking Changes

  - Removed subfolders of some unused Api-Versions for smaller package size. If your application requires a specific and non-latest Api-Version, it's recommended to pin this package to the previous released version; If your application always only use latest Api-Version, please ignore this change.
  - Model BaseManagedCluster no longer has parameter power_state
  - Model Components1Q1Og48SchemasManagedclusterAllof1 no longer has parameter azure_portal_fqdn
  - Model Components1Q1Og48SchemasManagedclusterAllof1 no longer has parameter disable_local_accounts
  - Model Components1Q1Og48SchemasManagedclusterAllof1 no longer has parameter fqdn_subdomain
  - Model Components1Q1Og48SchemasManagedclusterAllof1 no longer has parameter http_proxy_config
  - Model Components1Q1Og48SchemasManagedclusterAllof1 no longer has parameter private_link_resources
  - Model NetworkProfile no longer has parameter management_subnet_cidr
  - Model OpenShiftManagedCluster no longer has parameter refresh_cluster
  - Model OpenShiftManagedClusterMasterPoolProfile no longer has parameter api_properties
  - Removed operation ContainerServicesOperations.list_orchestrators
  - Removed operation group FleetMembersOperations
  - Removed operation group FleetsOperations
  - Removed operation group LoadBalancersOperations
  - Removed operation group ManagedClusterSnapshotsOperations
  - Removed operation group OperationStatusResultOperations

## 33.0.0 (2024-11-08)

### Features Added

  - Model AdvancedNetworking has a new parameter enabled
  - Model AdvancedNetworkingSecurity has a new parameter enabled
  - Model AgentPool has a new parameter e_tag
  - Model ContainerServiceNetworkProfile has a new parameter advanced_networking
  - Model ManagedCluster has a new parameter e_tag
  - Model ManagedCluster has a new parameter node_resource_group_profile
  - Model ManagedClusterAgentPoolProfile has a new parameter e_tag
  - Model ManagedClusterAgentPoolProfileProperties has a new parameter e_tag
  - Operation AgentPoolsOperations.begin_create_or_update has a new optional parameter if_match
  - Operation AgentPoolsOperations.begin_create_or_update has a new optional parameter if_none_match
  - Operation AgentPoolsOperations.begin_delete has a new optional parameter if_match
  - Operation ManagedClustersOperations.begin_create_or_update has a new optional parameter if_match
  - Operation ManagedClustersOperations.begin_create_or_update has a new optional parameter if_none_match
  - Operation ManagedClustersOperations.begin_delete has a new optional parameter if_match
  - Operation ManagedClustersOperations.begin_update_tags has a new optional parameter if_match

### Breaking Changes

  - Model AdvancedNetworkingObservability no longer has parameter tls_management
  - Model AdvancedNetworkingSecurity no longer has parameter fqdn_policy

## 32.1.0 (2024-10-11)

### Features Added

  - Model AgentPoolGPUProfile has a new parameter driver_type
  - Operation AgentPoolsOperations.begin_delete has a new optional parameter ignore_pod_disruption_budget

## 32.0.0 (2024-09-12)

### Features Added

  - Added operation AgentPoolsOperations.begin_delete_machines
  - Model AdvancedNetworking has a new parameter security
  - Model AdvancedNetworkingObservability has a new parameter tls_management
  - Model AgentPool has a new parameter security_profile
  - Model ManagedClusterAgentPoolProfile has a new parameter security_profile
  - Model ManagedClusterAgentPoolProfileProperties has a new parameter security_profile

### Breaking Changes

  - Model AgentPoolSecurityProfile no longer has parameter ssh_access

## 31.0.0 (2024-07-18)

### Features Added

  - Added operation group LoadBalancersOperations
  - Model ManagedClusterAzureMonitorProfileAppMonitoring has a new parameter auto_instrumentation
  - Model ManagedClusterAzureMonitorProfileAppMonitoring has a new parameter open_telemetry_logs
  - Model ManagedClusterAzureMonitorProfileAppMonitoring has a new parameter open_telemetry_metrics
  - Model ManagedClusterAzureMonitorProfileAppMonitoringOpenTelemetryMetrics has a new parameter port
  - Model ManagedClusterAzureMonitorProfileContainerInsights has a new parameter disable_custom_metrics
  - Model ManagedClusterAzureMonitorProfileContainerInsights has a new parameter disable_prometheus_metrics_scraping
  - Model ManagedClusterAzureMonitorProfileContainerInsights has a new parameter syslog_port
  - Model ManagedClusterPropertiesAutoScalerProfile has a new parameter daemonset_eviction_for_empty_nodes
  - Model ManagedClusterPropertiesAutoScalerProfile has a new parameter daemonset_eviction_for_occupied_nodes
  - Model ManagedClusterPropertiesAutoScalerProfile has a new parameter ignore_daemonsets_utilization
  - Model ScaleProfile has a new parameter autoscale

### Breaking Changes

  - Model ManagedClusterAzureMonitorProfileAppMonitoring no longer has parameter enabled
  - Model ManagedClusterAzureMonitorProfileContainerInsights no longer has parameter windows_host_logs
  - Removed operation ManagedClustersOperations.get_os_options

## 30.0.0 (2024-04-22)

### Features Added

  - Model AgentPool has a new parameter windows_profile
  - Model KubernetesVersion has a new parameter is_default
  - Model ManagedCluster has a new parameter metrics_profile
  - Model ManagedClusterAgentPoolProfile has a new parameter windows_profile
  - Model ManagedClusterAgentPoolProfileProperties has a new parameter windows_profile

### Breaking Changes

  - Model IstioEgressGateway no longer has parameter node_selector

## 29.1.0 (2024-02-20)

### Features Added

  - Model AgentPoolSecurityProfile has a new parameter enable_secure_boot
  - Model AgentPoolSecurityProfile has a new parameter enable_vtpm
  - Model ManagedCluster has a new parameter ingress_profile

## 29.0.0 (2024-01-22)

### Breaking Changes

  - Model AgentPool no longer has parameter artifact_streaming_profile
  - Model AgentPool no longer has parameter enable_custom_ca_trust
  - Model AgentPool no longer has parameter gpu_profile
  - Model AgentPool no longer has parameter message_of_the_day
  - Model AgentPool no longer has parameter node_initialization_taints
  - Model AgentPool no longer has parameter security_profile
  - Model AgentPool no longer has parameter virtual_machine_nodes_status
  - Model AgentPool no longer has parameter virtual_machines_profile
  - Model AgentPool no longer has parameter windows_profile
  - Model ContainerServiceNetworkProfile no longer has parameter kube_proxy_config
  - Model ContainerServiceNetworkProfile no longer has parameter monitoring
  - Model ManagedCluster no longer has parameter ai_toolchain_operator_profile
  - Model ManagedCluster no longer has parameter creation_data
  - Model ManagedCluster no longer has parameter enable_namespace_resources
  - Model ManagedCluster no longer has parameter guardrails_profile
  - Model ManagedCluster no longer has parameter ingress_profile
  - Model ManagedCluster no longer has parameter metrics_profile
  - Model ManagedCluster no longer has parameter node_provisioning_profile
  - Model ManagedCluster no longer has parameter node_resource_group_profile
  - Model ManagedClusterAPIServerAccessProfile no longer has parameter enable_vnet_integration
  - Model ManagedClusterAPIServerAccessProfile no longer has parameter subnet_id
  - Model ManagedClusterAgentPoolProfile no longer has parameter artifact_streaming_profile
  - Model ManagedClusterAgentPoolProfile no longer has parameter enable_custom_ca_trust
  - Model ManagedClusterAgentPoolProfile no longer has parameter gpu_profile
  - Model ManagedClusterAgentPoolProfile no longer has parameter message_of_the_day
  - Model ManagedClusterAgentPoolProfile no longer has parameter node_initialization_taints
  - Model ManagedClusterAgentPoolProfile no longer has parameter security_profile
  - Model ManagedClusterAgentPoolProfile no longer has parameter virtual_machine_nodes_status
  - Model ManagedClusterAgentPoolProfile no longer has parameter virtual_machines_profile
  - Model ManagedClusterAgentPoolProfile no longer has parameter windows_profile
  - Model ManagedClusterAgentPoolProfileProperties no longer has parameter artifact_streaming_profile
  - Model ManagedClusterAgentPoolProfileProperties no longer has parameter enable_custom_ca_trust
  - Model ManagedClusterAgentPoolProfileProperties no longer has parameter gpu_profile
  - Model ManagedClusterAgentPoolProfileProperties no longer has parameter message_of_the_day
  - Model ManagedClusterAgentPoolProfileProperties no longer has parameter node_initialization_taints
  - Model ManagedClusterAgentPoolProfileProperties no longer has parameter security_profile
  - Model ManagedClusterAgentPoolProfileProperties no longer has parameter virtual_machine_nodes_status
  - Model ManagedClusterAgentPoolProfileProperties no longer has parameter virtual_machines_profile
  - Model ManagedClusterAgentPoolProfileProperties no longer has parameter windows_profile
  - Model ManagedClusterAzureMonitorProfile no longer has parameter logs
  - Model ManagedClusterAzureMonitorProfileMetrics no longer has parameter app_monitoring_open_telemetry_metrics
  - Model ManagedClusterHTTPProxyConfig no longer has parameter effective_no_proxy
  - Model ManagedClusterPropertiesAutoScalerProfile no longer has parameter daemonset_eviction_for_empty_nodes
  - Model ManagedClusterPropertiesAutoScalerProfile no longer has parameter daemonset_eviction_for_occupied_nodes
  - Model ManagedClusterPropertiesAutoScalerProfile no longer has parameter ignore_daemonsets_utilization
  - Model ManagedClusterSecurityProfile no longer has parameter custom_ca_trust_certificates
  - Model ManagedClusterSecurityProfile no longer has parameter image_integrity
  - Model ManagedClusterSecurityProfile no longer has parameter node_restriction
  - Model ManagedClusterStorageProfileDiskCSIDriver no longer has parameter version
  - Model ManagedClusterWorkloadAutoScalerProfileVerticalPodAutoscaler no longer has parameter addon_autoscaling
  - Operation AgentPoolsOperations.begin_delete no longer has parameter ignore_pod_disruption_budget
  - Operation ManagedClustersOperations.begin_delete no longer has parameter ignore_pod_disruption_budget
  - Removed operation AgentPoolsOperations.begin_delete_machines
  - Removed operation ManagedClustersOperations.get_guardrails_versions
  - Removed operation ManagedClustersOperations.list_guardrails_versions

## 28.0.0 (2023-11-20)

### Features Added

  - Added operation AgentPoolsOperations.begin_delete_machines
  - Added operation ManagedClustersOperations.get_guardrails_versions
  - Added operation ManagedClustersOperations.list_guardrails_versions
  - Added operation group OperationStatusResultOperations
  - Model AgentPool has a new parameter artifact_streaming_profile
  - Model AgentPool has a new parameter capacity_reservation_group_id
  - Model AgentPool has a new parameter enable_custom_ca_trust
  - Model AgentPool has a new parameter gpu_profile
  - Model AgentPool has a new parameter message_of_the_day
  - Model AgentPool has a new parameter network_profile
  - Model AgentPool has a new parameter node_initialization_taints
  - Model AgentPool has a new parameter security_profile
  - Model AgentPool has a new parameter virtual_machine_nodes_status
  - Model AgentPool has a new parameter virtual_machines_profile
  - Model AgentPool has a new parameter windows_profile
  - Model AgentPoolUpgradeSettings has a new parameter node_soak_duration_in_minutes
  - Model ContainerServiceNetworkProfile has a new parameter kube_proxy_config
  - Model ContainerServiceNetworkProfile has a new parameter monitoring
  - Model ManagedCluster has a new parameter ai_toolchain_operator_profile
  - Model ManagedCluster has a new parameter creation_data
  - Model ManagedCluster has a new parameter enable_namespace_resources
  - Model ManagedCluster has a new parameter guardrails_profile
  - Model ManagedCluster has a new parameter ingress_profile
  - Model ManagedCluster has a new parameter metrics_profile
  - Model ManagedCluster has a new parameter node_provisioning_profile
  - Model ManagedCluster has a new parameter node_resource_group_profile
  - Model ManagedClusterAPIServerAccessProfile has a new parameter enable_vnet_integration
  - Model ManagedClusterAPIServerAccessProfile has a new parameter subnet_id
  - Model ManagedClusterAgentPoolProfile has a new parameter artifact_streaming_profile
  - Model ManagedClusterAgentPoolProfile has a new parameter capacity_reservation_group_id
  - Model ManagedClusterAgentPoolProfile has a new parameter enable_custom_ca_trust
  - Model ManagedClusterAgentPoolProfile has a new parameter gpu_profile
  - Model ManagedClusterAgentPoolProfile has a new parameter message_of_the_day
  - Model ManagedClusterAgentPoolProfile has a new parameter network_profile
  - Model ManagedClusterAgentPoolProfile has a new parameter node_initialization_taints
  - Model ManagedClusterAgentPoolProfile has a new parameter security_profile
  - Model ManagedClusterAgentPoolProfile has a new parameter virtual_machine_nodes_status
  - Model ManagedClusterAgentPoolProfile has a new parameter virtual_machines_profile
  - Model ManagedClusterAgentPoolProfile has a new parameter windows_profile
  - Model ManagedClusterAgentPoolProfileProperties has a new parameter artifact_streaming_profile
  - Model ManagedClusterAgentPoolProfileProperties has a new parameter capacity_reservation_group_id
  - Model ManagedClusterAgentPoolProfileProperties has a new parameter enable_custom_ca_trust
  - Model ManagedClusterAgentPoolProfileProperties has a new parameter gpu_profile
  - Model ManagedClusterAgentPoolProfileProperties has a new parameter message_of_the_day
  - Model ManagedClusterAgentPoolProfileProperties has a new parameter network_profile
  - Model ManagedClusterAgentPoolProfileProperties has a new parameter node_initialization_taints
  - Model ManagedClusterAgentPoolProfileProperties has a new parameter security_profile
  - Model ManagedClusterAgentPoolProfileProperties has a new parameter virtual_machine_nodes_status
  - Model ManagedClusterAgentPoolProfileProperties has a new parameter virtual_machines_profile
  - Model ManagedClusterAgentPoolProfileProperties has a new parameter windows_profile
  - Model ManagedClusterAzureMonitorProfile has a new parameter logs
  - Model ManagedClusterAzureMonitorProfileMetrics has a new parameter app_monitoring_open_telemetry_metrics
  - Model ManagedClusterHTTPProxyConfig has a new parameter effective_no_proxy
  - Model ManagedClusterLoadBalancerProfile has a new parameter backend_pool_type
  - Model ManagedClusterPropertiesAutoScalerProfile has a new parameter daemonset_eviction_for_empty_nodes
  - Model ManagedClusterPropertiesAutoScalerProfile has a new parameter daemonset_eviction_for_occupied_nodes
  - Model ManagedClusterPropertiesAutoScalerProfile has a new parameter ignore_daemonsets_utilization
  - Model ManagedClusterSecurityProfile has a new parameter custom_ca_trust_certificates
  - Model ManagedClusterSecurityProfile has a new parameter image_integrity
  - Model ManagedClusterSecurityProfile has a new parameter node_restriction
  - Model ManagedClusterStorageProfileDiskCSIDriver has a new parameter version
  - Model ManagedClusterWorkloadAutoScalerProfileVerticalPodAutoscaler has a new parameter addon_autoscaling
  - Operation AgentPoolsOperations.begin_delete has a new optional parameter ignore_pod_disruption_budget
  - Operation ManagedClustersOperations.begin_delete has a new optional parameter ignore_pod_disruption_budget

### Breaking Changes

  - Renamed operation TrustedAccessRoleBindingsOperations.create_or_update to TrustedAccessRoleBindingsOperations.begin_create_or_update
  - Renamed operation TrustedAccessRoleBindingsOperations.delete to TrustedAccessRoleBindingsOperations.begin_delete

## 27.0.0 (2023-10-23)

### Features Added

  - Added operation ManagedClustersOperations.get_mesh_revision_profile
  - Added operation ManagedClustersOperations.get_mesh_upgrade_profile
  - Added operation ManagedClustersOperations.list_mesh_revision_profiles
  - Added operation ManagedClustersOperations.list_mesh_upgrade_profiles
  - Added operation group MachinesOperations
  - Model IstioComponents has a new parameter egress_gateways
  - Model ManagedCluster has a new parameter resource_uid
  - Model ManagedCluster has a new parameter service_mesh_profile
  - Model ManagedClusterIngressProfileWebAppRouting has a new parameter dns_zone_resource_ids

### Breaking Changes

  - Model ManagedClusterIngressProfileWebAppRouting no longer has parameter dns_zone_resource_id

## 26.0.0 (2023-08-18)

### Features Added

  - Model IstioServiceMesh has a new parameter certificate_authority
  - Model IstioServiceMesh has a new parameter revisions
  - Model ManagedCluster has a new parameter upgrade_settings
  - Model UpgradeOverrideSettings has a new parameter force_upgrade

### Breaking Changes

  - Model UpgradeOverrideSettings no longer has parameter control_plane_overrides

## 25.0.0 (2023-07-26)

### Features Added

  - Model AgentPoolUpgradeSettings has a new parameter drain_timeout_in_minutes
  - Model ManagedClusterIdentity has a new parameter delegated_resources

### Breaking Changes

  - Model AgentPool no longer has parameter capacity_reservation_group_id
  - Model AgentPool no longer has parameter enable_custom_ca_trust
  - Model AgentPool no longer has parameter message_of_the_day
  - Model AgentPool no longer has parameter network_profile
  - Model AgentPool no longer has parameter windows_profile
  - Model ContainerServiceNetworkProfile no longer has parameter kube_proxy_config
  - Model ContainerServiceNetworkProfile no longer has parameter monitoring
  - Model ManagedCluster no longer has parameter creation_data
  - Model ManagedCluster no longer has parameter enable_namespace_resources
  - Model ManagedCluster no longer has parameter guardrails_profile
  - Model ManagedCluster no longer has parameter ingress_profile
  - Model ManagedCluster no longer has parameter node_resource_group_profile
  - Model ManagedCluster no longer has parameter service_mesh_profile
  - Model ManagedCluster no longer has parameter upgrade_settings
  - Model ManagedClusterAPIServerAccessProfile no longer has parameter enable_vnet_integration
  - Model ManagedClusterAPIServerAccessProfile no longer has parameter subnet_id
  - Model ManagedClusterAgentPoolProfile no longer has parameter capacity_reservation_group_id
  - Model ManagedClusterAgentPoolProfile no longer has parameter enable_custom_ca_trust
  - Model ManagedClusterAgentPoolProfile no longer has parameter message_of_the_day
  - Model ManagedClusterAgentPoolProfile no longer has parameter network_profile
  - Model ManagedClusterAgentPoolProfile no longer has parameter windows_profile
  - Model ManagedClusterAgentPoolProfileProperties no longer has parameter capacity_reservation_group_id
  - Model ManagedClusterAgentPoolProfileProperties no longer has parameter enable_custom_ca_trust
  - Model ManagedClusterAgentPoolProfileProperties no longer has parameter message_of_the_day
  - Model ManagedClusterAgentPoolProfileProperties no longer has parameter network_profile
  - Model ManagedClusterAgentPoolProfileProperties no longer has parameter windows_profile
  - Model ManagedClusterHTTPProxyConfig no longer has parameter effective_no_proxy
  - Model ManagedClusterLoadBalancerProfile no longer has parameter backend_pool_type
  - Model ManagedClusterSecurityProfile no longer has parameter custom_ca_trust_certificates
  - Model ManagedClusterSecurityProfile no longer has parameter node_restriction
  - Model ManagedClusterStorageProfileDiskCSIDriver no longer has parameter version
  - Model ManagedClusterWorkloadAutoScalerProfileVerticalPodAutoscaler no longer has parameter controlled_values
  - Model ManagedClusterWorkloadAutoScalerProfileVerticalPodAutoscaler no longer has parameter update_mode
  - Operation AgentPoolsOperations.begin_delete no longer has parameter ignore_pod_disruption_budget
  - Operation ManagedClustersOperations.begin_delete no longer has parameter ignore_pod_disruption_budget

## 24.0.0 (2023-06-21)

### Features Added

  - Model ContainerServiceNetworkProfile has a new parameter monitoring
  - Model OrchestratorProfile has a new parameter is_preview

### Breaking Changes

  - Removed operation ContainerServicesOperations.begin_create_or_update
  - Removed operation ContainerServicesOperations.begin_delete
  - Removed operation ContainerServicesOperations.get
  - Removed operation ContainerServicesOperations.list
  - Removed operation ContainerServicesOperations.list_by_resource_group

## 23.0.0 (2023-05-16)

### Breaking Changes

  - Model ContainerServiceNetworkProfile no longer has parameter docker_bridge_cidr

## 22.1.0 (2023-04-19)

### Features Added

  - Added operation ManagedClustersOperations.list_kubernetes_versions
  - Model ManagedCluster has a new parameter support_plan

## 22.0.0 (2023-03-23)

### Features Added

  - Model ContainerServiceNetworkProfile has a new parameter network_dataplane
  - Model ManagedCluster has a new parameter service_mesh_profile
  - Model ManagedClusterIngressProfileWebAppRouting has a new parameter identity

### Breaking Changes

  - Model ContainerServiceNetworkProfile no longer has parameter ebpf_dataplane

## 21.2.0 (2023-02-20)

### Features Added

  - Model ManagedCluster has a new parameter upgrade_settings

## 21.1.0 (2022-12-30)

### Features Added

  - Model ManagedCluster has a new parameter node_resource_group_profile

## 21.0.0 (2022-12-15)

### Features Added

  - Model MaintenanceConfiguration has a new parameter maintenance_window
  - Model ManagedClusterAutoUpgradeProfile has a new parameter node_os_upgrade_channel

### Breaking Changes

  - Renamed operation AgentPoolsOperations.abort_latest_operation to AgentPoolsOperations.begin_abort_latest_operation
  - Renamed operation ManagedClustersOperations.abort_latest_operation to ManagedClustersOperations.begin_abort_latest_operation

## 20.7.0 (2022-11-09)

### Features Added

  - Add new api-version `2022-09-02-preview` for operation group `fleets`

## 20.6.0 (2022-10-25)

### Features Added

  - Model AgentPoolNetworkProfile has a new parameter allowed_host_ports
  - Model AgentPoolNetworkProfile has a new parameter application_security_groups
  - Model ContainerServiceNetworkProfile has a new parameter ebpf_dataplane
  - Model ManagedClusterSecurityProfile has a new parameter custom_ca_trust_certificates

## 20.5.0 (2022-10-18)

### Features Added

  - Model AgentPool has a new parameter network_profile
  - Model ManagedClusterAgentPoolProfile has a new parameter network_profile
  - Model ManagedClusterAgentPoolProfileProperties has a new parameter network_profile

## 20.4.0 (2022-09-20)

### Features Added

  - Model AgentPool has a new parameter windows_profile
  - Model ContainerServiceNetworkProfile has a new parameter kube_proxy_config
  - Model ManagedCluster has a new parameter guardrails_profile
  - Model ManagedClusterAgentPoolProfile has a new parameter windows_profile
  - Model ManagedClusterAgentPoolProfileProperties has a new parameter windows_profile
  - Model ManagedClusterLoadBalancerProfile has a new parameter backend_pool_type

## 20.3.0 (2022-08-26)

### Features Added

  - Added operation AgentPoolsOperations.abort_latest_operation
  - Added operation ManagedClustersOperations.abort_latest_operation
  - Model ManagedCluster has a new parameter azure_monitor_profile
  - Model ManagedClusterSecurityProfile has a new parameter image_cleaner
  - Model ManagedClusterWorkloadAutoScalerProfile has a new parameter vertical_pod_autoscaler

## 20.2.0 (2022-07-25)

**Features**

  - Add a new api-version `2022-06-01`

## 20.1.0 (2022-07-21)

**Features**

  - Added operation group FleetMembersOperations
  - Added operation group FleetsOperations
  - Model ManagedClusterSecurityProfile has a new parameter node_restriction

## 20.0.0 (2022-06-09)

**Features**

  - Model AzureKeyVaultKms has a new parameter key_vault_network_access
  - Model AzureKeyVaultKms has a new parameter key_vault_resource_id
  - Model ManagedCluster has a new parameter workload_auto_scaler_profile
  - Model ManagedClusterSecurityProfile has a new parameter defender
  - Model ManagedClusterStorageProfile has a new parameter blob_csi_driver

**Breaking changes**

  - Model ManagedClusterSecurityProfile no longer has parameter azure_defender

## 19.1.0 (2022-05-13)

**Features**

  - Added operation group TrustedAccessRoleBindingsOperations
  - Added operation group TrustedAccessRolesOperations
  - Model AgentPool has a new parameter enable_custom_ca_trust
  - Model ContainerServiceNetworkProfile has a new parameter network_plugin_mode
  - Model ManagedCluster has a new parameter storage_profile
  - Model ManagedClusterAPIServerAccessProfile has a new parameter enable_vnet_integration
  - Model ManagedClusterAPIServerAccessProfile has a new parameter subnet_id
  - Model ManagedClusterAgentPoolProfile has a new parameter enable_custom_ca_trust
  - Model ManagedClusterAgentPoolProfileProperties has a new parameter enable_custom_ca_trust
  - Model NetworkProfileForSnapshot has a new parameter network_plugin_mode

## 19.0.0 (2022-04-15)

**Features**

  - Added operation ManagedClustersOperations.begin_rotate_service_account_signing_keys
  - Model AgentPool has a new parameter current_orchestrator_version
  - Model ManagedCluster has a new parameter creation_data
  - Model ManagedCluster has a new parameter ingress_profile
  - Model ManagedClusterAgentPoolProfile has a new parameter current_orchestrator_version
  - Model ManagedClusterAgentPoolProfileProperties has a new parameter current_orchestrator_version
  - Model ManagedClusterHTTPProxyConfig has a new parameter effective_no_proxy
  - Model ManagedClusterSecurityProfile has a new parameter workload_identity

**Breaking changes**

  - Model Resource no longer has parameter location
  - Model Resource no longer has parameter tags
  - Operation AgentPoolsOperations.begin_delete has a new parameter ignore_pod_disruption_budget
  - Operation ManagedClustersOperations.begin_delete has a new parameter ignore_pod_disruption_budget

## 18.0.0 (2022-03-23)

**Features**

  - Added operation group ManagedClusterSnapshotsOperations
  - Model ManagedCluster has a new parameter system_data
  - Model ManagedClusterAccessProfile has a new parameter system_data
  - Model ManagedClusterSecurityProfile has a new parameter azure_key_vault_kms
  - Model Resource has a new parameter system_data

**Breaking changes**

  - Operation ManagedClustersOperations.list_cluster_admin_credentials has a new signature
  - Operation ManagedClustersOperations.list_cluster_user_credentials has a new signature

## 17.0.0 (2022-02-21)

**Features**

  - Model AgentPool has a new parameter capacity_reservation_group_id
  - Model AgentPool has a new parameter host_group_id
  - Model AgentPool has a new parameter message_of_the_day
  - Model ManagedCluster has a new parameter current_kubernetes_version
  - Model ManagedCluster has a new parameter enable_namespace_resources
  - Model ManagedCluster has a new parameter oidc_issuer_profile
  - Model ManagedClusterAgentPoolProfile has a new parameter capacity_reservation_group_id
  - Model ManagedClusterAgentPoolProfile has a new parameter host_group_id
  - Model ManagedClusterAgentPoolProfile has a new parameter message_of_the_day
  - Model ManagedClusterAgentPoolProfileProperties has a new parameter capacity_reservation_group_id
  - Model ManagedClusterAgentPoolProfileProperties has a new parameter host_group_id
  - Model ManagedClusterAgentPoolProfileProperties has a new parameter message_of_the_day

**Breaking changes**

  - Operation ManagedClustersOperations.list_cluster_admin_credentials has a new signature

## 16.4.0 (2021-11-25)

**Features**

  - Model ContainerServiceNetworkProfile has a new parameter service_cidrs
  - Model ContainerServiceNetworkProfile has a new parameter pod_cidrs
  - Model ContainerServiceNetworkProfile has a new parameter ip_families
  - Model ManagedClusterLoadBalancerProfileManagedOutboundIPs has a new parameter count_ipv6

## 16.3.0 (2021-10-18)

**Features**

  - Model ManagedClusterWindowsProfile has a new parameter gmsa_profile
  - Model Snapshot has a new parameter vm_size
  - Model Snapshot has a new parameter os_type
  - Model Snapshot has a new parameter os_sku
  - Model Snapshot has a new parameter kubernetes_version
  - Model Snapshot has a new parameter node_image_version
  - Model Snapshot has a new parameter enable_fips

## 16.2.0 (2021-09-09)

**Features**

  - Model ManagedClusterAgentPoolProfileProperties has a new parameter creation_data
  - Model ManagedClusterAgentPoolProfileProperties has a new parameter workload_runtime
  - Model ManagedClusterLoadBalancerProfile has a new parameter enable_multiple_standard_load_balancers
  - Model ManagedClusterAgentPoolProfile has a new parameter creation_data
  - Model ManagedClusterAgentPoolProfile has a new parameter workload_runtime
  - Model ManagedCluster has a new parameter public_network_access
  - Model ManagedClusterAPIServerAccessProfile has a new parameter disable_run_command
  - Model AgentPool has a new parameter creation_data
  - Model AgentPool has a new parameter workload_runtime
  - Added operation group SnapshotsOperations

## 16.1.0 (2021-08-06)

**Features**

  - Model ManagedClusterAgentPoolProfile has a new parameter scale_down_mode
  - Model ContainerServiceNetworkProfile has a new parameter nat_gateway_profile
  - Model ManagedClusterAgentPoolProfileProperties has a new parameter scale_down_mode
  - Model ManagedCluster has a new parameter security_profile
  - Model AgentPool has a new parameter scale_down_mode

## 16.0.0 (2021-06-17)

**Features**

  - Model ManagedClusterAgentPoolProfile has a new parameter enable_ultra_ssd
  - Model ManagedClusterAPIServerAccessProfile has a new parameter enable_private_cluster_public_fqdn
  - Model AgentPool has a new parameter enable_ultra_ssd
  - Model ManagedClusterAgentPoolProfileProperties has a new parameter enable_ultra_ssd
  - Added operation ManagedClustersOperations.list_outbound_network_dependencies_endpoints

**Breaking changes**

  - Operation ManagedClustersOperations.list_cluster_admin_credentials has a new signature
  - Operation ManagedClustersOperations.list_cluster_monitoring_user_credentials has a new signature
  - Operation ManagedClustersOperations.list_cluster_user_credentials has a new signature

## 15.1.0 (2021-04-07)

**Features**

  - Model Components1Q1Og48SchemasManagedclusterAllof1 has a new parameter private_link_resources
  - Model Components1Q1Og48SchemasManagedclusterAllof1 has a new parameter disable_local_accounts
  - Model Components1Q1Og48SchemasManagedclusterAllof1 has a new parameter http_proxy_config
  - Model ManagedClusterPodIdentity has a new parameter binding_selector
  - Model ManagedClusterAgentPoolProfileProperties has a new parameter gpu_instance_profile
  - Model ManagedClusterAgentPoolProfileProperties has a new parameter enable_fips
  - Model ManagedClusterAgentPoolProfileProperties has a new parameter os_sku
  - Model AgentPool has a new parameter gpu_instance_profile
  - Model AgentPool has a new parameter enable_fips
  - Model AgentPool has a new parameter os_sku
  - Model ManagedCluster has a new parameter extended_location
  - Model ManagedCluster has a new parameter private_link_resources
  - Model ManagedCluster has a new parameter disable_local_accounts
  - Model ManagedCluster has a new parameter http_proxy_config
  - Model ManagedClusterAgentPoolProfile has a new parameter gpu_instance_profile
  - Model ManagedClusterAgentPoolProfile has a new parameter enable_fips
  - Model ManagedClusterAgentPoolProfile has a new parameter os_sku
  - Model ManagedClusterWindowsProfile has a new parameter enable_csi_proxy
  - Added operation ManagedClustersOperations.get_command_result
  - Added operation ManagedClustersOperations.begin_run_command
  - Added operation ManagedClustersOperations.get_os_options

## 15.0.0 (2021-03-03)

**Features**

  - Model ManagedClusterPropertiesAutoScalerProfile has a new parameter max_node_provision_time
  - Model ManagedClusterPodIdentityProfile has a new parameter allow_network_plugin_kubenet
  - Model KubeletConfig has a new parameter container_log_max_size_mb
  - Model KubeletConfig has a new parameter pod_max_pids
  - Model KubeletConfig has a new parameter container_log_max_files
  - Model SysctlConfig has a new parameter net_core_rmem_default
  - Model SysctlConfig has a new parameter net_core_wmem_default
  - Model Components1Q1Og48SchemasManagedclusterAllof1 has a new parameter azure_portal_fqdn
  - Model Components1Q1Og48SchemasManagedclusterAllof1 has a new parameter fqdn_subdomain
  - Model ManagedCluster has a new parameter azure_portal_fqdn
  - Model ManagedCluster has a new parameter fqdn_subdomain
  - Model ManagedClusterAgentPoolProfile has a new parameter kubelet_disk_type
  - Model ManagedClusterAgentPoolProfile has a new parameter enable_encryption_at_host
  - Model ManagedClusterAgentPoolProfile has a new parameter node_public_ip_prefix_id
  - Model ManagedClusterAgentPoolProfileProperties has a new parameter kubelet_disk_type
  - Model ManagedClusterAgentPoolProfileProperties has a new parameter enable_encryption_at_host
  - Model ManagedClusterAgentPoolProfileProperties has a new parameter node_public_ip_prefix_id
  - Model AgentPool has a new parameter kubelet_disk_type
  - Model AgentPool has a new parameter enable_encryption_at_host
  - Model AgentPool has a new parameter node_public_ip_prefix_id
  - Added operation group MaintenanceConfigurationsOperations

**Breaking changes**

  - Model SysctlConfig no longer has parameter net_ipv4_tcp_rmem
  - Model SysctlConfig no longer has parameter net_ipv4_tcp_wmem

## 14.0.0 (2020-11-23)

**Features**

  - Model ManagedCluster has a new parameter pod_identity_profile
  - Model ManagedCluster has a new parameter auto_upgrade_profile
  - Model ManagedClusterAgentPoolProfile has a new parameter linux_os_config
  - Model ManagedClusterAgentPoolProfile has a new parameter kubelet_config
  - Model ManagedClusterAgentPoolProfile has a new parameter pod_subnet_id
  - Model ManagedClusterAgentPoolProfileProperties has a new parameter linux_os_config
  - Model ManagedClusterAgentPoolProfileProperties has a new parameter kubelet_config
  - Model ManagedClusterAgentPoolProfileProperties has a new parameter pod_subnet_id
  - Model ManagedClusterAPIServerAccessProfile has a new parameter private_dns_zone
  - Model AgentPool has a new parameter linux_os_config
  - Model AgentPool has a new parameter kubelet_config
  - Model AgentPool has a new parameter pod_subnet_id

## 14.0.0b1 (2020-10-23)

This is beta preview version.
For detailed changelog please refer to equivalent stable version 9.4.0 (https://pypi.org/project/azure-mgmt-containerservice/9.4.0/)

This version uses a next-generation code generator that introduces important breaking changes, but also important new features (like unified authentication and async programming).

**General breaking changes**

- Credential system has been completly revamped:

  - `azure.common.credentials` or `msrestazure.azure_active_directory` instances are no longer supported, use the `azure-identity` classes instead: https://pypi.org/project/azure-identity/
  - `credentials` parameter has been renamed `credential`

- The `config` attribute no longer exists on a client, configuration should be passed as kwarg. Example: `MyClient(credential, subscription_id, enable_logging=True)`. For a complete set of
  supported options, see the [parameters accept in init documentation of azure-core](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/CLIENT_LIBRARY_DEVELOPER.md#available-policies)
- You can't import a `version` module anymore, use `__version__` instead
- Operations that used to return a `msrest.polling.LROPoller` now returns a `azure.core.polling.LROPoller` and are prefixed with `begin_`.
- Exceptions tree have been simplified and most exceptions are now `azure.core.exceptions.HttpResponseError` (`CloudError` has been removed).
- Most of the operation kwarg have changed. Some of the most noticeable:

  - `raw` has been removed. Equivalent feature can be found using `cls`, a callback that will give access to internal HTTP response for advanced user
  - For a complete set of supported options, see the [parameters accept in Request documentation of azure-core](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/CLIENT_LIBRARY_DEVELOPER.md#available-policies)

**General new features**

- Type annotations support using `typing`. SDKs are mypy ready.
- This client has now stable and official support for async. Check the `aio` namespace of your package to find the async client.
- This client now support natively tracing library like OpenCensus or OpenTelemetry. See this [tracing quickstart](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/core/azure-core-tracing-opentelemetry) for an overview.


## 9.4.0 (2020-09-11)

**Features**

  - Model ManagedClusterAgentPoolProfile has a new parameter power_state
  - Model ManagedClusterAgentPoolProfile has a new parameter os_disk_type
  - Model ManagedClusterPropertiesAutoScalerProfile has a new parameter max_empty_bulk_delete
  - Model ManagedClusterPropertiesAutoScalerProfile has a new parameter skip_nodes_with_local_storage
  - Model ManagedClusterPropertiesAutoScalerProfile has a new parameter max_total_unready_percentage
  - Model ManagedClusterPropertiesAutoScalerProfile has a new parameter ok_total_unready_count
  - Model ManagedClusterPropertiesAutoScalerProfile has a new parameter expander
  - Model ManagedClusterPropertiesAutoScalerProfile has a new parameter skip_nodes_with_system_pods
  - Model ManagedClusterPropertiesAutoScalerProfile has a new parameter new_pod_scale_up_delay
  - Model AgentPool has a new parameter power_state
  - Model AgentPool has a new parameter os_disk_type
  - Model ManagedClusterAgentPoolProfileProperties has a new parameter power_state
  - Model ManagedClusterAgentPoolProfileProperties has a new parameter os_disk_type
  - Model ManagedCluster has a new parameter power_state
  - Added operation ManagedClustersOperations.start
  - Added operation ManagedClustersOperations.stop
  - Added operation group ResolvePrivateLinkServiceIdOperations
  - Added operation group PrivateLinkResourcesOperations

## 9.3.0 (2020-08-24)

**Features**

  - Model ManagedClusterWindowsProfile has a new parameter license_type
  - Added operation ManagedClustersOperations.upgrade_node_image_version

## 9.2.0 (2020-06-24)

**Features**

  - Model ManagedClusterIdentity has a new parameter user_assigned_identities
  - Model ManagedClusterAADProfile has a new parameter enable_azure_rbac
  - Model ManagedClusterAgentPoolProfile has a new parameter proximity_placement_group_id
  - Model ManagedClusterAgentPoolProfileProperties has a new parameter proximity_placement_group_id
  - Model AgentPool has a new parameter proximity_placement_group_id
  - Added operation group PrivateEndpointConnectionsOperations

## 9.1.0 (2020-06-03)

**Features**

  - Model AgentPool has a new parameter node_image_version
  - Model AgentPool has a new parameter upgrade_settings
  - Model AgentPoolUpgradeProfile has a new parameter latest_node_image_version
  - Model ManagedClusterAgentPoolProfile has a new parameter node_image_version
  - Model ManagedClusterAgentPoolProfile has a new parameter upgrade_settings
  - Model ManagedClusterAgentPoolProfileProperties has a new parameter node_image_version
  - Model ManagedClusterAgentPoolProfileProperties has a new parameter upgrade_settings

## 9.0.1 (2020-04-09)

**Bugfixes**

  - Switch field type to string to avoid unmarshal errors

## 9.0.0 (2020-03-24)

**Features**

  - Model ManagedClusterAgentPoolProfile has a new parameter mode
  - Model ManagedCluster has a new parameter sku
  - Model OpenShiftManagedCluster has a new parameter refresh_cluster
  - Model ManagedClusterAADProfile has a new parameter admin_group_object_ids
  - Model ManagedClusterAADProfile has a new parameter managed
  - Model ManagedClusterAgentPoolProfileProperties has a new parameter mode
  - Model OpenShiftManagedClusterMasterPoolProfile has a new parameter api_properties
  - Model ManagedClusterPropertiesAutoScalerProfile has a new parameter balance_similar_node_groups
  - Model NetworkProfile has a new parameter management_subnet_cidr
  - Model AgentPool has a new parameter mode

**Breaking changes**

  - Model OpenShiftManagedClusterMasterPoolProfile no longer has parameter name
  - Model OpenShiftManagedClusterMasterPoolProfile no longer has parameter os_type
  - Model NetworkProfile no longer has parameter peer_vnet_id

## 8.3.0 (2020-02-14)

**Features**

  - Model ManagedCluster has a new parameter auto_scaler_profile
  - Model ManagedClusterAgentPoolProfile has a new parameter spot_max_price
  - Model AgentPool has a new parameter spot_max_price
  - Model ManagedClusterAgentPoolProfileProperties has a new parameter spot_max_price
  - Model ContainerServiceNetworkProfile has a new parameter network_mode
  - Added operation ManagedClustersOperations.list_cluster_monitoring_user_credentials

## 8.2.0 (2020-01-07)

**Features**

  - Model ManagedCluster has a new parameter disk_encryption_set_id

## 8.1.0 (2019-12-16)

**Features**

  - Model ContainerServiceNetworkProfile has a new parameter
    outbound_type
  - Model ManagedClusterAgentPoolProfile has a new parameter
    node_labels
  - Model ManagedClusterAgentPoolProfile has a new parameter tags
  - Model ManagedCluster has a new parameter identity_profile
  - Model ManagedClusterLoadBalancerProfile has a new parameter
    idle_timeout_in_minutes
  - Model ManagedClusterLoadBalancerProfile has a new parameter
    allocated_outbound_ports
  - Model AgentPool has a new parameter node_labels
  - Model AgentPool has a new parameter tags
  - Model ManagedClusterAddonProfile has a new parameter identity
  - Model ManagedClusterAgentPoolProfileProperties has a new parameter
    node_labels
  - Model ManagedClusterAgentPoolProfileProperties has a new parameter
    tags

## 8.0.0 (2019-10-24)

**Features**

  - Model OpenShiftManagedCluster has a new parameter monitor_profile
  - Model ManagedCluster has a new parameter private_fqdn
  - Added operation
    ManagedClustersOperations.rotate_cluster_certificates

**Breaking changes**

  - Operation AgentPoolsOperations.get_available_agent_pool_versions
    has a new signature

## 7.0.0 (2019-08-30)

**Features**

  - Model ContainerServiceNetworkProfile has a new parameter
    load_balancer_profile
  - Model ManagedCluster has a new parameter
    api_server_access_profile

**Breaking changes**

  - Model ManagedCluster no longer has parameter
    api_server_authorized_ip_ranges

## 6.0.0 (2019-06-20)

**Features**

  - Model ManagedClusterAgentPoolProfile has a new parameter
    enable_node_public_ip
  - Model ManagedClusterAgentPoolProfile has a new parameter
    scale_set_eviction_policy
  - Model ManagedClusterAgentPoolProfile has a new parameter
    node_taints
  - Model ManagedClusterAgentPoolProfile has a new parameter
    scale_set_priority
  - Model AgentPool has a new parameter enable_node_public_ip
  - Model AgentPool has a new parameter scale_set_eviction_policy
  - Model AgentPool has a new parameter node_taints
  - Model AgentPool has a new parameter scale_set_priority
  - Model ManagedClusterAgentPoolProfileProperties has a new parameter
    enable_node_public_ip
  - Model ManagedClusterAgentPoolProfileProperties has a new parameter
    scale_set_eviction_policy
  - Model ManagedClusterAgentPoolProfileProperties has a new parameter
    node_taints
  - Model ManagedClusterAgentPoolProfileProperties has a new parameter
    scale_set_priority
  - Added operation
    AgentPoolsOperations.get_available_agent_pool_versions
  - Added operation AgentPoolsOperations.get_upgrade_profile

**General Breaking changes**

This version uses a next-generation code generator that *might*
introduce breaking changes if you were importing from the v20xx_yy_zz
API folders. In summary, some modules were incorrectly
visible/importable and have been renamed. This fixed several issues
caused by usage of classes that were not supposed to be used in the
first place.

  - ContainerServiceManagementClient cannot be imported from
    `azure.mgmt.containerservice.v20xx_yy_zz.container_service_management_client`
    anymore (import from `azure.mgmt.containerservice.v20xx_yy_zz`
    works like before)
  - ContainerServiceManagementClientConfiguration import has been moved
    from
    `azure.mgmt.containerservice.v20xx_yy_zz.container_service_management_client`
    to `azure.mgmt.containerservice.v20xx_yy_zz`
  - A model `MyClass` from a "models" sub-module cannot be imported
    anymore using
    `azure.mgmt.containerservice.v20xx_yy_zz.models.my_class`
    (import from `azure.mgmt.containerservice.v20xx_yy_zz.models`
    works like before)
  - An operation class `MyClassOperations` from an `operations`
    sub-module cannot be imported anymore using
    `azure.mgmt.containerservice.v20xx_yy_zz.operations.my_class_operations`
    (import from
    `azure.mgmt.containerservice.v20xx_yy_zz.operations` works like
    before)

Last but not least, HTTP connection pooling is now enabled by default.
You should always use a client as a context manager, or call close(), or
use no more than one client per process.

## 5.3.0 (2019-05-03)

**Features**

  - Model OrchestratorProfile has a new parameter is_preview
  - Model OrchestratorVersionProfile has a new parameter is_preview
  - Model ContainerServiceNetworkProfile has a new parameter
    load_balancer_sku
  - Model ManagedCluster has a new parameter identity
  - Model ManagedCluster has a new parameter max_agent_pools
  - Model ManagedCluster has a new parameter windows_profile

## 5.2.0 (2019-04-30)

**Features**

  - OpenShift is now using a GA api version
  - Model OpenShiftManagedCluster has a new parameter cluster_version
  - Model NetworkProfile has a new parameter vnet_id

## 5.1.0 (2019-04-08)

**Features**

  - Model OpenShiftManagedClusterAADIdentityProvider has a new parameter
    customer_admin_group_id

## 5.0.0 (2019-03-19)

**Features**

  - Model ManagedClusterAgentPoolProfile has a new parameter min_count
  - Model ManagedClusterAgentPoolProfile has a new parameter
    availability_zones
  - Model ManagedClusterAgentPoolProfile has a new parameter type
  - Model ManagedClusterAgentPoolProfile has a new parameter
    enable_auto_scaling
  - Model ManagedClusterAgentPoolProfile has a new parameter max_count
  - Model ManagedClusterAgentPoolProfile has a new parameter
    provisioning_state
  - Model ManagedClusterAgentPoolProfile has a new parameter
    orchestrator_version
  - Model ManagedCluster has a new parameter
    api_server_authorized_ip_ranges
  - Model ManagedCluster has a new parameter
    enable_pod_security_policy
  - Added operation group AgentPoolsOperations

**Breaking changes**

  - Parameter count of model ManagedClusterAgentPoolProfile is now
    required
  - Model ManagedClusterAgentPoolProfile no longer has parameter
    storage_profile

## 4.4.0 (2019-01-09)

**Features**

  - Added operation
    ManagedClustersOperations.reset_service_principal_profile
  - Added operation ManagedClustersOperations.reset_aad_profile

## 4.3.0 (2018-12-13)

**Features**

  - Support for Azure Profiles
  - OpenShift ManagedCluster (preview)

This package also adds Preview version of ManagedCluster (AKS
2018-08-01-preview), this includes the following breaking changes and
features, if you optin for this new API version:

**Features**

  - Model ManagedClusterAgentPoolProfile has a new parameter type
  - Model ManagedClusterAgentPoolProfile has a new parameter max_count
  - Model ManagedClusterAgentPoolProfile has a new parameter
    enable_auto_scaling
  - Model ManagedClusterAgentPoolProfile has a new parameter min_count

**Breaking changes**

  - Parameter count of model ManagedClusterAgentPoolProfile is now
    required
  - Model ManagedClusterAgentPoolProfile no longer has parameter
    storage_profile

**Note**

  - azure-mgmt-nspkg is not installed anymore on Python 3 (PEP420-based
    namespace package)

## 4.2.2 (2018-08-09)

**Bugfixes**

  - Fix invalid definition of CredentialResult

## 4.2.1 (2018-08-08)

**Bugfixes**

  - Fix some invalid regexp
  - Fix invalid definition of CredentialResult

## 4.2.0 (2018-07-30)

**Features**

  - Add managed_clusters.list_cluster_admin_credentials
  - Add managed_clusters.list_cluster_user_credentials
  - Add managed_clusters.update_tags

**Bugfixes**

  - Fix incorrect JSON description of ManagedCluster class

## 4.1.0 (2018-06-13)

**Features**

  - Add node_resource_group attribute to some models

## 4.0.0 (2018-05-25)

**Features**

  - Added operation ManagedClustersOperations.get_access_profile
  - Updated VM sizes
  - Client class can be used as a context manager to keep the underlying
    HTTP session open for performance

**General Breaking changes**

This version uses a next-generation code generator that *might*
introduce breaking changes.

  - Model signatures now use only keyword-argument syntax. All
    positional arguments must be re-written as keyword-arguments. To
    keep auto-completion in most cases, models are now generated for
    Python 2 and Python 3. Python 3 uses the "*" syntax for
    keyword-only arguments.
  - Enum types now use the "str" mixin (class AzureEnum(str, Enum)) to
    improve the behavior when unrecognized enum values are encountered.
    While this is not a breaking change, the distinctions are important,
    and are documented here:
    <https://docs.python.org/3/library/enum.html#others> At a glance:
      - "is" should not be used at all.
      - "format" will return the string value, where "%s" string
        formatting will return `NameOfEnum.stringvalue`. Format syntax
        should be prefered.
  - New Long Running Operation:
      - Return type changes from
        `msrestazure.azure_operation.AzureOperationPoller` to
        `msrest.polling.LROPoller`. External API is the same.
      - Return type is now **always** a `msrest.polling.LROPoller`,
        regardless of the optional parameters used.
      - The behavior has changed when using `raw=True`. Instead of
        returning the initial call result as `ClientRawResponse`,
        without polling, now this returns an LROPoller. After polling,
        the final resource will be returned as a `ClientRawResponse`.
      - New `polling` parameter. The default behavior is
        `Polling=True` which will poll using ARM algorithm. When
        `Polling=False`, the response of the initial call will be
        returned without polling.
      - `polling` parameter accepts instances of subclasses of
        `msrest.polling.PollingMethod`.
      - `add_done_callback` will no longer raise if called after
        polling is finished, but will instead execute the callback right
        away.

**Bugfixes**

  - Compatibility of the sdist with wheel 0.31.0

## 3.0.1 (2018-01-25)

**Bugfixes**

  - Fix incorrect mapping in OrchestratorVersionProfileListResult

## 3.0.0 (2017-12-13)

  - Flattened ManagedCluster so there is no separate properties object
  - Added get_access_profiles operation to managed clusters

## 2.0.0 (2017-10-XX)

**Features**

  - Managed clusters

**Breaking changes**

  - VM is now require for master profile (recommended default:
    standard_d2_v2)

## 1.0.0 (2017-08-08)

  - Initial Release extracted from azure-mgmt-compute 2.1.0
