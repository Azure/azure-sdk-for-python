# TypeSpec Migration SDK Output for azure-mgmt-automation

## Source

- **Spec PR**: https://github.com/Azure/azure-rest-api-specs/pull/40023
- **Pre-migration swagger source**: [specification/automation/resource-manager @ 0f953923](https://github.com/Azure/azure-rest-api-specs/tree/0f9539236cbea0cd9ca5dc0bde00d15a039fe22d/specification/automation/resource-manager)
- **TypeSpec source**: specification/automation/Automation.Management (PR head: 157bdb1c)

## Breaking Change Analysis

**All breaking changes are ACCEPTED — no mitigations required.**

| Category | Count | Action |
|----------|-------|--------|
| Multi-level flattened properties removal (Cat 11) | ~130 | ACCEPT |
| Parameters changed to keyword-only (Cat 9) | ~21 | ACCEPT |
| Unreferenced model removal (Cat 7) | 2 | ACCEPT |
| Pageable model removal (Cat 8) | 2 | ACCEPT |
| Common types upgrade (Cat 6) | 2 | ACCEPT |
| Python naming conflict resolution | 2 | ACCEPT |

### Category 11 — Multi-level Flattened Properties Removal

The majority of breaking changes. Models like `AutomationAccountCreateOrUpdateParameters`, `CertificateCreateOrUpdateParameters`, `ConnectionCreateOrUpdateParameters`, and ~30 other `*Parameters` models lost their flattened instance variables (e.g., `sku`, `description`, `content_link`) and gained a `properties` sub-object. This reflects TypeSpec's preservation of the actual REST API hierarchy.

### Category 9 — Parameters Changed to Keyword-Only

~21 operation methods changed `client_request_id` or `inlinecount` parameters from `positional_or_keyword` to `keyword_only`. This is the expected behavior from TypeSpec's operation design.

### Category 7 — Unreferenced Model Removal

- `RunbookCreateOrUpdateDraftParameters`
- `RunbookCreateOrUpdateDraftProperties`

### Category 8 — Pageable Model Removal

- `JobListResultV2`
- `SourceControlSyncJobStreamsListBySyncJob`

### Category 6 — Common Types Upgrade

- `ErrorResponse` restructured (lost `code`/`message`, replaced by `AutomationErrorResponse`)

### Python Naming Conflict Resolution

- `AgentRegistration.keys` renamed to `keys_property` (avoids conflict with `dict.keys()`)
- `KeyListResult.keys` removed (same conflict)
- `DscNodeUpdateParametersProperties.name` removed (moved into properties structure)

## Conclusion

No spec-side mitigations (`client.tsp`) are needed. All breaking changes fall under well-known acceptable migration patterns.
