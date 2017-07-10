.. :changelog:

Release History
===============

1.3.0 (2017-07-10)
++++++++++++++++++

**Features**

- Adding "available_private_access_services" operation group (2017-06-01)
- Adding "radius_secret" in Virtual Network Gateway

**Bug Fixes**

- VMSS Network ApiVersion fix in 2017-06-01 (point to 2017-03-30)

1.2.0 (2017-07-03)
++++++++++++++++++

**Features**

Adding the following features to both 2017-03-01 and 2017-06-01:

- express route ipv6
- VMSS Network (get, list, etc.)
- VMSS Public IP (get, list, etc.)

1.1.0 (2017-06-27)
++++++++++++++++++

**Features**

- Add list_usage in virtual networks (2017-03-01)

- Add ApiVersion 2017-06-01 (new default)

This new ApiVersion is for new Application Gateway features:

  - ApplicationGateway Ssl Policy custom cipher suites support [new properties added to Sslpolicy Property of ApplciationGatewayPropertiesFormat]
  - Get AvailableSslOptions api [new resource ApplicationGatewayAvailableSslOptions and child resource ApplicationGatewayPredefinedPolicy]
  - Redirection support [new child resource ApplicationGatewayRedirectConfiguration for Application Gateway,
    new properties in UrlPathMap, PathRules and RequestRoutingRule]
  - Azure Websites feature support [new properties in ApplicationGatewayBackendHttpSettingsPropertiesFormat,
    ApplicationGatewayProbePropertiesFormat, schema for property ApplicationGatewayProbeHealthResponseMatch]

1.0.0 (2017-05-15)
++++++++++++++++++

- Tag 1.0.0rc3 as stable (same content)

1.0.0rc3 (2017-05-03)
+++++++++++++++++++++

**Features**

- Added check connectivity api to network watcher

1.0.0rc2 (2017-04-18)
+++++++++++++++++++++

**Features**

- Add ApiVersion 2016-12-01 and 2017-03-01
- 2017-03-01 is now default ApiVersion

**Bugfixes**

- Restore access to NetworkWatcher and PacketCapture from 2016-09-01

1.0.0rc1 (2017-04-11)
+++++++++++++++++++++

**Features**

To help customers with sovereign clouds (not general Azure),
this version has official multi ApiVersion support for 2015-06-15 and 2016-09-01

0.30.1 (2017-03-27)
+++++++++++++++++++

* Add NetworkWatcher
* Add PacketCapture
* Add new methods to Virtualk Network Gateway

  * get_bgp_peer_status
  * get_learned_routes
  * get_advertised_routes

0.30.0 (2016-11-01)
+++++++++++++++++++

* Initial preview release. Based on API version 2016-09-01.


0.20.0 (2015-08-31)
+++++++++++++++++++

* Initial preview release. Based on API version 2015-05-01-preview.
