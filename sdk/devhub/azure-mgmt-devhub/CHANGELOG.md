# Release History

## 1.0.0b2 (2026-06-02)

### Features Added

  - Client `DevHubMgmtClient` added parameter `cloud_setting` in method `__init__`
  - Client `DevHubMgmtClient` added method `get_adoo_auth_info`
  - Client `DevHubMgmtClient` added method `send_request`
  - Client `DevHubMgmtClient` added operation group `iac_profiles`
  - Client `DevHubMgmtClient` added operation group `adoo_auth`
  - Client `DevHubMgmtClient` added operation group `template`
  - Client `DevHubMgmtClient` added operation group `versioned_template`
  - Enum `ManifestType` added member `KUSTOMIZE`
  - Added model `ADOOAuth`
  - Added model `ADOOAuthCallRequest`
  - Added model `ADOOAuthInfoResponse`
  - Added model `ADOOAuthResponse`
  - Added model `ADOProviderProfile`
  - Added model `ADORepository`
  - Added model `AzurePipelineProfile`
  - Added model `Build`
  - Added model `ExportTemplateRequest`
  - Added model `GenerateVersionedTemplateResponse`
  - Added model `GitHubProviderProfile`
  - Added model `GitHubRepository`
  - Added model `GitHubWorkflowProfile`
  - Added model `IacGitHubProfile`
  - Added model `IacProfile`
  - Added model `IacProfileProperties`
  - Added model `IacTemplateDetails`
  - Added model `IacTemplateProperties`
  - Added model `OidcCredentials`
  - Added model `Parameter`
  - Added model `ParameterDefault`
  - Added enum `ParameterKind`
  - Added enum `ParameterType`
  - Added model `PrLinkResponse`
  - Added model `PullRequest`
  - Added enum `QuickStartTemplateType`
  - Added enum `RepositoryProviderType`
  - Added model `ScaleProperty`
  - Added model `ScaleTemplateRequest`
  - Added model `StageProperties`
  - Added model `Template`
  - Added model `TemplateProperties`
  - Added model `TemplateReference`
  - Added enum `TemplateType`
  - Added model `TemplateWorkflowProfile`
  - Added model `TerraformProfile`
  - Added model `VersionedTemplate`
  - Added model `VersionedTemplateProperties`
  - Added operation group `ADOOAuthOperations`
  - Added operation group `IacProfilesOperations`
  - Added operation group `TemplateOperations`
  - Added operation group `VersionedTemplateOperations`

### Breaking Changes

  - This version introduces new hybrid models which have dual dictionary and model nature. Please follow https://aka.ms/azsdk/python/migrate/hybrid-models for migration.
  - For the method breakings, please refer to https://aka.ms/azsdk/python/migrate/operations for migration.
  - Model `GitHubOAuthResponse` moved instance variable `username` under property `properties` whose type is `GitHubOAuthProperties`
  - Method `DevHubMgmtClient.git_hub_o_auth_callback` changed its parameter `code`/`state` from `positional_or_keyword` to `keyword_only`
  - Method `WorkflowOperations.list_by_resource_group` changed its parameter `managed_cluster_resource` from `positional_or_keyword` to `keyword_only`

### Other Changes
  - Renamed operation group `DevHubMgmtClientOperationsMixin` to `_DevHubMgmtClientOperationsMixin`

## 1.0.0b1 (2023-05-20)

* Initial Release
