# Release History

## 10.0.0b1 (2026-07-07)

### Features Added

  - Client `DnsManagementClient` added parameter `cloud_setting` in method `__init__`
  - Client `DnsManagementClient` added method `send_request`
  - Client `DnsManagementClient` added operation group `dnssec_configs`
  - Model `RecordSet` added property `properties`
  - Model `RecordSet` added property `system_data`
  - Enum `RecordType` added member `DS`
  - Enum `RecordType` added member `NAPTR`
  - Enum `RecordType` added member `TLSA`
  - Model `Resource` added property `system_data`
  - Model `Zone` added property `properties`
  - Model `Zone` added property `system_data`
  - Added model `CloudError`
  - Added enum `CreatedByType`
  - Added model `DelegationSignerInfo`
  - Added model `Digest`
  - Added model `DnsResourceReferenceRequestProperties`
  - Added model `DnsResourceReferenceResultProperties`
  - Added model `DnssecConfig`
  - Added model `DnssecProperties`
  - Added model `DsRecord`
  - Added model `NaptrRecord`
  - Added model `ProxyResource`
  - Added model `RecordSetProperties`
  - Added model `SigningKey`
  - Added model `SystemData`
  - Added model `TlsaRecord`
  - Added model `TrackedResource`
  - Added model `ZoneProperties`
  - Model `RecordSetsOperations` added parameter `etag` in method `create_or_update`
  - Model `RecordSetsOperations` added parameter `match_condition` in method `create_or_update`
  - Model `RecordSetsOperations` added parameter `etag` in method `delete`
  - Model `RecordSetsOperations` added parameter `match_condition` in method `delete`
  - Model `RecordSetsOperations` added parameter `etag` in method `update`
  - Model `RecordSetsOperations` added parameter `match_condition` in method `update`
  - Model `ZonesOperations` added parameter `etag` in method `begin_delete`
  - Model `ZonesOperations` added parameter `match_condition` in method `begin_delete`
  - Model `ZonesOperations` added parameter `etag` in method `create_or_update`
  - Model `ZonesOperations` added parameter `match_condition` in method `create_or_update`
  - Model `ZonesOperations` added parameter `etag` in method `update`
  - Model `ZonesOperations` added parameter `match_condition` in method `update`
  - Added model `DnssecConfigsOperations`

### Breaking Changes

  - Model `DnsResourceReferenceRequest` deleted or renamed its instance variable `target_resources`
  - Model `DnsResourceReferenceResult` deleted or renamed its instance variable `dns_resource_references`
  - Model `RecordSet` deleted or renamed its instance variable `metadata`
  - Model `RecordSet` deleted or renamed its instance variable `ttl`
  - Model `RecordSet` deleted or renamed its instance variable `fqdn`
  - Model `RecordSet` deleted or renamed its instance variable `provisioning_state`
  - Model `RecordSet` deleted or renamed its instance variable `target_resource`
  - Model `RecordSet` deleted or renamed its instance variable `a_records`
  - Model `RecordSet` deleted or renamed its instance variable `aaaa_records`
  - Model `RecordSet` deleted or renamed its instance variable `mx_records`
  - Model `RecordSet` deleted or renamed its instance variable `ns_records`
  - Model `RecordSet` deleted or renamed its instance variable `ptr_records`
  - Model `RecordSet` deleted or renamed its instance variable `srv_records`
  - Model `RecordSet` deleted or renamed its instance variable `txt_records`
  - Model `RecordSet` deleted or renamed its instance variable `cname_record`
  - Model `RecordSet` deleted or renamed its instance variable `soa_record`
  - Model `RecordSet` deleted or renamed its instance variable `caa_records`
  - Model `Resource` deleted or renamed its instance variable `location`
  - Model `Resource` deleted or renamed its instance variable `tags`
  - Model `Zone` deleted or renamed its instance variable `max_number_of_record_sets`
  - Model `Zone` deleted or renamed its instance variable `max_number_of_records_per_record_set`
  - Model `Zone` deleted or renamed its instance variable `number_of_record_sets`
  - Model `Zone` deleted or renamed its instance variable `name_servers`
  - Model `Zone` deleted or renamed its instance variable `zone_type`
  - Model `Zone` deleted or renamed its instance variable `registration_virtual_networks`
  - Model `Zone` deleted or renamed its instance variable `resolution_virtual_networks`
  - Deleted or renamed model `RecordSetListResult`
  - Deleted or renamed model `RecordSetUpdateParameters`
  - Deleted or renamed model `ZoneListResult`
  - Method `RecordSetsOperations.create_or_update` deleted or renamed its parameter `if_match` of kind `positional_or_keyword`
  - Method `RecordSetsOperations.create_or_update` deleted or renamed its parameter `if_none_match` of kind `positional_or_keyword`
  - Method `RecordSetsOperations.delete` deleted or renamed its parameter `if_match` of kind `positional_or_keyword`
  - Method `RecordSetsOperations.list_all_by_dns_zone` changed its parameter `record_set_name_suffix` from `positional_or_keyword` to `keyword_only`
  - Method `RecordSetsOperations.list_by_dns_zone` changed its parameter `recordsetnamesuffix` from `positional_or_keyword` to `keyword_only`
  - Method `RecordSetsOperations.list_by_type` changed its parameter `recordsetnamesuffix` from `positional_or_keyword` to `keyword_only`
  - Method `RecordSetsOperations.update` deleted or renamed its parameter `if_match` of kind `positional_or_keyword`
  - Method `ZonesOperations.begin_delete` deleted or renamed its parameter `if_match` of kind `positional_or_keyword`
  - Method `ZonesOperations.create_or_update` deleted or renamed its parameter `if_match` of kind `positional_or_keyword`
  - Method `ZonesOperations.create_or_update` deleted or renamed its parameter `if_none_match` of kind `positional_or_keyword`
  - Method `ZonesOperations.update` deleted or renamed its parameter `if_match` of kind `positional_or_keyword`
  - Method `ZonesOperations.create_or_update` re-ordered its parameters from `['self', 'resource_group_name', 'zone_name', 'parameters', 'if_match', 'if_none_match', 'kwargs']` to `['self', 'resource_group_name', 'zone_name', 'parameters', 'etag', 'match_condition', 'kwargs']`
  - Method `RecordSetsOperations.create_or_update` re-ordered its parameters from `['self', 'resource_group_name', 'zone_name', 'relative_record_set_name', 'record_type', 'parameters', 'if_match', 'if_none_match', 'kwargs']` to `['self', 'resource_group_name', 'zone_name', 'relative_record_set_name', 'record_type', 'parameters', 'etag', 'match_condition', 'kwargs']`

## 1.0.0b1 (1970-01-01)

### Other Changes

  - Initial version