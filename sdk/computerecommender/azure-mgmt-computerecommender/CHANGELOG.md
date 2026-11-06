# Release History

## 1.0.0b4 (2026-11-05)

### Features Added

  - Client `RecommenderMgmtClient` added operation group `compute_placement_scores`
  - Model `PlacementScore` added property `placement_preference`
  - Added model `ComputePlacementScoresBase`
  - Added model `ComputePlacementScoresInput`
  - Added model `ComputePlacementScoresResponse`
  - Added enum `PlacementScoreValue`
  - Added model `PlacementScoresProperties`
  - Added model `SpotPlacementScoresBase`
  - Added operation group `ComputePlacementScoresOperations`

### Breaking Changes

  - Model `PlacementScore` deleted or renamed its instance variable `is_quota_available`
  - `SpotPlacementScoresInput.desired_sizes` is now required.
  - Deleted or renamed model `ComputeDiagnosticBase`
  - Deleted or renamed model `DiagnosticProperties`
  - Model `ComputePlacementScoresBase` changed type of its property `properties` from `DiagnosticProperties` to `PlacementScoresProperties`
  - Method `SpotPlacementScoresOperations.get` changed return type from `ComputeDiagnosticBase` to `SpotPlacementScoresBase`

## 1.0.0b3 (2026-08-28)

### Features Added

  - Model `SkuMixPlacementResponse` added property `capacity_limits`
  - Model `SkuMixPlacementResponse` added property `id`
  - Added model `SkuMixPlacementCapacityLimit`
  - Added enum `SkuMixPlacementCapacityLimitReason`

### Breaking Changes

  - Model `SkuMixPlacementDeploymentChoice` deleted or renamed its instance variable `id`
  - Model `SkuMixPlacementItem` deleted or renamed its instance variable `capacity_max`

## 1.0.0b2 (2026-08-03)

### Features Added

  - Client `RecommenderMgmtClient` added operation group `sku_mix_placement_scores`
  - Added enum `SkuMixPlacementAllocationStrategy`
  - Added model `SkuMixPlacementBase`
  - Added model `SkuMixPlacementCapacityProfile`
  - Added enum `SkuMixPlacementCapacityType`
  - Added model `SkuMixPlacementDeploymentChoice`
  - Added model `SkuMixPlacementInstanceDescription`
  - Added model `SkuMixPlacementItem`
  - Added enum `SkuMixPlacementOSType`
  - Added enum `SkuMixPlacementPartialFulfillmentReason`
  - Added enum `SkuMixPlacementPriority`
  - Added model `SkuMixPlacementProperties`
  - Added model `SkuMixPlacementRequest`
  - Added model `SkuMixPlacementResponse`
  - Added model `SkuMixPlacementSpotPriorityProfile`
  - Added model `SkuMixPlacementVMSize`
  - Added enum `SkuMixPlacementZonalDistributionStrategy`
  - Added model `SkuMixPlacementZoneAllocationPolicy`
  - Added model `SkuMixPlacementZonePreference`

## 1.0.0b1 (2025-09-04)

### Other Changes

  - Initial version
