# 2026-11-01-preview generation

Generation inputs are `Azure/azure-rest-api-specs` commit
`2c0ca3a8b788bc866d2312b72bc05b49b048973d`,
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
