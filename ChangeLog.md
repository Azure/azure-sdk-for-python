## 2016.07.21 - Azure ARM version 0.4.0
* Regenerated ARM sdk with Autorest [autorest.0.17.0](https://github.com/Azure/autorest/commit/b54f66a4f6ddbe5d733b2e995ed29dac696c135e) along with new available swagger spec from [azure-rest-api-specs](https://github.com/Azure/azure-rest-api-specs)
* Releasing following new azure_mgmt_* gems
    * azure_mgmt_batch
    * azure_mgmt_cognitive_services
    * azure_mgmt_commerce
    * azure_mgmt_datalake_analytics
    * azure_mgmt_datalake_store
    * azure_mgmt_devtestlabs
    * azure_mgmt_dns
    * azure_mgmt_key_vault
    * azure_mgmt_logic
    * azure_mgmt_machine_learning
    * azure_mgmt_media_services
    * azure_mgmt_policy
    * azure_mgmt_powerbi_embedded
    * azure_mgmt_server_management
    * azure_mgmt_traffic_manager

## 2016.05.23 - Azure ARM version 0.3.1
* Regenerated ARM sdk with Autorest [autorest.0.17.0-Nightly20160519](https://www.myget.org/feed/autorest/package/nuget/autorest/0.17.0-Nightly20160522)
* Updating gemspec files to use the correct [homepage](https://github.com/Azure/azure-sdk-ruby) for each gem

## 2016.05.23 - Azure ARM version 0.3.0
* Regenerated ARM sdk with Autorest [autorest.0.17.0-Nightly20160519](https://www.myget.org/feed/autorest/package/nuget/autorest/0.17.0-Nightly20160522)
* Regenerated ARM sdk for newest published swagger specs from azure-rest-api-specs
    * azure_mgmt_cdn 2015-06-01 -> 2016-04-02
    * azure_mgmt_compute 2015-06-15 -> 2016-03-30
    * azure_mgmt_network 2015-06-15 -> 2016-03-30
    * azure_mgmt_resources 2015-11-01 -> 2016-02-01
    * azure_mgmt_scheduler 2016-01-01 -> 2016-03-01
    * azure_mgtm_storage 2015-06-15 -> 2016-01-01
* Updated tests to match new sdk
* Updated autorest location to point to environmental variable
* Updated min version of ms_rest_azure gem to 0.2.3
* Updated version of gems to 0.3.0 due to following breaking change:
    * introduced sync and async versions of operations

## 2016.05.05 - Azure ARM version 0.2.1
* Initializing repo after split from azure-sdk-for-ruby