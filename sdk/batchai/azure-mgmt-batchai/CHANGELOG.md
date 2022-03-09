# Release History

## 7.0.0b1 (2021-06-02)

This is beta preview version.
For detailed changelog please refer to equivalent stable version 2.0.0(https://pypi.org/project/azure-mgmt-batchai/2.0.0/)

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
  - For a complete set of supported options, see the [parameters accept in Request documentation of azure-core](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/CLIENT_LIBRARY_DEVELOPER.md#available-policies)

**General new features**

- Type annotations support using `typing`. SDKs are mypy ready.
- This client has now stable and official support for async. Check the `aio` namespace of your package to find the async client.
- This client now support natively tracing library like OpenCensus or OpenTelemetry. See this [tracing quickstart](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/core/azure-core-tracing-opentelemetry) for an overview.

## 2.0.0 (2018-06-07)

**Breaking changes**

This version uses 2018-05-01 BatchAI API specification which introduced the following braking changes:

- Clusters, FileServers must be created under a workspace;
- Jobs must be created under an experiment;
- Clusters, FileServers and Jobs do not accept location during creation and belong to the same location as the parent
  workspace;
- Clusters, FileServers and Jobs do not support tags;
- BatchAIManagementClient.usage renamed to BatchAIManagementClient.usages;
- Job priority changed a type from int to an enum;
- File.is_directory is replaced with File.file_type;
- Job.priority and JobCreateParameters.priority is replaced with scheduling_priority;
- Removed unsupported MountSettings.file_server_type attribute;
- OutputDirectory.type unsupported attribute removed;
- OutputDirectory.create_new attributes removed, BatchAI will always create output directories if they not exist;
- SetupTask.run_elevated attribute removed, the setup task is always executed under root.

**Features**

- Added support to workspaces to group Clusters, FileServers and Experiments and remove limit on number of allocated
  resources;
- Added support for experiment to group jobs and remove limit on number of jobs;
- Added support for configuring /dev/shm for jobs which use docker containers;
- Added first class support for generic MPI jobs;
- Added first class support for Horovod jobs.

## 1.0.1 (2018-04-16)

**Bugfixes**

- Fix some invalid models in Python 3
- Compatibility of the sdist with wheel 0.31.0

## 1.0.0 (2018-03-19)

**General Breaking changes**

This version uses a next-generation code generator that *might* introduce breaking changes.

- Model signatures now use only keyword-argument syntax. All positional arguments must be re-written as keyword-arguments.
  To keep auto-completion in most cases, models are now generated for Python 2 and Python 3. Python 3 uses the "*" syntax for keyword-only arguments.
- Enum types now use the "str" mixin (class AzureEnum(str, Enum)) to improve the behavior when unrecognized enum values are encountered.
  While this is not a breaking change, the distinctions are important, and are documented here:
  https://docs.python.org/3/library/enum.html#others
  At a glance:

  - "is" should not be used at all.
  - "format" will return the string value, where "%s" string formatting will return `NameOfEnum.stringvalue`. Format syntax should be prefered.

- New Long Running Operation:

  - Return type changes from `msrestazure.azure_operation.AzureOperationPoller` to `msrest.polling.LROPoller`. External API is the same.
  - Return type is now **always** a `msrest.polling.LROPoller`, regardless of the optional parameters used.
  - The behavior has changed when using `raw=True`. Instead of returning the initial call result as `ClientRawResponse`,
    without polling, now this returns an LROPoller. After polling, the final resource will be returned as a `ClientRawResponse`.
  - New `polling` parameter. The default behavior is `Polling=True` which will poll using ARM algorithm. When `Polling=False`,
    the response of the initial call will be returned without polling.
  - `polling` parameter accepts instances of subclasses of `msrest.polling.PollingMethod`.
  - `add_done_callback` will no longer raise if called after polling is finished, but will instead execute the callback right away.

**Features**

- added support for job level mounting
- added support for environment variables with secret values
- added support for performance counters reporting in Azure Application Insights
- added support for custom images
- added support for pyTorch deep learning framework
- added API for usage and limits reporting
- added API for listing job files in subdirectories
- now user can choose caching type during NFS creation
- get cluster now reports a path segment generated for storing start task output logs
- get job now reports a path segment generated for job's output directories
- renamed EnvironmentSetting to EnvironmentVariable

## 0.2.0 (2017-10-05)

* credentials_info property got renamed to credentials.
* removed unused class FileServerStatus and Code enum
* renamed enums for CachingType and VmPriority
* removed 'statuses' attribute on FileServer

## 0.1.0 (2017-10-03)

* Initial Release
