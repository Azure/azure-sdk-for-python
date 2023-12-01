# Release History

## 1.0.0 (Unreleased)

### Features Added

- Support AAD Authentication
- Support 8 severity level for AnalyzeText

### Breaking Changes

Contract change for AnalyzeText, AnalyzeImage, Blocklist management related methods. The changes are listed below:

#### AnalyzeText

- AnalyzeTextOptions
  - Renamed breakByBlocklists to haltOnBlocklistHit
  - Added AnalyzeTextOutputType model for the `output_type` property.
- AnalyzeTextResult
  - Renamed blocklistsMatchResults to blocklistsMatch
  - Replaced TextAnalyzeSeverityResult by TextCategoriesAnalysis

#### AnalyzeImage

- AnalyzeImageOptions
  - Replaced ImageData by ContentSafetyImageData
  - Add AnalyzeImageOutputType
- AnalyzeImageResult
  - Replaced ImageAnalyzeSeverityResult by ImageCategoriesAnalysis

#### Blocklist management

- Added BlocklistAsyncClient
- Renamed AddBlockItemsOptions to AddOrUpdateTextBlocklistItemsOptions
- Renamed AddBlockItemsResult to AddOrUpdateTextBlocklistItemsResult
- Renamed RemoveBlockItemsOptions to RemoveTextBlocklistItemsOptions
- Renamed TextBlockItemInfo to TextBlocklistItem

## 1.0.0b1 (2023-05-22)

- Initial version
