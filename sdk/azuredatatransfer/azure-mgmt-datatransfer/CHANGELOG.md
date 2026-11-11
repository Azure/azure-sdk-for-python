# Release History

## 1.0.0b3 (2026-11-11)

### Features Added

  - Client `DataTransferMgmtClient` added operation group `messaging_transfer_flows`
  - Client `DataTransferMgmtClient` added operation group `storage_transfer_flows`
  - Model `DirectionSettings` added property `messaging_location_mappings`
  - Model `DirectionSettings` added property `storage_location_mappings`
  - Enum `TargetType` added member `MESSAGING_TRANSFER_FLOW`
  - Enum `TargetType` added member `STORAGE_TRANSFER_FLOW`
  - Added enum `CommonTransferFlowStatus`
  - Added model `ListTransferFlowsByPipelineRequestBody`
  - Added model `ListTransferFlowsParameterBody`
  - Added model `ListTransferFlowsRequestBody`
  - Added model `LocationMapping`
  - Added model `MessagingTransferFlow`
  - Added model `MessagingTransferFlowProperties`
  - Added model `MessagingTransferFlowsPatch`
  - Added model `StorageTransferFlow`
  - Added model `StorageTransferFlowProperties`
  - Added model `StorageTransferFlowsPatch`
  - Added model `TransferFlowIdBody`
  - Added model `TransferFlowRequestBody`
  - Added model `TransferFlowResponseBody`
  - Added model `TransferFlowSummary`
  - Added enum `TransferRole`
  - Model `PipelinesOperations` added method `begin_approve_transfer_flow`
  - Model `PipelinesOperations` added method `begin_reject_transfer_flow`
  - Model `PipelinesOperations` added method `list_transfer_flows`
  - Added operation group `MessagingTransferFlowsOperations`
  - Added operation group `StorageTransferFlowsOperations`

## 1.0.0b2 (2026-11-06)

### Other Changes

  - Regular release

## 1.0.0b1 (2026-07-15)

### Other Changes

  - Initial version
