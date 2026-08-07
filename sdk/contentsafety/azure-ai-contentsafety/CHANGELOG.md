# Release History

## 1.1.0b1 (2026-08-03)

### Features Added

- Added support for the `2026-07-01-preview` API version.
- Added `ContentProvenanceClient`, which detects whether media was generated or modified by an AI system:
  - `begin_detect` starts a long-running provenance detection operation.
  - `get_operation_status` returns the status and result of a detection operation.
- Added models `DetectProvenanceOptions`, `DetectProvenanceResult`, `DetectedProvenance`, `ProvenanceContent`, and `ProvenanceDetectOperation`.
- Added enums `DetectedProvenanceType` and `ProvenanceOperationKind`.
- Added `shield_prompt` for shielding prompts from direct and indirect injection attacks.
- Added `detect_text_protected_material` for detecting protected material in text.

### Other Changes

- The minimum supported Python version is now 3.10 (previously 3.7).

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
