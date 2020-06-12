# Release History

## 0.2.0 (2020-04-12)

**Features**

  - Model PeeringServicePrefix has a new parameter peering_service_prefix_key
  - Model PeerAsn has a new parameter peer_contact_detail
  - Model PeeringService has a new parameter sku
  - Added operation group RegisteredPrefixesOperations
  - Added operation group PeeringServiceCountriesOperations
  - Added operation group RegisteredAsnsOperations

**Breaking changes**

  - Operation LegacyPeeringsOperations.list has a new signature
  - Operation PrefixesOperations.create_or_update has a new signature
  - Operation PeeringServiceLocationsOperations.list has a new signature
  - Model PeerAsn no longer has parameter peer_contact_info

## 0.1.0rc2 (2019-10-24)

**Breaking changes**

  - Migrated operations from PeeringServicePrefixesOperations to
    PrefixesOperations

## 0.1.0rc1 (2019-09-26)

  - Initial Release
