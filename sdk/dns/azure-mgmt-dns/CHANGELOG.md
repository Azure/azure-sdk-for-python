# Release History

## 10.0.0b1 (2026-07-07)

### Features Added

  - Client `DnsManagementClient` added parameter `cloud_setting` in method `__init__`
  - Client `DnsManagementClient` added method `send_request`
  - Client `DnsManagementClient` added operation group `dnssec_configs`
  - Model `RecordSet` added property `system_data`
  - Enum `RecordType` added member `DS`
  - Enum `RecordType` added member `NAPTR`
  - Enum `RecordType` added member `TLSA`
  - Model `Resource` added property `system_data`
  - Model `Zone` added property `system_data`
  - Added model `CloudError`
  - Added enum `CreatedByType`
  - Added model `DelegationSignerInfo`
  - Added model `Digest`
  - Added model `DnssecConfig`
  - Added model `DnssecProperties`
  - Added model `DsRecord`
  - Added model `NaptrRecord`
  - Added model `ProxyResource`
  - Added model `SigningKey`
  - Added model `SystemData`
  - Added model `TlsaRecord`
  - Added model `TrackedResource`
  - Added operation group `DnssecConfigsOperations`

### Breaking Changes

  - This version introduces new hybrid models which have dual dictionary and model nature. Please follow https://aka.ms/azsdk/python/migrate/hybrid-models for migration.
  - For the method breakings, please refer to https://aka.ms/azsdk/python/migrate/operations for migration.
  - Model `DnsResourceReferenceRequest` moved instance variable `target_resources` under property `properties` whose type is `DnsResourceReferenceRequestProperties`
  - Model `DnsResourceReferenceResult` moved instance variable `dns_resource_references` under property `properties` whose type is `DnsResourceReferenceResultProperties`
  - Model `RecordSet` moved instance variable `metadata`, `ttl`, `fqdn`, `provisioning_state`, `target_resource`, `a_records`, `aaaa_records`, `mx_records`, `ns_records`, `ptr_records`, `srv_records`, `txt_records`, `cname_record`, `soa_record` and `caa_records` under property `properties` whose type is `RecordSetProperties`
  - Model `Resource` deleted or renamed its instance variable `location`
  - Model `Resource` deleted or renamed its instance variable `tags`
  - Model `Zone` moved instance variable `max_number_of_record_sets`, `max_number_of_records_per_record_set`, `number_of_record_sets`, `name_servers`, `zone_type`, `registration_virtual_networks` and `resolution_virtual_networks` under property `properties` whose type is `ZoneProperties`
  - Method `RecordSetsOperations.create_or_update` replaced positional_or_keyword parameters `if_match`/`if_none_match` to keyword_only parameters `etag`/`match_condition`
  - Method `RecordSetsOperations.delete` replaced positional_or_keyword parameter `if_match` to keyword_only parameters `etag`/`match_condition`
  - Method `RecordSetsOperations.list_all_by_dns_zone` changed its parameter `record_set_name_suffix` from `positional_or_keyword` to `keyword_only`
  - Method `RecordSetsOperations.list_by_dns_zone` changed its parameter `recordsetnamesuffix` from `positional_or_keyword` to `keyword_only`
  - Method `RecordSetsOperations.list_by_type` changed its parameter `recordsetnamesuffix` from `positional_or_keyword` to `keyword_only`
  - Method `RecordSetsOperations.update` replaced positional_or_keyword parameter `if_match` to keyword_only parameters `etag`/`match_condition`
  - Method `ZonesOperations.begin_delete` replaced positional_or_keyword parameter `if_match` to keyword_only parameters `etag`/`match_condition`
  - Method `ZonesOperations.create_or_update` replaced positional_or_keyword parameters `if_match`/`if_none_match` to keyword_only parameters `etag`/`match_condition`
  - Method `ZonesOperations.update` replaced positional_or_keyword parameter `if_match` to keyword_only parameters `etag`/`match_condition`

### Other Changes

  - Deleted model `RecordSetListResult`/`ZoneListResult` which actually were not used by SDK users
  - Deleted model `RecordSetUpdateParameters` which actually were not used by SDK users

## 1.0.0b1 (1970-01-01)

### Other Changes

  - Initial version