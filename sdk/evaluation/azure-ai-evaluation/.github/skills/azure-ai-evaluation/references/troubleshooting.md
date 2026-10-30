# Diagnose before retrying

Use read-only `azsdk_get_pipeline_status`; load `azsdk-common-pipeline-analysis` before `azsdk_analyze_pipeline`. Read-only `az`/`gh` diagnostics are distinct from publication: no CLI release fallback. Never log credentials/customer payloads.

| Symptom | Evidence and next action |
|---|---|
| Green run, no package | Match definition 7162, branch/SHA and artifact version. An old successful URL may be the previous release. Inspect `Release_azureaievaluation` separately from Build. |
| Release skipped | Inspect `AutoReleasePrepare` and `ReleaseArtifact_azureaievaluation`. Missing/unlabeled PRs, unmatched packages or resolver errors emit `false` and exit zero: **skipped**, not awaiting approval. Also inspect `Skip.Release`, `SetDevVersion`, dependencies and build reason. |
| Label added late | Cached output remains false. An authorized owner must re-evaluate the resolver on the correct source commit and dependent release stage, or use the documented authorized manual route. Retrying Release alone cannot repair eligibility. Verify new output. |
| API approval false | Verify revision/version and gate. Name approval is not revision approval. Request current reviewer action; no break-glass switches, disabled checks, hidden notes or inferred exceptions. `azsdk_package_get_approval_status` can report API Review Hub `unknownPackage` while APIView (legacy) separately shows `isApproved: true` for the same package/version — read the final merged result and its source, not only the first sub-result. |
| App PR 403 | App/enterprise-managed-user identity, CLI identity and SAML/SSO grants are separate. Successful `gh` authentication does not fix the app. Explain app relinking/access repair or provide a verified fork/base compare URL for manual creation. No retry loop or `gh pr create` bypass. |
| Existing PyPI target | Confirm exact-version artifacts/source. Never overwrite, silently bump or republish. If the fix is absent, obtain a newly classified version and approvals. |
| Default Python resolves too old | `azpysdk`/release scripts require Python >= 3.10; a shell's default interpreter can still be 3.9. Run `python --version` (and `py -0p` on Windows) before invoking tooling; activate the correct venv instead of assuming the active shell is already compliant. |
| Deletions silently incomplete on Windows | Long repository paths (Chronus/node installs, nested `node_modules`) can exceed Windows path limits; a delete can report success while leaving residual files. Verify with a fresh listing after deletion, enable `git config core.longpaths true` or use a short-path tool, and never assume exit code 0 proves removal. |
| "Green" run doesn't match the release | A scheduled/nightly pipeline run can be green while the actual PR/commit being released never ran that pipeline, or ran an older one. Match the run's triggering PR number and source SHA exactly before citing it as release evidence; a same-named green run elsewhere is not substitute evidence. |

## Preparation and Chronus failures

The script's "latest released version" enumerates PyPI names, not a semantic maximum. Compare `info.version` and release metadata; lexical ordering can put an older minor last.

Missing `uv` virtual-environment errors can coexist with outer exit zero. Inspect output, both local files and tracking. Repair the approved environment before retrying: tracking may already have changed. Do not report false local-only success.

Compare the wrapper's `_CHRONUS_INSTALL_DIR`/binary path with `.github\chronus\package.json` and lockfile. At authoring time it expects `.github`, not `.github\chronus`; re-check, since this mismatch may be fixed.

If mismatched, stop before accepting installation. With approved pinned tooling already installed, the root-level package-scoped equivalent is:

```powershell
.\.github\chronus\node_modules\.bin\chronus.cmd status --only azure-ai-evaluation
# Only after approval for local edits:
.\.github\chronus\node_modules\.bin\chronus.cmd changelog --package azure-ai-evaluation
```

Do not install unrelated dependencies or alter manifests. After a missing-tool failure, use approved pinned setup within installation authorization. For npm E401, report registry/authentication blockers without tokens; never remove auth or switch registries to bypass them — this is an environment/registry-authentication condition, not a defect in this skill's instructions. Manual collection needs policy-consistent maintainer approval, exact-once notes and appropriate fragment consumption.

Handoff: observed command/task, sanitized error, local/remote state and next owner action. No guessed success or implied authorization.
