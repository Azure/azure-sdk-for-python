# 2026-11-01-preview generation

Generation inputs are `Azure/azure-rest-api-specs` commit
`b41ba04c0219f6622b7f5214fc020f90bad339ae`,
`specification/search/data-plane/Search/client.tsp` and `tspconfig.yaml`.
The repository-pinned `tsp-client` 0.33.1 resolves
`@azure-tools/typespec-python` 0.63.10. Run from the package directory:

```powershell
npm exec --prefix C:\sdk-dp1101\python\eng\common\tsp-client --no -- tsp-client update --no-prompt --save-inputs
python .github\skills\azure-search-documents\scripts\apply_generator_workarounds.py
```

## Customization diagnosis

The pinned `client.tsp` intentionally renames generated resource-list methods to
`list_synonym_maps`, `list_indexers`, `list_skillsets`, and
`list_data_source_connections`. Unmodified existing Python wrappers call removed
`_get_*` methods; eight existing sync/async unit tests fail with `AttributeError`.
The wrappers now call the renamed generated methods, preserving their public
`get_*` names, list return values, and paging options. This is Python compatibility
behavior, not a service-contract or emitter defect.

The generated `SearchRequest` supports `more_like_this` and `agentic_options`,
but Python's existing custom search pager builds that request itself. These
parameters must be forwarded by both handwritten search methods and their shared
request builder. Generated vector-query models already serialize the three
topic-graph discriminators, so no model workaround is needed for that feature.
The index-list projection converter also explicitly copies the new graph and
OneLake security configuration and the restored SharePoint connector registration;
the generated response model carries these fields but the older handwritten
field-by-field conversion omitted them. Async lists reuse this same converter.

The service intentionally moved `fieldName` and `boost` from `ScoringFunction`
into its classic derived models to permit random scoring without these fields.
The generated base consequently rejects the previously accepted Python keywords.
A compatibility subclass restores these two fields on the public base.
Concrete subclasses retain their generated implementations and inherit the public
compatibility base so `isinstance` and polymorphic deserialization still work.
Random scoring does not emit field or boost values unless explicitly supplied.
This preserves SDK-owned compatibility without changing the pinned service
contract or generator.

The Python emitter's File-ingestion LRO output refers to
`_indexes_models1.KnowledgeSourceFile`, but imports that namespace as `_models1`
(sync) or `_models2` (async). This produces eight MyPy errors and raises
`NameError` when creating or resuming the two ingestion pollers. The emitter's
`builder_serializer.py` uses `get_poller_with_response_type()` for these runtime
generic expressions, independently of the aliases used in its imports.
The package-owned exact-match post-generation rewriter replaces these eight
references; regression tests exercise both pollers with polling disabled.
Report this namespace-alias mismatch upstream to `@typespec/http-client-python`
with the pinned Search reproduction. Remove the two replacements after
regenerating with an emitter whose unmodified output passes those tests and MyPy.
The existing workaround script otherwise remains unchanged; no public-spec or
shared generator modification is used.
The same rewriter applies narrow generated-code pylint complexity comments to the
expanded `SearchField` overload and generated SSE methods; handwritten complexity
limits remain unchanged.
Generated defaults follow the new preview; explicit older `api_version` values
and all previously advertised enum members remain available.

The spec revision above advances the original pin
`2c0ca3a8b788bc866d2312b72bc05b49b048973d` only for topic-graph descriptions and
an example correction; it does not change the wire contract or SDK version.

## Documentation diagnostics

Public CI build 6992015 fails Sphinx on `QueryDebugMode.AGENTIC` with
`Inline substitution_reference start-string without end-string`. The
`models-index.tsp` description contains the language-neutral text
`supported modes using |;`. The pinned Python emitter delegates enum member
descriptions to `enum.py.jinja2`, which wraps the text without escaping this
reStructuredText delimiter. Sphinx obtains member documentation from the source
literal, not the enum member's runtime `__doc__`; a runtime customization cannot
repair that source. The package-owned exact-match post-generation rewriter
formats the separator as an inline literal, preserving its documentation and
runtime value. This avoids changing the signed-off shared spec or hand-editing
generated files. The regression test checks the member's source documentation;
the package Sphinx build checks the actual rendered result. Report the unescaped
enum delimiter to `@typespec/http-client-python`, and remove the replacement once
unmodified generated documentation passes both checks.

## Recording prerequisites

Public CI build 6992015 has 160 failing recorded tests and 206 passing offline
tests on each sampled platform. All 160 distinct failures in the Windows,
Ubuntu, and macOS task logs request `2026-11-01-preview` while their matching
recordings use `2026-08-01-preview`. These recordings must be refreshed against
an authorized service, not edited to impersonate new service responses.

Follow the repository [testing guide](../../../../doc/dev/tests.md) and the
package's [environment template](../.github/skills/azure-search-documents/scripts/Set-LiveTestEnvironment.sample.ps1).
Before recording, confirm:

- A dedicated disposable Search service supports the November preview, semantic
  ranking, knowledge bases/sources, and File ingestion. The live-test preparer
  deletes existing indexes, knowledge resources, synonym maps, aliases, indexers,
  data sources, and skillsets; do not point it at a shared or production service.
- `SEARCH_SERVICE_ENDPOINT` and `SEARCH_SERVICE_NAME` identify that service.
  The signed-in principal needs Search Service Contributor and Search Index Data
  Contributor, as in the [test-resource template](../../test-resources.bicep).
- `SEARCH_STORAGE_CONNECTION_STRING` and `SEARCH_STORAGE_CONTAINER_NAME` identify
  existing Blob fixtures for indexer tests. Keep the connection string in an
  approved local secret store/environment, never in chat or committed files.
- `SEARCH_AZURE_OPENAI_ENDPOINT`, `SEARCH_AZURE_OPENAI_EMBEDDING_DEPLOYMENT`, and
  `SEARCH_AZURE_OPENAI_EMBEDDING_MODEL` identify an existing embedding deployment.
  File tests pass no OpenAI API key, so the Search service needs a managed
  identity authorized to use that deployment.

An existing Azure CLI login is supported by `get_credential()` when
`AZURE_TEST_USE_CLI_AUTH=true`; no client secret or Search admin key is required
by the current recorded suite. CLI login does not provide the storage connection
string or configure service-side OpenAI access. Separate performance scenarios
using `AzureKeyCredential` additionally require their documented API key.

Only after the environment is approved, set `AZURE_TEST_RUN_LIVE=true` and leave
`AZURE_SKIP_LIVE_RECORDING` unset/false, run the live tests, and inspect sanitized
recordings before updating the package's asset tag. No live run or resource
provisioning was performed for this CI repair.
