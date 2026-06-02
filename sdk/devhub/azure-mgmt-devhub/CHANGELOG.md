# Release History

## 1.0.0b2 (2026-06-02)

### Features Added

  - Client `DevHubMgmtClient` added method `send_request`
  - Enum `ManifestType` added member `KUSTOMIZE`
  - Added model `IacGitHubProfile`
  - Added model `TerraformProfile`

### Breaking Changes

  - Method `DevHubMgmtClient.git_hub_o_auth_callback` changed its parameter `code` from `positional_or_keyword` to `keyword_only`
  - Method `DevHubMgmtClient.git_hub_o_auth_callback` changed its parameter `state` from `positional_or_keyword` to `keyword_only`
  - Deleted or renamed model `ADOOAuthListResponse`
  - Method `WorkflowOperations.list_by_resource_group` changed its parameter `managed_cluster_resource` from `positional_or_keyword` to `keyword_only`

## 1.0.0b1 (2023-05-20)

* Initial Release
