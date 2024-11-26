# Release History

## 1.0.1 (Unreleased)

### Features Added

### Breaking Changes

### Bugs Fixed

### Other Changes

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
