# Release History

## 1.0.0b4 (2022-05-13)

- Deprecate the package

## 1.0.0b3 (2021-10-25)

**Features**

  - Model ProxyResource has a new parameter system_data
  - Model Resource has a new parameter system_data
  - Model TrackedResource has a new parameter system_data
  - Model VideoAnalyzerUpdate has a new parameter provisioning_state
  - Model VideoAnalyzerUpdate has a new parameter iot_hubs
  - Model VideoAnalyzerUpdate has a new parameter network_access_control
  - Model VideoAnalyzerUpdate has a new parameter private_endpoint_connections
  - Model VideoAnalyzerUpdate has a new parameter public_network_access
  - Model VideoAnalyzer has a new parameter provisioning_state
  - Model VideoAnalyzer has a new parameter iot_hubs
  - Model VideoAnalyzer has a new parameter network_access_control
  - Model VideoAnalyzer has a new parameter private_endpoint_connections
  - Model VideoAnalyzer has a new parameter public_network_access
  - Model VideoEntity has a new parameter archival
  - Model VideoEntity has a new parameter content_urls
  - Added operation VideoAnalyzersOperations.begin_update
  - Added operation VideoAnalyzersOperations.begin_create_or_update
  - Added operation VideosOperations.list_content_token
  - Added operation group PrivateEndpointConnectionsOperations
  - Added operation group PrivateLinkResourcesOperations
  - Added operation group OperationStatusesOperations
  - Added operation group PipelineJobsOperations
  - Added operation group PipelineTopologiesOperations
  - Added operation group VideoAnalyzerOperationStatusesOperations
  - Added operation group LivePipelineOperationStatusesOperations
  - Added operation group LivePipelinesOperations
  - Added operation group OperationResultsOperations
  - Added operation group PipelineJobOperationStatusesOperations
  - Added operation group VideoAnalyzerOperationResultsOperations

**Breaking changes**

  - Parameter id of model StorageAccount is now required
  - Operation EdgeModulesOperations.list has a new signature
  - Operation EdgeModulesOperations.list has a new signature
  - Model VideoFlags no longer has parameter is_recording
  - Model VideoFlags has a new required parameter is_in_use
  - Model VideoEntity no longer has parameter streaming
  - Removed operation VideoAnalyzersOperations.create_or_update
  - Removed operation VideoAnalyzersOperations.update
  - Removed operation VideoAnalyzersOperations.sync_storage_keys
  - Removed operation VideosOperations.list_streaming_token

## 1.0.0b2 (2021-05-24)
  - Update README.md

## 1.0.0b1 (2021-05-11)

* Initial Release
