# Azure Search Documents 2026-08-01-preview Gap Disposition

This report verifies the Python SDK against Azure/azure-rest-api-specs commit
`c195a3fe73b28cd90bf8a302944b2c0ec3d80def` and the package-specific regeneration,
testing, and release guidance.

## Resolved locally

| Finding | Resolution |
|---|---|
| File update argument order | Added sync and async `_patch.py` wrappers exposing `update_knowledge_source_file(name, file_id, body)` and forwarding to generated code by keyword. Focused tests verify both signatures and delegation. |
| Stream class namespace | Set `KnowledgeBaseRetrievalStream.__module__` to `azure.search.documents.knowledgebases` and `AsyncKnowledgeBaseRetrievalStream.__module__` to `azure.search.documents.knowledgebases.aio`. |
| File operation coverage | Added sync and async tests for the customized File update operation. Registered both update and multipart upload operations in the preview capability surface. |
| Listing capability and wrapper coverage | Registered `search`, `page_size`, and `search_type` on all August list surfaces, plus File-list `prefix`. Added sync and async forwarding tests for the four SDK-owned list wrappers. |
| Streaming asymmetry | Added async deserialization coverage for all known event types and mirrored both authorization-header forwarding assertions in sync and async tests. |
| Stale preview capabilities | Removed `WorkIQAttribution`, `McpServerTool.inclusion_mode`, and removed inclusion-mode enum members. Added `KnowledgeBaseWorkIQReference.search_sensitivity_label_info` and current August operation/parameter capabilities. All registered capabilities now resolve. |
| Generator workaround drift | Added a package test that executes `apply_generator_workarounds.py --check`. Updated the script to skip obsolete issue shapes only when the affected generated feature is absent, while retaining fail-fast behavior for unknown output. |
| Generated ingestion-parameter import | Corrected the generated `indexes.types` type-only import to resolve `KnowledgeSourceIngestionParameters` from the public `knowledgebases.models` namespace. Added the exact repair to the package-owned post-generation workaround. |
| APIView artifact refresh | Regenerated `api.md` and `api.metadata.yml` from the fresh token. The artifact now shows `update_knowledge_source_file(name, file_id, body)` and both stream classes in their public namespaces. |
| Release notes | Updated the pinned TypeSpec commit, removed the post-cut logical-reasoning claim, and recorded the SDK-owned signature and namespace fixes. |

## Findings rejected

### Generated `types` modules are not missing from `__all__`

The three `types` modules are explicitly importable and documented. Azure SDK package `__all__`
lists public symbols for wildcard imports, not submodule objects. Adding `types` would diverge from
repository-wide generated package conventions without improving explicit imports or APIView.

### Generated base-client API-version prose is not the exported client contract

Generated base clients describe `api_version=None`, meaning “use the operation default.” The
exported clients are package `_patch.py` subclasses whose docstrings name
`ApiVersion.V2026_08_01_PREVIEW`, and every configuration resolves an omitted value to
`"2026-08-01-preview"`. Editing generated base files would be overwritten and is prohibited by the
package customization guide.

### Shared event exports in the async namespace are intentional convenience exports

`KnowledgeBaseRetrievalEvent` and `KnowledgeBaseRetrievalEventData` are transport-neutral event
types used by both stream implementations. Keeping them available from the async namespace avoids
forcing async users to import the synchronous package. Their canonical module remains
`azure.search.documents.knowledgebases`; removing the async aliases would be an unnecessary preview
breaking change.

## Remaining gaps

### Multipart File service recording

The new multipart upload and update service behavior does not yet have a recorded live pytest using
a File knowledge source. Public surface, request models, samples, capability registration, and the
SDK-owned update wrapper are covered locally, but a Test Proxy recording requires provisioned File
knowledge-source resources. Before declaring live-sample coverage complete, record matching sync and
async tests for multipart upload/update and push the updated `assets.json` tag. This does not block
unit, MyPy, Pylint, Sphinx, or existing playback validation.

### Changelog verifier integration

The package `CHANGELOG.md` is updated for `12.1.0b2`, but `azpysdk changelog verify` cannot use the
repository-pinned Chronus installation because the launcher hardcodes `.github/package.json` and
`.github/node_modules/.bin/chronus`; the actual pinned project and lockfile are under
`.github/chronus`. Invoking that pinned Chronus binary directly reports that
`azure-search-documents` has no pending changeset. The package release guide still documents direct
`CHANGELOG.md` maintenance, and adding a `feature` changeset would request a new minor version rather
than the planned beta patch. The repository changelog-tool owner should reconcile the launcher path
and release workflow before Chronus verification is treated as a package blocker.

## APIView export environment disposition

`azpysdk apistub .` successfully generates a fresh `azure-search-documents_python.json` token. The
token contains the corrected public `update_knowledge_source_file(name, file_id, body)` signature and
the public stream namespaces.

The system-installed PowerShell 7.6.4 runtime aborted with a stack overflow on every command tested,
including `1+1`, `Write-Output`, and two-byte JSON parsing. Package integrity verification reported
no modified installed files. Side-by-side Microsoft PowerShell 7.6.3 and 7.5.9 packages passed the
same runtime smoke tests, identifying 7.6.4 as the regression boundary. The APIView failure also
reproduced for the released `azure-search-documents==12.1.0b1` wheel, proving it was not caused by
this SDK surface. PowerShell 7.5.9 completed the supported `azpysdk apistub .` workflow. No API
artifact was hand-edited.

## Local release validation

The following checks pass on the final local package:

- Tests: 336 passed, with no failures, skips, or warnings.
- MyPy: 74 source files and 64 sample files pass.
- Pylint: no warnings or errors.
- Sphinx: strict build passes with no warnings.
- Black: formatting passes with no changes.
- VerifyTypes: passes with 99.5% completeness; remaining partial types are existing dynamic
	patch/mixin annotations and are nonblocking.
- Import-all, sdist verification, wheel verification, and Bandit all pass.

The aggregate Azure SDK MCP check could not start its server, so equivalent local `azpysdk` checks
were run individually. APIView token, Markdown, and metadata generation pass with PowerShell 7.5.9;
the system PowerShell 7.6.4 installation remains unusable and should be downgraded or repaired before
future APIView regeneration.