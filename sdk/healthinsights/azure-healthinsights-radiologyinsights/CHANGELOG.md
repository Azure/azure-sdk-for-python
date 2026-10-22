# Release History

## 1.1.0 (2025-06-10)

Extending scope with inferences for scoring and assessment, quality measure and guidance.

### Features Added

- 3 new inferences added:
  - ScoringAndAssessmentInference
    - AssessmentValueRange
    - ScoringAndAssessmentCategoryType
  - GuidanceInference
    - GuidanceOptions
    - PresentGuidanceInformation
    - GuidanceRankingType
  - QualityMeasureInference
    - QualityMeasureOptions
    - QualityMeasureType
    - QualityMeasureComplianceType
- Added samples for scoring and assessment, Quality Measure and Guidance

## 1.0.0 (2024-09-10)

- GA release

### Breaking Changes

- Unique ID required to be added in the request parameters 
- models.PatientInfo renamed into models.PatientDetails
- models.Encounter renamed into models.PatientEncounter
- models.RadiologyInsightsResult renamed into models.RadiologyInsightsJob
- PatientDocument.created_date_time renamed into PatientDocument.created_at
- FollowupCommunication.datetime renamed into FollowupCommunication.communicated_at
- FollowupRecommendation.effective_date_time renamed into FollowupRecommendation.effective_at

## 1.0.0b1 (2024-03-01)

- Initial version
