## Configuring Client-side Logging for Azure Machine Learning SDK v2


This document explains the logging system for the Azure ML SDK for developers in this repository who want to understand how the logging system works and how to configure it for their own methods and modules.

### When do we log?

Logging will be disabled if
 - Calls are not being made from a Jupyter notebook. As an Azure SDK, azure-ai-ml must comply with the Azure SDK for Python's guidelines around logging. The guidelines limit logging to interactive scenarios only, meaning that client-side logging can only be enabled when a user is running SDK code from a Jupyter notebook.
 - An incorrect user agent is passed. This prevents calls from other Azure SDKs being inadvertently logged under the azure-ai-ml namespace. Valid user agents for azure-ai-ml following this pattern: "azure-ai-ml/< version >"
 - The subscription ID is in the `test_subscriptions` list of internal developer subscription IDs declared in [`logging_handler.py`](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ml/azure-ai-ml/azure/ai/ml/_telemetry/logging_handler.py). Those subscriptions can be used to prevent logging of test commands.
 - An exception is triggered while trying to set up and return the logging handler. Logging should never interfere with the execution of the code, so if an exception is triggered, we simply move on.

Logging can also be explicitly disabled in any scenario by setting `MLClient`'s `enable_telemetry` parameter equal to `False`.

In all of these cases, a `logging.NullHandler` is returned from `get_appinsights_log_handler`.

### What do we log?

The logging structure depends on access to the MLClient, which is passed to the operations class in the constructor. Methods not connected to the MLClient will not have access to that information and thus, cannot be tracked via appinsights logging.

If logging has been configured for a method, the following information will be logged:
 - The method name
 - The operation ID
 - The parent operation ID, if exists
 - The subscription ID, if available
 - The resource group name, if available
 - The activity name
 - The activity status (i.e. "Success" or "Failure")
 - The log level
 - The log message
 - The log timestamp
 - The location
 - The Python version

Note that this list isn't exhaustive, but it represents the most important information that is logged.

### How do we log?

1. Initialize the package logger with ActivityLogger

`OpsLogger` is responsible for encapsulating the logging setup for the package. It contains two loggers - `package_logger` and `module_logger`. Custom dimensions can be updated to include additional information.

To configure logging for a class, you'll need to instantiate an `OpsLogger` with the module name and then call `update_info()`. This will add the logging handler to the package logger.


```python
from azure.ai.ml._utils._logger_utils import OpsLogger


ops_logger = OpsLogger(__name__)
module_logger = ops_logger.module_logger

class DataOperations(_ScopeDependentOperations):
    def __init__(
        self,
        operation_scope: OperationScope,
        operation_config: OperationConfig,
        service_client: Union[ServiceClient042023_preview, ServiceClient102021Dataplane],
        service_client_012024_preview: ServiceClient012024_preview,
        datastore_operations: DatastoreOperations,
        **kwargs: Any,
    ):
        super(DataOperations, self).__init__(operation_scope, operation_config)
        ops_logger.update_info(kwargs) # <--- Need this line in constructor
        ...
```

1. Configure logging for a method with the `distributed_trace` and `monitor_with_activity` decorators

*Distributed Tracing*
 - `@distributed_trace` is used to enable distributed tracing for a method. Its imported from azure.core.tracing.decorator and when applied to a method, it captures and propagates trace information, which is crucial for identifying performance bottlenecks and troubleshooting issues that span multiple services.

*Activity Monitoring*
 - `@monitor_with_activity` is used to track a method's activity with the provided logger and activity type. This records telemetry data specific to this method's execution including the duration and result status. It accepts parameters like a logger, an activity name, and an activity type (e.g., ActivityType.PUBLICAPI).

Add these decorators to the method you want to log.

```python
    @monitor_with_activity(ops_logger, "Workspace.Get_Keys", ActivityType.PUBLICAPI)
    @distributed_trace
    def get_keys(self, name: Optional[str] = None) -> Optional[WorkspaceKeys]:
        """Get WorkspaceKeys by workspace name.

        :param name: Name of the workspace.
        :type name: str
        :return: Keys of workspace dependent resources.
        :rtype: ~azure.ai.ml.entities.WorkspaceKeys

        .. admonition:: Example:

            .. literalinclude:: ../samples/ml_samples_workspace.py
                :start-after: [START workspace_get_keys]
                :end-before: [END workspace_get_keys]
                :language: python
                :dedent: 8
                :caption: Get the workspace keys for the workspace with the given name.
        """
        workspace_name = self._check_workspace_name(name)
        obj = self._operation.list_keys(self._resource_group_name, workspace_name)
        return WorkspaceKeys._from_rest_object(obj)
```

### Where do we log?
All logs are sent to Application Insights. [Here](https://ms.portal.azure.com#@72f988bf-86f1-41af-91ab-2d7cd011db47/blade/Microsoft_OperationsManagementSuite_Workspace/Logs.ReactView/resourceId/%2Fsubscriptions%2F589c7ae9-223e-45e3-a191-98433e0821a9%2FresourceGroups%2Fvienna-sdk%2Fproviders%2Fmicrosoft.insights%2Fcomponents%2Fvienna-sdk-unitedstates/source/LogsBlade.AnalyticsShareLinkToQuery/q/H4sIAAAAAAAAA42Rz0rEQAzG7z5F7KkFV%252FBuhUVBvPkGJU5DO7IzGZKMVfHhnarb1suy13zf98s%252FE3SkF18wjSQE5gOpYUhw1wIOXN%252BMDWDsN8ItRJ7qZomUuuJAUFQxnbyNUO2d%252BTdvH%252Fcc0oGM%252BmrtwGri41C7rMbhoXCjeo56nZWkK6RoDVy2UM0Zejcq3WdpPyvQngdYo5pf1IlPVixP%252Fcn81tr5fgMRUs7i6FE4p5OMo7MbZmsXMdCGw4kEz5hk8f0fYyk%252Fo5Qtz4akH%252Fsf6%252FcN60UdR0MfFSr8zEI79LtwmG%252BfhF%252FJ2fr6q%252BOvvwF2fSfoNQIAAA%253D%253D) is the query to see all azure-ai-ml logs.
