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

## Retrieval stream contract

With the generation inputs recorded above, both generated `retrieve_stream`
methods pass a typed `Stream` or `AsyncStream` to `cls`, not an iterator of raw
bytes. Genuine November recording reproduced `TypeError` when the handwritten
wrapper fed those already-deserialized events into its SSE byte decoder.
An initial response-byte workaround avoided that exception but retained the
wrong public event-envelope contract. It has been superseded: both handwritten
`retrieve_stream` overrides are removed, exposing the generated typed streams
and their direct payload models, matching the intended October GA behavior.
The November operation retains Work IQ authorization forwarding and terminal
event handling. Legacy parser helpers remain importable but are not used by
the public operation.

Unit tests exercise the real generated operation through a mocked pipeline,
including payload variants, terminal stopping, callbacks, authorization headers,
and response closure. Both existing SSE recordings replay with direct typed
payload assertions, and the corresponding samples use those payloads directly.
This is SDK-owned compatibility, not a service-spec change or emitter defect.

## October GA compatibility carry-forward

The Python comparison baseline is PR #49365 at
`a4610424b2d91b6e5f13e78dbcc8b6fcac57ac5f`, an intended GA change rather than
evidence of a published release. The preview retains its November default and
pinned specification. SDK-owned carry-forward includes explicit October API
selection, enum aliases, buffered retry and task ownership, canonical batch
storage, non-destructive paging metadata, semantic encoding, conditional
deletes, field-helper options, dictionary batch inputs, error-map forwarding,
buffered client options and schema-client ownership, and handwritten input
annotations. Vector sequences are normalized to a list of polymorphic models
in the shared request builder, as in the GA baseline.

GA's
`indexes.types.KnowledgeBaseModel = Union[KnowledgeBaseAzureOpenAIModel]`
simplifies to a callable TypedDict, whereas November's three-member union is
not callable. The legacy alias remains unchanged so existing
`KnowledgeBaseModel(...)` construction continues to work. A separate public
`indexes.types.KnowledgeBaseModelInput` union includes Azure OpenAI, Microsoft
Retriever 1, and OpenAI-compatible models. The `indexes.types.KnowledgeBase.models`
annotation remains `list[KnowledgeBaseModel]`. An earlier union-of-lists
annotation accepted pre-typed GA input lists but broke GA callers reading that
field as the narrow legacy list, and rejected appending new variants.
The same caller passed MyPy against exact merged October source
`c143a045142bf8e56416b6023f25230d301f56b3` and failed against that widened field.
A separate `indexes.types.KnowledgeBaseInput` exposes the same fields and
requiredness, with `models: list[KnowledgeBaseModelInput]`. Callers use this new
TypedDict for the full November union and construct concrete model TypedDicts
rather than calling the union. Both create and create-or-update accept either
TypedDict, synchronously and asynchronously; requests and response models are
unchanged.

The original generated union correctly represents the November spec. Separating
the input union from the callable legacy alias is an SDK-owned compatibility
choice, not a service-spec defect or an emitter bug. The package-owned
post-generation rewriter preserves both aliases, copies the generated definition
into the separate statically declared input TypedDict, and updates generated
submission annotations without changing the generation inputs.
Sync/async regressions exercise submitting the legacy constructor and all three
variants; regeneration tests verify the separate field contracts, requiredness,
and idempotence. Caller typing checks include GA list read-back and mutable
November input lists.
Keep this compatibility customization until unmodified generated output
preserves both GA construction and complete November input typing.
The new public input type and alias remain subject to Python API review;
neither the similar RP .NET customization nor local validation constitutes
architect approval.
The customization MCP attempt applied no patches because its global dependency
build failed on `azure-search-nspkg`; the approved fallback uses this existing
rewriter and the package venv, not manual edits to generated files.
The checked-in static caller regression is included explicitly when running
MyPy from the package directory:

```powershell
python -m mypy --config-file mypy.ini azure tests\test_generator_workarounds.py
```

For this typing revision, API snapshots were parsed from an isolated extraction
of the freshly built wheel after byte-comparing its 77 packaged source files
with the workspace. The parser API bypassed the wrapper's cached same-version
installation; the standard markdown exporter and metadata extractor produced
`api.md` and `api.metadata.yml`. Operation and wrapper runtime ASTs remain
unchanged after excluding annotations and docstrings.

The four additional offline completed File-poller continuation cases were
removed at the user's request while the azure-core/generated-response mismatch
remains unresolved. Original typed-poller tests and failed-operation monitor
tests remain. Removing this coverage does not fix or establish support for
completed-token resumption.

The final customized preview was compared with the exact GA source revision
above using the same APIView parser (0.3.31) for both locally built wheels and
the repository's APIView-to-code-report converter and breaking-change tracker.
The initial tracker run flagged four enum aliases and seventeen scoring-model
properties. The enum findings exposed genuine GA regressions: aliases assigned
after enum creation supported attribute access but were absent from
`__members__`, causing enum-name lookup to fail. The customization now follows
GA's runtime enum declaration with `CaseInsensitiveEnumMeta`, registering
`GPT_5_MINI`, `GPT_5_NANO`, `GPT_5_4_MINI`, and `GPT_5_4_NANO` inside the class.
This restores attribute identity, registered and case-insensitive name lookup,
and canonical names while retaining every generated November member.
Regression tests cover those contracts and preservation of November values.

The refreshed wheel and API snapshot no longer produce the four enum findings.
The seventeen remaining scoring-property findings are false positives: the
properties are inherited from generated and compatibility bases and remain
usable in runtime and MyPy caller probes. No breaking-check suppressions were
added to the repository.

Runtime comparison covered 623 SDK exports across twelve public modules,
including inherited members, parameter shapes, and registered enum names and
values. After the enum repair, these checks find zero confirmed GA-to-preview
API breaks across the checked surface. They do not prove all service behavior
or possible typing changes compatible. The MCP detector separately returned
clean, but did not identify an explicit comparison baseline; the exact-ref
comparison above is the basis for this compatibility conclusion.

Source changes were requested through `azsdk_customized_code_update` with
`editScope="CustomCode"`. Some timed-out requests applied partial edits.
Other requests applied patches but returned `BuildAfterPatchesFailed` during
global Python dependency setup, independently of local package-venv results.
Regression-test authoring was handled separately after the tool classified it
outside its automated customization phase. Local wheel builds and comparative
API snapshots succeeded independently of the MCP build verdict.

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

Follow the repository [testing guide](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/tests.md) and the
package's [environment template](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/.github/skills/azure-search-documents/scripts/Set-LiveTestEnvironment.sample.ps1).
Before recording, confirm:

- A dedicated disposable Search service supports the November preview, semantic
  ranking, knowledge bases/sources, and File ingestion. Service-wide cleanup
  has been removed from the live-test preparer; tests use their own resource
  names. Still use only an explicitly authorized test service, not production.
- `SEARCH_SERVICE_ENDPOINT` and `SEARCH_SERVICE_NAME` identify that service.
  The signed-in principal needs Search Service Contributor and Search Index Data
  Contributor, as in the [test-resource template](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/test-resources.bicep).
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
recordings before updating the package's asset tag. The authorized PPE recordings
have been refreshed and published to `Azure/azure-sdk-assets`, and `assets.json`
references the published tag. Four new model-backed live cases are deferred;
all 470 remaining unit and playback tests pass without exclusions.
