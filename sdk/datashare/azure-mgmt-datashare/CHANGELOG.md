# Release History

## 1.0.0b1 (2020-12-04)

This is beta preview version.

This version uses a next-generation code generator that introduces important breaking changes, but also important new features (like unified authentication and async programming).

**General breaking changes**

- Credential system has been completly revamped:

  - `azure.common.credentials` or `msrestazure.azure_active_directory` instances are no longer supported, use the `azure-identity` classes instead: https://pypi.org/project/azure-identity/
  - `credentials` parameter has been renamed `credential`

- The `config` attribute no longer exists on a client, configuration should be passed as kwarg. Example: `MyClient(credential, subscription_id, enable_logging=True)`. For a complete set of
  supported options, see the [parameters accept in init documentation of azure-core](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/core/azure-core/CLIENT_LIBRARY_DEVELOPER.md#available-policies)
- You can't import a `version` module anymore, use `__version__` instead
- Operations that used to return a `msrest.polling.LROPoller` now returns a `azure.core.polling.LROPoller` and are prefixed with `begin_`.
- Exceptions tree have been simplified and most exceptions are now `azure.core.exceptions.HttpResponseError` (`CloudError` has been removed).
- Most of the operation kwarg have changed. Some of the most noticeable:

  - `raw` has been removed. Equivalent feature can be found using `cls`, a callback that will give access to internal HTTP response for advanced user
  - For a complete set of
  supported options, see the [parameters accept in Request documentation of azure-core](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/core/azure-core/CLIENT_LIBRARY_DEVELOPER.md#available-policies)

**General new features**

- Type annotations support using `typing`. SDKs are mypy ready.
- This client has now stable and official support for async. Check the `aio` namespace of your package to find the async client.
- This client now support natively tracing library like OpenCensus or OpenTelemetry. See this [tracing quickstart](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/core/azure-core-tracing-opentelemetry) for an overview.

## 0.2.0 (2020-05-14)

**Features**

  - Model ShareSubscriptionSynchronization has a new parameter synchronization_mode
  - Model ProviderShareSubscription has a new parameter consumer_name
  - Model ProviderShareSubscription has a new parameter consumer_email
  - Model ProviderShareSubscription has a new parameter consumer_tenant_name
  - Model ProviderShareSubscription has a new parameter provider_email
  - Model ProviderShareSubscription has a new parameter provider_name
  - Model ADLSGen2FileSystemDataSetMapping has a new parameter provisioning_state
  - Model SqlDWTableDataSetMapping has a new parameter provisioning_state
  - Model Invitation has a new parameter user_name
  - Model Invitation has a new parameter user_email
  - Model Account has a new parameter user_name
  - Model Account has a new parameter user_email
  - Model ShareSubscription has a new parameter provider_tenant_name
  - Model ShareSubscription has a new parameter user_name
  - Model ShareSubscription has a new parameter provider_email
  - Model ShareSubscription has a new parameter user_email
  - Model ShareSubscription has a new parameter provider_name
  - Model ADLSGen2FolderDataSetMapping has a new parameter provisioning_state
  - Model ConsumerSourceDataSet has a new parameter data_set_location
  - Model ConsumerSourceDataSet has a new parameter data_set_path
  - Model BlobFolderDataSetMapping has a new parameter provisioning_state
  - Model ScheduledTrigger has a new parameter user_name
  - Model Share has a new parameter user_name
  - Model Share has a new parameter user_email
  - Model BlobContainerDataSetMapping has a new parameter provisioning_state
  - Model ScheduledSynchronizationSetting has a new parameter user_name
  - Model ShareSynchronization has a new parameter consumer_name
  - Model ShareSynchronization has a new parameter consumer_email
  - Model ShareSynchronization has a new parameter consumer_tenant_name
  - Model ShareSynchronization has a new parameter synchronization_mode
  - Model ADLSGen2FileDataSetMapping has a new parameter provisioning_state
  - Model SqlDBTableDataSetMapping has a new parameter provisioning_state
  - Model ConsumerInvitation has a new parameter provider_tenant_name
  - Model ConsumerInvitation has a new parameter user_name
  - Model ConsumerInvitation has a new parameter provider_email
  - Model ConsumerInvitation has a new parameter user_email
  - Model ConsumerInvitation has a new parameter provider_name
  - Model BlobDataSetMapping has a new parameter provisioning_state

**Breaking changes**

  - Parameter data_set_id of model ADLSGen2FileSystemDataSetMapping is now required
  - Parameter data_set_id of model SqlDWTableDataSetMapping is now required
  - Parameter data_set_id of model ADLSGen2FolderDataSetMapping is now required
  - Parameter data_warehouse_name of model SqlDWTableDataSet is now required
  - Parameter table_name of model SqlDWTableDataSet is now required
  - Parameter sql_server_resource_id of model SqlDWTableDataSet is now required
  - Parameter data_set_id of model BlobFolderDataSetMapping is now required
  - Parameter data_set_id of model BlobContainerDataSetMapping is now required
  - Parameter data_set_id of model ADLSGen2FileDataSetMapping is now required
  - Parameter data_set_id of model SqlDBTableDataSetMapping is now required
  - Parameter database_name of model SqlDBTableDataSet is now required
  - Parameter table_name of model SqlDBTableDataSet is now required
  - Parameter sql_server_resource_id of model SqlDBTableDataSet is now required
  - Parameter data_set_id of model BlobDataSetMapping is now required
  - Operation ShareSubscriptionsOperations.create has a new signature
  - Model ProviderShareSubscription no longer has parameter shared_by
  - Model ProviderShareSubscription no longer has parameter company
  - Model ProviderShareSubscription no longer has parameter created_by
  - Model SqlDWTableDataSetMapping has a new required parameter schema_name
  - Model Invitation no longer has parameter sender
  - Model Account no longer has parameter created_by
  - Model ShareSubscription no longer has parameter share_sender
  - Model ShareSubscription no longer has parameter share_sender_company_name
  - Model ShareSubscription no longer has parameter created_by
  - Model ShareSubscription has a new required parameter source_share_location
  - Model SqlDWTableDataSet has a new required parameter schema_name
  - Model ScheduledTrigger no longer has parameter created_by
  - Model Share no longer has parameter created_by
  - Model ScheduledSynchronizationSetting no longer has parameter created_by
  - Model ShareSynchronization no longer has parameter company
  - Model ShareSynchronization no longer has parameter recipient
  - Model SqlDBTableDataSetMapping has a new required parameter schema_name
  - Model ConsumerInvitation no longer has parameter sender
  - Model ConsumerInvitation no longer has parameter sender_company_name
  - Model SqlDBTableDataSet has a new required parameter schema_name

## 0.1.0rc1 (2019-09-29)

  - Initial Release
