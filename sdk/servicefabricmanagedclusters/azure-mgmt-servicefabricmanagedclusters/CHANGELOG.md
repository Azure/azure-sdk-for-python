# Release History

## 1.0.0 (2021-04-27)

**Features**

  - Model ManagedCluster has a new parameter zonal_resiliency
  - Model ManagedCluster has a new parameter cluster_upgrade_mode
  - Model NodeType has a new parameter data_disk_type
  - Model NodeType has a new parameter multiple_placement_groups
  - Model NodeType has a new parameter is_stateless
  - Model LoadBalancingRule has a new parameter probe_port
  - Added operation group ManagedClusterVersionOperations

**Breaking changes**

  - Model StatelessServiceProperties no longer has parameter service_dns_name
  - Model StatelessServiceProperties no longer has parameter instance_close_delay_duration
  - Model ServiceResourceProperties no longer has parameter service_dns_name
  - Model AverageServiceLoadScalingTrigger has a new required parameter use_only_primary_load
  - Model StatefulServiceProperties no longer has parameter service_dns_name
  - Model StatefulServiceProperties no longer has parameter drop_source_replica_on_move

## 1.0.0b1 (2021-02-26)

* Initial Release
