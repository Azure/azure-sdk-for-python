# Discovery SDK - Cross-Language TODO Tracker

## ChatModelDeployment Update Test Removal

**Reason:** `ChatModelDeploymentProperties.modelFormat` and `ChatModelDeploymentProperties.modelName` have `visibility: ["read", "create"]` — they are NOT updatable via PATCH. The update test (`test_update_chat_model_deployment`) should be removed from all SDK languages.

| Language | Repo | Status |
|----------|------|--------|
| Python (public) | `azure-sdk-for-python` | ✅ Done — update test removed |
| Python (PR) | `azure-sdk-for-python-pr` | ⬜ Pending |
| Java | `azure-sdk-for-java` | ⬜ Check & remove if present |
| .NET | `azure-sdk-for-net` | ⬜ Check & remove if present |
| Go | `azure-sdk-for-go` | ⬜ Check & remove if present |
| JavaScript/TS | `azure-sdk-for-js` | ⬜ Check & remove if present |

## Notes
- The `begin_update` (PATCH) operation still exists in the generated SDK but should not be tested for chat model deployments since the only meaningful properties (`modelFormat`, `modelName`) are create/read only.
- Workspace update tests are fine — workspace properties like `keyVaultProperties` are updatable.
