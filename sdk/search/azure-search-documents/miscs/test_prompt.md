# Generated Surface Test Plan

Repository: `azure-sdk-for-python`
Package: `sdk/search/azure-search-documents`

## Existing Test Conventions

- Tests are split into pure unit/playback suites (no network) and live suites recorded through the Test Proxy.
- Most sync suites have async twins; keep coverage aligned.
- Generated code lives under `_generated/`; customization wrappers live beside it. Tests should import from the customization layer so missing surface area in the public layer is caught (if something is only in `_generated/`, we want the test to fail).
- When touching SearchIndex or SearchField parity, make sure changes land in both `azure/search/documents/indexes/models/_models.py` and `_index.py`; additions that only exist in `_generated` are bugs.
- Live tests use `SearchEnvVarPreparer`, `search_decorator`, and `@recorded_by_proxy` so they can be recorded and replayed.
- Live recordings must pass through the sanitizers configured in `tests/conftest.py`.

## Implementation Guidance

- Stay with the current layout: sync playback tests live beside other suites in `tests/`, and live suites keep their `_live` suffix in the same folder.
- Reuse existing fixtures/helpers (`search_service_preparer.py`, hotel JSON payloads) or extend them as needed instead of creating new directories.
- Ensure each live test uses the Test Proxy decorators so it can be recorded and replayed; sanitized recordings should accompany the tests.
- Keep generated resource-name seeds simple but specific (for example, `ks`/`kb` prefixes for knowledge sources/bases) so recordings stay readable without leaking details.

## Scenarios to Cover (focus on generated layer)

1. **Web Knowledge Source CRUD** – CRUD operations for a web knowledge source.
2. **Federated SharePoint Knowledge Source CRUD** – create, update, fetch, delete a SharePoint knowledge source.
3. **Knowledge Bases CRUD (KA → KB rename)** – end-to-end create/update/delete for Knowledge Bases using the renamed API surface.
4. **KR Reasoning Effort / QOL Configuration** – validate reasoning-effort and quality-of-life settings.
5. **ACLs Elevated Read** – exercise elevated-read ACL configuration paths and confirm request payloads.
6. **Purview Index Configuration** – create/update Purview index configuration and assert generated model fidelity.
7. **Content Understanding Skill  (CRUD with existing skills)** – CRUD skill definitions leveraging existing skills; confirm serialization/deserialization matches generated schema.
8. **Scoring Function Aggregation (product support)** – ensure index CRUD with scoring function aggregations (product) round-trips correctly.
9. **Facet Aggregations (avg, min, max, cardinality)** – validate facet response parsing across aggregation types.
10. **Indexed Knowledge Source Status Tracking** – poll status transitions for indexed knowledge sources and ensure generated status models deserialize correctly.
11. **Indexer Runtime** – start an indexer run, monitor runtime status, and verify generated response models.

## Expectations

- Sync and async suites should stay in lockstep.
- Exercise scenarios through the customization layer entry points so gaps between generated and public surfaces surface as failures; only dip into `_generated` code when explicitly validating autorest output.
- Record live runs where indicated, then commit sanitized recordings alongside the tests.
- Capture any special setup notes (service configuration, required data sources) alongside the tests or in this prompt so future re-recordings stay smooth.
