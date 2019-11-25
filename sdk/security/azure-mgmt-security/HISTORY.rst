.. :changelog:

Release History
===============

0.3.0 (2019-08-01)
++++++++++++++++++

**Features**

- Model JitNetworkAccessPolicyVirtualMachine has a new parameter public_ip_address
- Model JitNetworkAccessRequestPort has a new parameter mapped_port
- Added operation group RegulatoryComplianceControlsOperations
- Added operation group ComplianceResultsOperations
- Added operation group ServerVulnerabilityAssessmentOperations
- Added operation group IoTSecuritySolutionsResourceGroupOperations
- Added operation group AdaptiveApplicationControlsOperations
- Added operation group IoTSecuritySolutionsOperations
- Added operation group IotSecuritySolutionOperations
- Added operation group RegulatoryComplianceStandardsOperations
- Added operation group IoTSecuritySolutionsAnalyticsOperations
- Added operation group IoTSecuritySolutionsAnalyticsAggregatedAlertOperations
- Added operation group IoTSecuritySolutionsAnalyticsRecommendationsOperations
- Added operation group RegulatoryComplianceAssessmentsOperations
- Added operation group IoTSecuritySolutionsAnalyticsRecommendationOperations
- Added operation group IoTSecuritySolutionsAnalyticsAggregatedAlertsOperations

**General breaking changes**  

This version uses a next-generation code generator that *might* introduce breaking changes if from some import.
In summary, some modules were incorrectly visible/importable and have been renamed. This fixed several issues caused by usage of classes that were not supposed to be used in the first place.

- SecurityCenter cannot be imported from `azure.mgmt.security.security_center` anymore (import from `azure.mgmt.security` works like before)
- SecurityCenterConfiguration import has been moved from `azure.mgmt.security.security_center` to `azure.mgmt.security`
- A model `MyClass` from a "models" sub-module cannot be imported anymore using `azure.mgmt.security.models.my_class` (import from `azure.mgmt.security.models` works like before)
- An operation class `MyClassOperations` from an `operations` sub-module cannot be imported anymore using `azure.mgmt.security.operations.my_class_operations` (import from `azure.mgmt.security.operations` works like before)
                
Last but not least, HTTP connection pooling is now enabled by default. You should always use a client as a context manager, or call close(), or use no more than one client per process.

0.2.0 (2019-04-16)
++++++++++++++++++

**Features**

- Model Pricing has a new parameter free_trial_remaining_time
- Model Alert has a new parameter is_incident
- Added operation PricingsOperations.get
- Added operation PricingsOperations.update
- Added operation group AllowedConnectionsOperations

**Breaking changes**

- Operation SettingsOperations.update has a new signature
- Removed operation PricingsOperations.update_subscription_pricing
- Removed operation PricingsOperations.list_by_resource_group
- Removed operation PricingsOperations.create_or_update_resource_group_pricing
- Removed operation PricingsOperations.get_resource_group_pricing
- Removed operation PricingsOperations.get_subscription_pricing

0.1.0 (2018-10-29)
++++++++++++++++++

* Initial Release
