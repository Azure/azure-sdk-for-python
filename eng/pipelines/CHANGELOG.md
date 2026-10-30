# Python pipeline change log

## Unreleased

### Fixed

- Forward the optional `ReleasePlanId` to release completion for every caller; the default `0` preserves the existing package-name lookup when no SDK PR is supplied.
- Use the existing test-pipeline flag for the template pilot's prepare-stage SDK PR binding, without service-directory-specific conditions or duplicate empty defaults. Normal service releases retain the shared template's empty SDK PR fallback and package-name lookup unless an explicit plan ID is supplied.
- Clarify the template pipeline's release-plan ID label and retain existing signing, publishing, approval, and release eligibility behavior.
