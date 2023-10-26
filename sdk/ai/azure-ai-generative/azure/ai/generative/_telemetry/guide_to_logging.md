## Configuring Client-side Logging for Azure Gen AI SDK


This document explains the logging system for the Azure Generative AI SDK for developers in this repository who want to understand how the logging system works and how to configure it for their own methods and modules.



### When do we log?

Logging will be disabled if
 - Calls are not being made from a Jupyter notebook. As an Azure SDK, azure-ai-generative must comply with the Azure SDK for Python's guidelines around logging. The guidelines limit logging to interactive scenarios only, meaning that client-side logging can only be enabled when a user is running SDK code from a Jupyter notebook.
 - An incorrect user agent is passed. This prevents calls from other Azure SDKs being inadvertently logged under the azure-ai-generative namespace.
 - The subscription ID is in the `test_subscriptions` list of internal developer subscription IDs declared in [`logging_handler.py`](logging_handler.py). 
 - An exception is triggered while trying to set up and return the logging handler. Logging should never interfere with the execution of the code, so if an exception is triggered, we simply move on.

Logging can also be explicitly disabled in any scenario by passing `enable_telemetry=False` when configuring the `AIClient`.

In all of these cases, a `logging.NullHandler` is returned from `get_appinsights_log_handler`.

### What do we log?

The basic Kusto query for azure-generative-ai logs can be found [here](https://ms.portal.azure.com/#view/Microsoft_OperationsManagementSuite_Workspace/Logs.ReactView/resourceId/%2Fsubscriptions%2F589c7ae9-223e-45e3-a191-98433e0821a9%2FresourceGroups%2Fvienna-sdk%2Fproviders%2Fmicrosoft.insights%2Fcomponents%2Fvienna-sdk-unitedstates/source/LogsBlade.AnalyticsShareLinkToQuery/q/H4sIAAAAAAAAA42PwW7CQAxE73yF2VNyAIk7qYTa%252F4isjZWs1LUj29sUxMezuZD2grjO88x4XDGS7e6wTKQEnjKZY57howMcpTlN2gLy8IecgWVp2qen6oYjQaXqtiSfIFyip5%252Fk10%252FJ8zc5DWGrEHNNPDaxmEv%252BqrlsSdiOxUj7msTewr6DsHro16m2r%252BiyEujeC9isSiZFI%252FWjSplf%252Bv%252Bf9oyZtpnbC1HYMbFBwFtROmA6VJ0U62YKDxOKl7dSAQAA). This query can be adapted to filter for specific log levels, operations, and other properties.

If logging has been configured for a method, the following information will be logged:
 - The method name
 - The operation ID
 - The parent operation ID, if exists
 - The subscription ID
 - The resource group name
 - The project name
 - The team name
 - The activity name
 - The activity status (i.e. "Success" or "Failure")
 - The log level
 - The log message
 - The log timestamp
 - The location
 - The Python version

Note that this list isn't exhaustive, but it represents the most important information that is logged.

### How do we log?

1. Initialize the package logger with OpsLogger
```python
class OpsLogger:
    def __init__(self, name: str):
        self.package_logger: logging.Logger = logging.getLogger(GEN_AI_INTERNAL_LOGGER_NAMESPACE + name)
        self.package_logger.propagate = False
        self.module_logger = logging.getLogger(name)
        self.custom_dimensions = {}

    def update_info(self, data: dict) -> None:
        if "app_insights_handler" in data:
            self.package_logger.addHandler(data.pop("app_insights_handler"))
```

`OpsLogger` is responsible for encapsulating the logging setup for the package. It contains two loggers - `package_logger` and `module_logger`. Custom dimensions can be updated to include additional information.

To configure logging for an operations class, you'll need to instantiate an `OpsLogger` with the module name and then call `update_info()` with the `kwargs` dictionary. This will add the logging handler to the package logger.


```python
from azure.ai.generative._telemetry import OpsLogger

ops_logger = OpsLogger(__name__)

class ProjectOperations:
    """ProjectOperations.

    You should not instantiate this class directly. Instead, you should
    create an MLClient instance that instantiates it for you and
    attaches it as an attribute.
    """

    def __init__(
        self, resource_group_name: str, ml_client: MLClient, service_client: ServiceClient062023Preview, **kwargs: Any
    ):
        self._ml_client = ml_client
        self._service_client = service_client
        self._resource_group_name = resource_group_name
        ops_logger.update_info(kwargs)  # <--- Need this line in constructor
```

2. Configure logging for a method with the `distributed_trace` and `monitor_with_activity` decorators

*Distributed Tracing*
 - `@distributed_trace` is used to enable distributed tracing for a method. Its imported from azure.core.tracing.decorator and when applied to a method, it captures and propagates trace information, which is crucial for identifying performance bottlenecks and troubleshooting issues that span multiple services.

*Activity Monitoring*
 - `@monitor_with_activity` is used to track a method's activity with the provided logger and activity type. This records telemetry data specific to this method's execution including the duration and result status. It accepts parameters like a logger, an activity name, and an activity type (e.g., ActivityType.PUBLICAPI).

Add these decorators to the method you want to log.

```python
    @distributed_trace
    @monitor_with_activity(logger, "Project.BeginCreate", ActivityType.PUBLICAPI)
    def begin_create(
        self, *, project: Project, update_dependent_resources: bool = False, **kwargs
    ) -> LROPoller[Project]:
        """Create a new project. Returns the project if it already exists.

        :keyword project: Project definition.
        :paramtype project: ~azure.ai.generative.entities.project
        :keyword update_dependent_resources: Whether to update dependent resources
        :paramtype update_dependent_resources: boolean
        :return: An instance of LROPoller that returns a project.
        :rtype: ~azure.core.polling.LROPoller[~azure.ai.generative.entities.project]
        """
        return self._ml_client.workspaces.begin_create(
            workspace=project._workspace,
            update_dependent_resources=update_dependent_resources,
            cls=lambda workspace: Project._from_v2_workspace(workspace=workspace),
            **kwargs,
        )
```
