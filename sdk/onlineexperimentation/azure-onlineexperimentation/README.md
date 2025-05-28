# Azure Online Experimentation client library for Python

This package contains Azure Online Experimentation client library for interacting with `Microsoft.OnlineExperimentation/workspaces` resources.

## Getting started

### Install the package

```bash
python -m pip install azure-onlineexperimentation
```

#### Prequisites

- Python 3.9 or later is required to use this package.
- You need an [Azure subscription][azure_sub] to use this package.
- An [Azure Online Experimentation workspace][azure_exp_workspace] resource in the Azure subscription.

### Create and authenticate the client

The Azure Online Experimentation client library initialization requires two parameters:

- The `endpoint` property value from the [`Microsoft.OnlineExperimentation/workspaces`][azure_exp_workspace] resource.
- A credential from `azure.identity`, the simplest approach is to use [DefaultAzureCredential][default_azure_credential] and `az login` to authenticate. See [Azure Identity client library for Python][azure_identity_credentials] for more details.

To construct a synchronous client:

<!-- SNIPPET:sample_initialize_client.initialize_client -->

```python
import os
from azure.identity import DefaultAzureCredential
from azure.onlineexperimentation import OnlineExperimentationClient

# Create a client with your Online Experimentation workspace endpoint and credentials
endpoint = os.environ["AZURE_ONLINEEXPERIMENTATION_ENDPOINT"]
client = OnlineExperimentationClient(endpoint, DefaultAzureCredential())
print(f"Client initialized with endpoint: {endpoint}")
```

<!-- END SNIPPET -->

To construct an asynchronous client, instead import `OnlineExperimentationClient` from `azure.onlineexperimentation.aio` and `DefaultAzureCredential` from `azure.identity.aio` namespaces:

<!-- SNIPPET:sample_initialize_async_client.initialize_async_client -->

```python
import os
from azure.identity.aio import DefaultAzureCredential
from azure.onlineexperimentation.aio import OnlineExperimentationClient

# Create a client with your Online Experimentation workspace endpoint and credentials
endpoint = os.environ["AZURE_ONLINEEXPERIMENTATION_ENDPOINT"]
client = OnlineExperimentationClient(endpoint, DefaultAzureCredential())
print(f"Client initialized with endpoint: {endpoint}")
```

<!-- END SNIPPET -->

## Key concepts

### Online Experimentation Workspace

[`Microsoft.OnlineExperimentation/workspaces`][az_exp_workspace] Azure resources work in conjunction with [Azure App Configuration][app_config] and [Azure Monitor][azure_monitor]. The Online Experimentation workspace handles management of metrics definitions and their continuous computation to monitor and evaluate experiment results.

### Experiment Metrics

Metrics are used to measure the impact of your online experiments. See the [samples][azure_exp_samples] for how to create and manage various types of experiment metrics.

## Troubleshooting

Errors can occur during initial requests and will provide information about how to resolve the error.

## Examples

This examples goes theough the experiment metric management lifecycle, to run the example:

- Set `AZURE_ONLINEEXPERIMENTATION_ENDPOINT` environment variable to the `endpoint` property value (URL) from a [`Microsoft.OnlineExperimentation/workspaces`][az_exp_workspace] resource.
- Enable `DefaultAzureCredential` by running `az login` or `Connect-AzAccount`, see [documentation][default_azure_credential] for details and troubleshooting.

<!-- SNIPPET:sample_experiment_metrics_management.experiment_metrics_management -->

```python
import os
import random
import json
from azure.identity import DefaultAzureCredential
from azure.onlineexperimentation import OnlineExperimentationClient
from azure.onlineexperimentation.models import (
    ExperimentMetric,
    LifecycleStage,
    DesiredDirection,
    UserRateMetricDefinition,
    ObservedEvent,
)
from azure.core.exceptions import HttpResponseError

# [Step 1] Initialize the SDK client
# The endpoint URL from the Microsoft.OnlineExperimentation/workspaces resource
endpoint = os.environ.get("AZURE_ONLINEEXPERIMENTATION_ENDPOINT", "<endpoint-not-set>")
credential = DefaultAzureCredential()

print(f"AZURE_ONLINEEXPERIMENTATION_ENDPOINT is {endpoint}")

client = OnlineExperimentationClient(endpoint=endpoint, credential=credential)

# [Step 2] Define the experiment metric
example_metric = ExperimentMetric(
    lifecycle=LifecycleStage.ACTIVE,
    display_name="% users with LLM interaction who made a high-value purchase",
    description="Percentage of users who received a response from the LLM and then made a purchase of $100 or more",
    categories=["Business"],
    desired_direction=DesiredDirection.INCREASE,
    definition=UserRateMetricDefinition(
        start_event=ObservedEvent(event_name="ResponseReceived"),
        end_event=ObservedEvent(event_name="Purchase", filter="Revenue > 100"),
    )
)

# [Optional][Step 2a] Validate the metric - checks for input errors without persisting anything
print("Checking if the experiment metric definition is valid...")
print(json.dumps(example_metric.as_dict(), indent=2))

try:
    validation_result = client.validate_metric(example_metric)
    
    print(f"Experiment metric definition valid: {validation_result.is_valid}.")
    for detail in validation_result.diagnostics or []:
        # Inspect details of why the metric definition was rejected as Invalid
        print(f"- {detail.code}: {detail.message}")
        
    # [Step 3] Create the experiment metric
    example_metric_id = f"sample_metric_id_{random.randint(10000, 20000)}"
    
    print(f"Creating the experiment metric {example_metric_id}...")
    # Using upsert to create the metric with If-None-Match header
    create_response = client.create_or_update_metric(
        experiment_metric_id=example_metric_id, 
        resource=example_metric,
        match_condition=None,  # This ensures If-None-Match: * header is sent
        etag=None
    )
    
    print(f"Experiment metric {create_response.id} created, etag: {create_response.e_tag}.")
    
    # [Step 4] Deactivate the experiment metric and update the description
    updated_metric = {
        "lifecycle": LifecycleStage.INACTIVE,  # pauses computation of this metric
        "description": "No longer need to compute this."
    }
    
    update_response = client.create_or_update_metric(
        experiment_metric_id=example_metric_id,
        resource=updated_metric,
        etag=create_response.e_tag,  # Ensures If-Match header is sent
        match_condition=None  # Not specifying match_condition as we're using etag
    )
    
    print(f"Updated metric: {update_response.id}, etag: {update_response.e_tag}.")
    
    # [Step 5] Delete the experiment metric
    client.delete_metric(
        experiment_metric_id=example_metric_id,
        etag=update_response.e_tag  # Ensures If-Match header is sent
    )
    
    print(f"Deleted metric: {example_metric_id}.")
    
except HttpResponseError as error:
    print(f"The operation failed with error: {error}")
```

<!-- END SNIPPET -->

## Next steps

Have a look at the [samples][azure_exp_samples] folder, containing fully runnable Python code for synchronous and asynchronous clients.

## Contributing

This project welcomes contributions and suggestions. Most contributions require
you to agree to a Contributor License Agreement (CLA) declaring that you have
the right to, and actually do, grant us the rights to use your contribution.
For details, visit <https://cla.microsoft.co>m.

When you submit a pull request, a CLA-bot will automatically determine whether
you need to provide a CLA and decorate the PR appropriately (e.g., label,
comment). Simply follow the instructions provided by the bot. You will only
need to do this once across all repos using our CLA.

This project has adopted the
[Microsoft Open Source Code of Conduct][code_of_conduct]. For more information,
see the Code of Conduct FAQ or contact <opencode@microsoft.com> with any
additional questions or comments.

<!-- LINKS -->
[code_of_conduct]: https://opensource.microsoft.com/codeofconduct/
[azure_identity_credentials]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity#credentials

[default_azure_credential]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity#defaultazurecredential
[azure_sub]: https://azure.microsoft.com/free/
[azure_exp_workspace]: https://learn.microsoft.com/azure/templates/microsoft.onlineexperimentation/workspaces
[app_config]: https://learn.microsoft.com/azure/azure-app-configuration/overview
[azure_monitor]: https://learn.microsoft.com/azure/azure-monitor/overview
[azure_exp_samples]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/onlineexperimentation/azure-onlineexperimentation/samples/
