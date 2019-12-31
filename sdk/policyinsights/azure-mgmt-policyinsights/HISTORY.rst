.. :changelog:

Release History
===============

0.4.0 (2019-12-31)
++++++++++++++++++

**Features**

- Model PolicyDefinitionSummary has a new parameter policy_definition_group_names
- Model Remediation has a new parameter resource_discovery_mode
- Model PolicyAssignmentSummary has a new parameter policy_groups
- Model PolicyState has a new parameter policy_definition_group_names
- Model SummaryResults has a new parameter policy_group_details
- Model SummaryResults has a new parameter policy_details
- Model SummaryResults has a new parameter resource_details
- Added operation group PolicyMetadataOperations

**Breaking changes**

- Removed operation PolicyStatesOperations.get_metadata

**General Breaking Changes**

This version uses a next-generation code generator that might introduce breaking changes if from some import. In summary, some modules were incorrectly visible/importable and have been renamed. This fixed several issues caused by usage of classes that were not supposed to be used in the first place.
PolicyInsightsClient cannot be imported from azure.mgmt.policyinsights.policy_insights_client anymore (import from azure.mgmt.policyinsights works like before)
PolicyInsightsClientConfiguration import has been moved from azure.mgmt.policyinsights.policy_insights_client to azure.mgmt.policyinsights
A model MyClass from a "models" sub-module cannot be imported anymore using azure.mgmt.policyinsights.models.my_class (import from azure.mgmt.policyinsights.models works like before)
An operation class MyClassOperations from an operations sub-module cannot be imported anymore using azure.mgmt.policyinsights.operations.my_class_operations (import from azure.mgmt.policyinsights.operations works like before)
Last but not least, HTTP connection pooling is now enabled by default. You should always use a client as a context manager, or call close(), or use no more than one client per process.

0.3.1 (2019-04-16)
++++++++++++++++++

**Bugfixes**

- Fix expressionValues and targetValues type

0.3.0 (2019-03-12)
++++++++++++++++++

**Features**

- Model QueryOptions has a new parameter expand
- Model PolicyState has a new parameter policy_evaluation_details
- Model PolicyState has a new parameter compliance_state

0.2.0 (2019-01-02)
++++++++++++++++++

**Features**

- Added operation group RemediationsOperations
- Added operation group PolicyTrackedResourcesOperations

0.1.0 (2018-05-04)
++++++++++++++++++

* Initial Release
