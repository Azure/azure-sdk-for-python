# Release History

## 1.0.0b2 (2026-05-28)

### Features Added

  - Model `GitHubOAuthResponse` added property `properties`
  - Enum `ManifestType` added member `KUSTOMIZE`
  - Added model `ADOOAuth`
  - Added model `ADOOAuthCallRequest`
  - Added model `ADOOAuthInfoResponse`
  - Added model `ADOOAuthResponse`
  - Added model `ADOProviderProfile`
  - Added model `ADORepository`
  - Added model `AzurePipelineProfile`
  - Added model `Build`
  - Added model `Deployment`
  - Added model `ExportTemplateRequest`
  - Added model `GenerateVersionedTemplateResponse`
  - Added model `GitHubOAuthProperties`
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
  - Added model `ADOOAuthOperations`
  - Added model `IacProfilesOperations`
  - Added model `TemplateOperations`
  - Added model `VersionedTemplateOperations`

### Breaking Changes

  - Deleted or renamed client `DevHubMgmtClient`
  - Model `GitHubOAuthResponse` deleted or renamed its instance variable `username`
  - Deleted or renamed model `DeploymentProperties`
  - Method `WorkflowOperations.list_by_resource_group` changed its parameter `managed_cluster_resource` from `positional_or_keyword` to `keyword_only`
  - Deleted or renamed model `DevHubMgmtClientOperationsMixin`

## 1.0.0b1 (2023-05-20)

* Initial Release
