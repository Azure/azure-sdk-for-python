# Release History

## 1.1.0b1 (2026-08-03)

skip changelog generation for data-plane package and please add changelog manually.

## 1.0.0 (2023-12-15)

### Features Added

- Support Microsoft Entra ID Authentication
- Support 8 severity level for AnalyzeText

### Breaking Changes

Contract change for AnalyzeText, AnalyzeImage, Blocklist management related methods. The changes are listed below:

#### AnalyzeText

- AnalyzeTextOptions
  - Renamed breakByBlocklists to haltOnBlocklistHit
  - Added AnalyzeTextOutputType model for the `output_type` property.
- AnalyzeTextResult
  - Renamed TextBlocklistMatchResult to TextBlocklistMatch
  - Replaced TextAnalyzeSeverityResult by TextCategoriesAnalysis

#### AnalyzeImage

- AnalyzeImageOptions
  - Added AnalyzeImageOutputType
- AnalyzeImageResult
  - Replaced ImageAnalyzeSeverityResult by ImageCategoriesAnalysis

#### Blocklist management

- Added BlocklistClient
- Renamed AddBlockItemsOptions to AddOrUpdateTextBlocklistItemsOptions
- Renamed AddBlockItemsResult to AddOrUpdateTextBlocklistItemsResult
- Renamed RemoveBlockItemsOptions to RemoveTextBlocklistItemsOptions
- Renamed TextBlockItemInfo to TextBlocklistItem

## 1.0.0b1 (2023-05-22)

- Initial version
