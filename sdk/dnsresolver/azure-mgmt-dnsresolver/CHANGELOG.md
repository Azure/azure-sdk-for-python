# Release History

## 1.1.0b1 (2022-12-27)

### Other Changes

  - Added generated samples in github repo
  - Drop support for python<3.7.0

## 1.0.0 (2022-09-15)

### Features Added

  - Model DnsForwardingRulesetPatch has a new parameter dns_resolver_outbound_endpoints

### Breaking Changes

  - Parameter dns_resolver_outbound_endpoints of model DnsForwardingRuleset is now required
  - Parameter domain_name of model ForwardingRule is now required
  - Parameter id of model SubResource is now required
  - Parameter ip_address of model TargetDnsServer is now required
  - Parameter ip_configurations of model InboundEndpoint is now required
  - Parameter subnet of model IpConfiguration is now required
  - Parameter subnet of model OutboundEndpoint is now required
  - Parameter target_dns_servers of model ForwardingRule is now required
  - Parameter virtual_network of model DnsResolver is now required
  - Parameter virtual_network of model VirtualNetworkLink is now required

## 1.0.0b1 (2022-02-21)

* Initial Release
