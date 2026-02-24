# Release History

## 1.0.0b1 (Unreleased)

### Features Added

- Added models `AssetStatisticsResponse`, `BandStatisticsMap`, `ClassMapLegendResponse`, `QueryableDefinitionsResponse`, `TilerAssetGeoJson`, `TilerInfoMapResponse`.
- `get_collection_queryables`, `list_queryables` now return `QueryableDefinitionsResponse`.
- `get_class_map_legend` now returns `ClassMapLegendResponse`.

### Breaking Changes

- Renamed `StacOperations.list_collections` to `StacOperations.get_collections`.
