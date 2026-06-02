# Release History

## 1.0.0b2 (2026-06-02)

### Features Added

  - Enum `ManifestType` added member `KUSTOMIZE`
  - Added model `IacGitHubProfile`
  - Added model `TerraformProfile`

### Breaking Changes

  - For the method breakings, please refer to https://aka.ms/azsdk/python/migrate/operations for migration.
  - Method `DevHubMgmtClient.git_hub_o_auth_callback` changed its parameter `code`/`state` from `positional_or_keyword` to `keyword_only`
  - Method `WorkflowOperations.list_by_resource_group` changed its parameter `managed_cluster_resource` from `positional_or_keyword` to `keyword_only`

### Other Changes

  - Deleted model `ADOOAuthListResponse` which actually were not used by SDK users

## 1.0.0b1 (2023-05-20)

* Initial Release
