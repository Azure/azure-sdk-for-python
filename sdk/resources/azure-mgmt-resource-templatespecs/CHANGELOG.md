# Release History

## 1.0.0 (2026-09-28)

### Features Added

  - Client `TemplateSpecsClient` added parameter `cloud_setting` in method `__init__`
  - Model `TemplateSpecVersionsOperations` added method `get_built_in`
  - Model `TemplateSpecVersionsOperations` added method `list_built_ins`
  - Model `TemplateSpecsOperations` added method `get_built_in`
  - Model `TemplateSpecsOperations` added method `list_built_ins`

### Breaking Changes

  - Method `AzureResourceBase.from_dict` changed type of its parameter `key_extractors` from `Callable[[str, Dict[str, Any], Any], Any]` to `Callable[[str, dict[str, Any], Any], Any]`
  - Method `AzureResourceBase.as_dict` changed type of its parameter `key_transformer` from `Callable[[str, Dict[str, Any], Any], Any]` to `Callable[[str, dict[str, Any], Any], Any]`
  - Method `ErrorAdditionalInfo.from_dict` changed type of its parameter `key_extractors` from `Callable[[str, Dict[str, Any], Any], Any]` to `Callable[[str, dict[str, Any], Any], Any]`
  - Method `ErrorAdditionalInfo.as_dict` changed type of its parameter `key_transformer` from `Callable[[str, Dict[str, Any], Any], Any]` to `Callable[[str, dict[str, Any], Any], Any]`
  - Method `ErrorResponse.from_dict` changed type of its parameter `key_extractors` from `Callable[[str, Dict[str, Any], Any], Any]` to `Callable[[str, dict[str, Any], Any], Any]`
  - Method `ErrorResponse.as_dict` changed type of its parameter `key_transformer` from `Callable[[str, Dict[str, Any], Any], Any]` to `Callable[[str, dict[str, Any], Any], Any]`
  - Method `LinkedTemplateArtifact.from_dict` changed type of its parameter `key_extractors` from `Callable[[str, Dict[str, Any], Any], Any]` to `Callable[[str, dict[str, Any], Any], Any]`
  - Method `LinkedTemplateArtifact.as_dict` changed type of its parameter `key_transformer` from `Callable[[str, Dict[str, Any], Any], Any]` to `Callable[[str, dict[str, Any], Any], Any]`
  - Method `SystemData.from_dict` changed type of its parameter `key_extractors` from `Callable[[str, Dict[str, Any], Any], Any]` to `Callable[[str, dict[str, Any], Any], Any]`
  - Method `SystemData.as_dict` changed type of its parameter `key_transformer` from `Callable[[str, Dict[str, Any], Any], Any]` to `Callable[[str, dict[str, Any], Any], Any]`
  - Method `TemplateSpec.from_dict` changed type of its parameter `key_extractors` from `Callable[[str, Dict[str, Any], Any], Any]` to `Callable[[str, dict[str, Any], Any], Any]`
  - Method `TemplateSpec.as_dict` changed type of its parameter `key_transformer` from `Callable[[str, Dict[str, Any], Any], Any]` to `Callable[[str, dict[str, Any], Any], Any]`
  - Method `TemplateSpecUpdateModel.from_dict` changed type of its parameter `key_extractors` from `Callable[[str, Dict[str, Any], Any], Any]` to `Callable[[str, dict[str, Any], Any], Any]`
  - Method `TemplateSpecUpdateModel.as_dict` changed type of its parameter `key_transformer` from `Callable[[str, Dict[str, Any], Any], Any]` to `Callable[[str, dict[str, Any], Any], Any]`
  - Method `TemplateSpecVersion.from_dict` changed type of its parameter `key_extractors` from `Callable[[str, Dict[str, Any], Any], Any]` to `Callable[[str, dict[str, Any], Any], Any]`
  - Method `TemplateSpecVersion.as_dict` changed type of its parameter `key_transformer` from `Callable[[str, Dict[str, Any], Any], Any]` to `Callable[[str, dict[str, Any], Any], Any]`
  - Method `TemplateSpecVersionInfo.from_dict` changed type of its parameter `key_extractors` from `Callable[[str, Dict[str, Any], Any], Any]` to `Callable[[str, dict[str, Any], Any], Any]`
  - Method `TemplateSpecVersionInfo.as_dict` changed type of its parameter `key_transformer` from `Callable[[str, Dict[str, Any], Any], Any]` to `Callable[[str, dict[str, Any], Any], Any]`
  - Method `TemplateSpecVersionUpdateModel.from_dict` changed type of its parameter `key_extractors` from `Callable[[str, Dict[str, Any], Any], Any]` to `Callable[[str, dict[str, Any], Any], Any]`
  - Method `TemplateSpecVersionUpdateModel.as_dict` changed type of its parameter `key_transformer` from `Callable[[str, Dict[str, Any], Any], Any]` to `Callable[[str, dict[str, Any], Any], Any]`
  - Method `TemplateSpecVersionsListResult.from_dict` changed type of its parameter `key_extractors` from `Callable[[str, Dict[str, Any], Any], Any]` to `Callable[[str, dict[str, Any], Any], Any]`
  - Method `TemplateSpecVersionsListResult.as_dict` changed type of its parameter `key_transformer` from `Callable[[str, Dict[str, Any], Any], Any]` to `Callable[[str, dict[str, Any], Any], Any]`
  - Method `TemplateSpecsError.from_dict` changed type of its parameter `key_extractors` from `Callable[[str, Dict[str, Any], Any], Any]` to `Callable[[str, dict[str, Any], Any], Any]`
  - Method `TemplateSpecsError.as_dict` changed type of its parameter `key_transformer` from `Callable[[str, Dict[str, Any], Any], Any]` to `Callable[[str, dict[str, Any], Any], Any]`
  - Method `TemplateSpecsListResult.from_dict` changed type of its parameter `key_extractors` from `Callable[[str, Dict[str, Any], Any], Any]` to `Callable[[str, dict[str, Any], Any], Any]`
  - Method `TemplateSpecsListResult.as_dict` changed type of its parameter `key_transformer` from `Callable[[str, Dict[str, Any], Any], Any]` to `Callable[[str, dict[str, Any], Any], Any]`

## 1.0.0b1 (2025-06-05)

### Other Changes

  - Initial version
