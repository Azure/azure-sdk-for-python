# Release History

## 2.0.0b1 (2021-11-15)

**Features**

  - Model WebChatChannel has a new parameter location
  - Model WebChatChannel has a new parameter provisioning_state
  - Model WebChatChannel has a new parameter etag
  - Model ConnectionSetting has a new parameter zones
  - Model DirectLineSpeechChannel has a new parameter provisioning_state
  - Model DirectLineSpeechChannel has a new parameter etag
  - Model Resource has a new parameter zones
  - Model KikChannel has a new parameter etag
  - Model MsTeamsChannel has a new parameter location
  - Model MsTeamsChannel has a new parameter provisioning_state
  - Model MsTeamsChannel has a new parameter etag
  - Model BotChannel has a new parameter zones
  - Model DirectLineChannel has a new parameter location
  - Model DirectLineChannel has a new parameter provisioning_state
  - Model DirectLineChannel has a new parameter etag
  - Model DirectLineSite has a new parameter is_block_user_upload_enabled
  - Model ConnectionSettingProperties has a new parameter provisioning_state
  - Model LineChannel has a new parameter etag
  - Model Bot has a new parameter zones
  - Model AlexaChannel has a new parameter provisioning_state
  - Model AlexaChannel has a new parameter etag
  - Model SlackChannel has a new parameter location
  - Model SlackChannel has a new parameter etag
  - Model SlackChannelProperties has a new parameter scopes
  - Model SkypeChannel has a new parameter etag
  - Model BotProperties has a new parameter manifest_url
  - Model BotProperties has a new parameter all_settings
  - Model BotProperties has a new parameter app_password_hint
  - Model BotProperties has a new parameter private_endpoint_connections
  - Model BotProperties has a new parameter is_streaming_supported
  - Model BotProperties has a new parameter disable_local_auth
  - Model BotProperties has a new parameter provisioning_state
  - Model BotProperties has a new parameter publishing_credentials
  - Model BotProperties has a new parameter msa_app_type
  - Model BotProperties has a new parameter msa_app_msi_resource_id
  - Model BotProperties has a new parameter migration_token
  - Model BotProperties has a new parameter msa_app_tenant_id
  - Model BotProperties has a new parameter is_developer_app_insights_api_key_set
  - Model BotProperties has a new parameter parameters
  - Model BotProperties has a new parameter cmek_encryption_status
  - Model BotProperties has a new parameter open_with_hint
  - Model SkypeChannelProperties has a new parameter incoming_call_route
  - Model FacebookChannel has a new parameter location
  - Model FacebookChannel has a new parameter provisioning_state
  - Model FacebookChannel has a new parameter etag
  - Model MsTeamsChannelProperties has a new parameter accepted_terms
  - Model MsTeamsChannelProperties has a new parameter incoming_call_route
  - Model MsTeamsChannelProperties has a new parameter deployment_environment
  - Model ServiceProviderParameter has a new parameter metadata
  - Model TelegramChannel has a new parameter provisioning_state
  - Model TelegramChannel has a new parameter etag
  - Model EmailChannel has a new parameter provisioning_state
  - Model EmailChannel has a new parameter etag
  - Model SmsChannel has a new parameter etag
  - Model Channel has a new parameter etag
  - Model DirectLineChannelProperties has a new parameter direct_line_embed_code
  - Added operation group PrivateEndpointConnectionsOperations
  - Added operation group PrivateLinkResourcesOperations
  - Added operation group OperationResultsOperations

**Breaking changes**

  - Model DirectLineSpeechChannelProperties no longer has parameter cognitive_services_subscription_id
  - Model DirectLineSpeechChannelProperties has a new required parameter cognitive_service_subscription_key
  - Model DirectLineSpeechChannelProperties has a new required parameter cognitive_service_region
  - Model WebChatSite no longer has parameter enable_preview
  - Model WebChatSite has a new required parameter is_webchat_preview_enabled

## 1.0.0 (2021-05-20)

**Features**

  - Model BotProperties has a new parameter schema_transformation_version
  - Model BotProperties has a new parameter cmek_key_vault_url
  - Model BotProperties has a new parameter is_isolated
  - Model BotProperties has a new parameter is_cmek_enabled
  - Added operation group HostSettingsOperations

## 1.0.0b1 (2020-11-20)

This is beta preview version.

This version uses a next-generation code generator that introduces important breaking changes, but also important new features (like unified authentication and async programming).

**General breaking changes**

- Credential system has been completly revamped:

  - `azure.common.credentials` or `msrestazure.azure_active_directory` instances are no longer supported, use the `azure-identity` classes instead: https://pypi.org/project/azure-identity/
  - `credentials` parameter has been renamed `credential`

- The `config` attribute no longer exists on a client, configuration should be passed as kwarg. Example: `MyClient(credential, subscription_id, enable_logging=True)`. For a complete set of
  supported options, see the [parameters accept in init documentation of azure-core](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/CLIENT_LIBRARY_DEVELOPER.md#available-policies)
- You can't import a `version` module anymore, use `__version__` instead
- Operations that used to return a `msrest.polling.LROPoller` now returns a `azure.core.polling.LROPoller` and are prefixed with `begin_`.
- Exceptions tree have been simplified and most exceptions are now `azure.core.exceptions.HttpResponseError` (`CloudError` has been removed).
- Most of the operation kwarg have changed. Some of the most noticeable:

  - `raw` has been removed. Equivalent feature can be found using `cls`, a callback that will give access to internal HTTP response for advanced user
  - For a complete set of
  supported options, see the [parameters accept in Request documentation of azure-core](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/CLIENT_LIBRARY_DEVELOPER.md#available-policies)

**General new features**

- Type annotations support using `typing`. SDKs are mypy ready.
- This client has now stable and official support for async. Check the `aio` namespace of your package to find the async client.
- This client now support natively tracing library like OpenCensus or OpenTelemetry. See this [tracing quickstart](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/core/azure-core-tracing-opentelemetry) for an overview.

## 0.2.0 (2019-05-21)

**Features**

  - Model DirectLineSite has a new parameter is_secure_site_enabled
  - Model DirectLineSite has a new parameter trusted_origins
  - Added operation group EnterpriseChannelsOperations

## 0.1.0 (2018-08-07)

  - Initial Release
