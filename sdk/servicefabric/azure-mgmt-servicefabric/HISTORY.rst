.. :changelog:

Release History
===============

0.4.0 (2019-08-19)
++++++++++++++++++

**Features**

- Added operation ClustersOperations.create_or_update
- Added operation ServicesOperations.create_or_update
- Added operation ApplicationsOperations.create_or_update
- Added operation ApplicationTypesOperations.create_or_update
- Added operation ApplicationTypeVersionsOperations.create_or_update

**Breaking changes**

- Removed operation ClustersOperations.create
- Removed operation ServicesOperations.create
- Removed operation ApplicationsOperations.create
- Removed operation ApplicationTypesOperations.create
- Removed operation ApplicationTypeVersionsOperations.create

0.3.0 (2019-05-30)
++++++++++++++++++

**Breaking changes**

- Model ServiceTypeHealthPolicy has a new signature
- Model ApplicationHealthPolicy has a new signature
- Model ErrorModel has a new signature
- Renamed operation group "application_type" to "application_types"
- Renamed operation group "service" to "services"
- Renamed operation group "application" to "applications"
- Removed operation group "version"

**Features**

- Add tags and etag attributes where supported
- Model ClusterHealthPolicy has a new parameter application_health_policies
- Model ClusterUpgradeDeltaHealthPolicy has a new parameter application_delta_health_policies
- Model StatelessServiceProperties has a new parameter service_package_activation_mode
- Model ServiceResource has a new parameter service_package_activation_mode
- Model Cluster has a new parameter reverse_proxy_certificate_common_names
- Model Cluster has a new parameter certificate_common_names
- Model Cluster has a new parameter event_store_service_enabled
- Model StatefulServiceProperties has a new parameter service_package_activation_mode
- Model ClusterUpdateParameters has a new parameter certificate_common_names
- Model ClusterUpdateParameters has a new parameter event_store_service_enabled

0.2.0 (2018-08-01)
++++++++++++++++++

* New preview release, based on 2017-07-01-preview
* Expect many breaking changes

0.1.0 (2017-08-24)
++++++++++++++++++

* Initial preview release
