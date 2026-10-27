# Python pipeline change log

## Unreleased

### Fixed

- Forward the optional `ReleasePlanId` to release completion for every caller; the default `0` preserves the existing package-name lookup when no SDK PR is supplied.
- Bind the prepare-stage SDK PR output once in the completion job without service-directory-specific conditions or empty defaults, and use the shared completion template's optional SDK PR fallback and initializer.
- Clarify the template pipeline's release-plan ID label and retain existing signing, publishing, approval, and release eligibility behavior.
