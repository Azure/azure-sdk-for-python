# Python pipeline change log

## Unreleased

### Fixed

- Forward the optional `ReleasePlanId` to release completion for every caller; the default `0` preserves the existing package-name lookup when no SDK PR is supplied.
- Scope the template automatic-release PR output to the completion job, with an explicit empty value for manual releases and other callers. Automatic PR correlation remains limited to the template pilot.
- Clarify the template pipeline's release-plan ID label and retain existing signing, publishing, approval, and release eligibility behavior.
