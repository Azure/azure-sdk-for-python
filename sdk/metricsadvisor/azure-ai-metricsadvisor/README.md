# Azure Metrics Advisor client library for Python
Metrics Advisor is a scalable real-time time series monitoring, alerting, and root cause analysis platform. Use Metrics Advisor to:

- Analyze multi-dimensional data from multiple data sources
- Identify and correlate anomalies
- Configure and fine-tune the anomaly detection model used on your data
- Diagnose anomalies and help with root cause analysis

[Source code][src_code] | [Package (Pypi)][package] | [API reference documentation][reference_documentation] | [Product documentation][ma_docs] | [Samples][samples_readme]

## Getting started

### Install the package

Install the Azure Metrics Advisor client library for Python with pip:

```commandline
pip install azure-ai-metricsadvisor --pre
```

### Prerequisites

* Python 2.7, or 3.5 or later is required to use this package.
* You need an [Azure subscription][azure_sub], and a [Metrics Advisor serivce][ma_service] to use this package.

### Authenticate the client

You will need two keys to authenticate the client:

1) The subscription key to your Metrics Advisor resource. You can find this in the Keys and Endpoint section of your resource in the Azure portal.
2) The API key for your Metrics Advisor instance. You can find this in the web portal for Metrics Advisor, in API keys on the left navigation menu.

We can use the keys to create a new `MetricsAdvisorClient` or `MetricsAdvisorAdministrationClient`.

```py
import os
from azure.ai.metricsadvisor import (
    MetricsAdvisorKeyCredential,
    MetricsAdvisorClient,
    MetricsAdvisorAdministrationClient,
)

service_endpoint = os.getenv("ENDPOINT")
subscription_key = os.getenv("SUBSCRIPTION_KEY")
api_key = os.getenv("API_KEY")

client = MetricsAdvisorClient(service_endpoint,
                            MetricsAdvisorKeyCredential(subscription_key, api_key))

admin_client = MetricsAdvisorAdministrationClient(service_endpoint,
                            MetricsAdvisorKeyCredential(subscription_key, api_key))
```

## Key concepts

### MetricsAdvisorClient

`MetricsAdvisorClient` helps with:

- listing incidents
- listing root causes of incidents
- retrieving original time series data and time series data enriched by the service.
- listing alerts
- adding feedback to tune your model

### MetricsAdvisorAdministrationClient

`MetricsAdvisorAdministrationClient` allows you to

- manage data feeds
- manage anomaly detection configurations
- manage anomaly alerting configurations
- manage hooks

### DataFeed

A `DataFeed` is what Metrics Advisor ingests from your data source, such as Cosmos DB or a SQL server. A data feed contains rows of:

- timestamps
- zero or more dimensions
- one or more measures

### Metric

A `DataFeedMetric` is a quantifiable measure that is used to monitor and assess the status of a specific business process. It can be a combination of multiple time series values divided into dimensions. For example a web health metric might contain dimensions for user count and the en-us market.

### AnomalyDetectionConfiguration

`AnomalyDetectionConfiguration` is required for every time series, and determines whether a point in the time series is an anomaly. 

### Anomaly & Incident

After a detection configuration is applied to metrics, `AnomalyIncident`s are generated whenever any series within it has an `DataPointAnomaly`.

### Alert

You can configure which anomalies should trigger an `AnomalyAlert`. You can set multiple alerts with different settings. For example, you could create an alert for anomalies with lower business impact, and another for more important alerts.

### Notification Hook

Metrics Advisor lets you create and subscribe to real-time alerts. These alerts are sent over the internet, using a notification hook like `EmailNotificationHook` or `WebNotificationHook`.

## Examples

* [Add a data feed from a sample or data source](#add-a-data-feed-from-a-sample-or-data-source "Add a data feed from a sample or data source")
* [Check ingestion status](#check-ingestion-status "Check ingestion status")
* [Configure anomaly detection configuration](#configure-anomaly-detection-configuration "Configure anomaly detection configuration")
* [Configure alert configuration](#configure-alert-configuration "Configure alert configuration")
* [Query anomaly detection results](#query-anomaly-detection-results "Query anomaly detection results")
* [Query incidents](#query-incidents "Query incidents")
* [Query root causes](#query-root-causes "Query root causes")
* [Add hooks for receiving anomaly alerts](#add-hooks-for-receiving-anomaly-alerts "Add hooks for receiving anomaly alerts")

### Add a data feed from a sample or data source

Metrics Advisor supports connecting different types of data sources. Here is a sample to ingest data from SQL Server.

```py
import os
import datetime
from azure.ai.metricsadvisor import MetricsAdvisorKeyCredential, MetricsAdvisorAdministrationClient
from azure.ai.metricsadvisor.models import (
        SQLServerDataFeed,
        DataFeedSchema,
        DataFeedMetric,
        DataFeedDimension,
        DataFeedOptions,
        DataFeedRollupSettings,
        DataFeedMissingDataPointFillSettings
    )

service_endpoint = os.getenv("ENDPOINT")
subscription_key = os.getenv("SUBSCRIPTION_KEY")
api_key = os.getenv("API_KEY")
sql_server_connection_string = os.getenv("SQL_SERVER_CONNECTION_STRING")
query = os.getenv("SQL_SERVER_QUERY")

client = MetricsAdvisorAdministrationClient(
    service_endpoint,
    MetricsAdvisorKeyCredential(subscription_key, api_key)
)

data_feed = client.create_data_feed(
    name="My data feed",
    source=SQLServerDataFeed(
        connection_string=sql_server_connection_string,
        query=query,
    ),
    granularity="Daily",
    schema=DataFeedSchema(
        metrics=[
            DataFeedMetric(name="cost", display_name="Cost"),
            DataFeedMetric(name="revenue", display_name="Revenue")
        ],
        dimensions=[
            DataFeedDimension(name="category", display_name="Category"),
            DataFeedDimension(name="city", display_name="City")
        ],
        timestamp_column="Timestamp"
    ),
    ingestion_settings=datetime.datetime(2019, 10, 1),
    options=DataFeedOptions(
        data_feed_description="cost/revenue data feed",
        rollup_settings=DataFeedRollupSettings(
            rollup_type="AutoRollup",
            rollup_method="Sum",
            rollup_identification_value="__CUSTOM_SUM__"
        ),
        missing_data_point_fill_settings=DataFeedMissingDataPointFillSettings(
            fill_type="SmartFilling"
        ),
        access_mode="Private"
    )
)

return data_feed
```

### Check ingestion status

After we start the data ingestion, we can check the ingestion status.

```py
import datetime
from azure.ai.metricsadvisor import MetricsAdvisorKeyCredential, MetricsAdvisorAdministrationClient

service_endpoint = os.getenv("ENDPOINT")
subscription_key = os.getenv("SUBSCRIPTION_KEY")
api_key = os.getenv("API_KEY")
data_feed_id = os.getenv("DATA_FEED_ID")

client = MetricsAdvisorAdministrationClient(service_endpoint,
    MetricsAdvisorKeyCredential(subscription_key, api_key)
)

ingestion_status = client.list_data_feed_ingestion_status(
    data_feed_id,
    datetime.datetime(2020, 9, 20),
    datetime.datetime(2020, 9, 25)
)
for status in ingestion_status:
    print("Timestamp: {}".format(status.timestamp))
    print("Status: {}".format(status.status))
    print("Message: {}\n".format(status.message))
```

### Configure anomaly detection configuration

While a default detection configuration is automatically applied to each metric, we can tune the detection modes used on our data by creating a customized anomaly detection configuration.

```py
from azure.ai.metricsadvisor import MetricsAdvisorKeyCredential, MetricsAdvisorAdministrationClient
from azure.ai.metricsadvisor.models import (
    ChangeThresholdCondition,
    HardThresholdCondition,
    SmartDetectionCondition,
    SuppressCondition,
    MetricDetectionCondition,
)

service_endpoint = os.getenv("ENDPOINT")
subscription_key = os.getenv("SUBSCRIPTION_KEY")
api_key = os.getenv("API_KEY")
metric_id = os.getenv("METRIC_ID")

client = MetricsAdvisorAdministrationClient(
    service_endpoint,
    MetricsAdvisorKeyCredential(subscription_key, api_key)
)

change_threshold_condition = ChangeThresholdCondition(
    anomaly_detector_direction="Both",
    change_percentage=20,
    shift_point=10,
    within_range=True,
    suppress_condition=SuppressCondition(
        min_number=5,
        min_ratio=2
    )
)
hard_threshold_condition = HardThresholdCondition(
    anomaly_detector_direction="Up",
    upper_bound=100,
    suppress_condition=SuppressCondition(
        min_number=2,
        min_ratio=2
    )
)
smart_detection_condition = SmartDetectionCondition(
    anomaly_detector_direction="Up",
    sensitivity=10,
    suppress_condition=SuppressCondition(
        min_number=2,
        min_ratio=2
    )
)

detection_config = client.create_detection_configuration(
    name="my_detection_config",
    metric_id=metric_id,
    description="anomaly detection config for metric",
    whole_series_detection_condition=MetricDetectionCondition(
        cross_conditions_operator="OR",
        change_threshold_condition=change_threshold_condition,
        hard_threshold_condition=hard_threshold_condition,
        smart_detection_condition=smart_detection_condition
    )
)
return detection_config
```

### Configure alert configuration

Then let's configure in which conditions an alert needs to be triggered.

```py
from azure.ai.metricsadvisor import MetricsAdvisorKeyCredential, MetricsAdvisorAdministrationClient
from azure.ai.metricsadvisor.models import (
    MetricAlertConfiguration,
    MetricAnomalyAlertScope,
    TopNGroupScope,
    MetricAnomalyAlertConditions,
    SeverityCondition,
    MetricBoundaryCondition,
    MetricAnomalyAlertSnoozeCondition,
)
service_endpoint = os.getenv("ENDPOINT")
subscription_key = os.getenv("SUBSCRIPTION_KEY")
api_key = os.getenv("API_KEY")
anomaly_detection_configuration_id = os.getenv("DETECTION_CONFIGURATION_ID")
hook_id = os.getenv("HOOK_ID")

client = MetricsAdvisorAdministrationClient(
    service_endpoint,
    MetricsAdvisorKeyCredential(subscription_key, api_key)
)

alert_config = client.create_alert_configuration(
    name="my alert config",
    description="alert config description",
    cross_metrics_operator="AND",
    metric_alert_configurations=[
        MetricAlertConfiguration(
            detection_configuration_id=anomaly_detection_configuration_id,
            alert_scope=MetricAnomalyAlertScope(
                scope_type="WholeSeries"
            ),
            alert_conditions=MetricAnomalyAlertConditions(
                severity_condition=SeverityCondition(
                    min_alert_severity="Low",
                    max_alert_severity="High"
                )
            )
        ),
        MetricAlertConfiguration(
            detection_configuration_id=anomaly_detection_configuration_id,
            alert_scope=MetricAnomalyAlertScope(
                scope_type="TopN",
                top_n_group_in_scope=TopNGroupScope(
                    top=10,
                    period=5,
                    min_top_count=5
                )
            ),
            alert_conditions=MetricAnomalyAlertConditions(
                metric_boundary_condition=MetricBoundaryCondition(
                    direction="Up",
                    upper=50
                )
            ),
            alert_snooze_condition=MetricAnomalyAlertSnoozeCondition(
                auto_snooze=2,
                snooze_scope="Metric",
                only_for_successive=True
            )
        ),
    ],
    hook_ids=[hook_id]
)

return alert_config
```

### Query anomaly detection results

We can query the alerts and anomalies.

```py
import datetime
from azure.ai.metricsadvisor import MetricsAdvisorKeyCredential, MetricsAdvisorClient

service_endpoint = os.getenv("ENDPOINT")
subscription_key = os.getenv("SUBSCRIPTION_KEY")
api_key = os.getenv("API_KEY")
alert_config_id = os.getenv("ALERT_CONFIG_ID")
alert_id = os.getenv("ALERT_ID")

client = MetricsAdvisorClient(service_endpoint,
    MetricsAdvisorKeyCredential(subscription_key, api_key)
)

results = client.list_alerts(
    alert_configuration_id=alert_config_id,
    start_time=datetime.datetime(2020, 1, 1),
    end_time=datetime.datetime(2020, 9, 9),
    time_mode="AnomalyTime",
)
for result in results:
    print("Alert id: {}".format(result.id))
    print("Create on: {}".format(result.created_on))

results = client.list_anomalies(
    alert_configuration_id=alert_config_id,
    alert_id=alert_id,
)
for result in results:
    print("Create on: {}".format(result.created_on))
    print("Severity: {}".format(result.severity))
    print("Status: {}".format(result.status))
```

### Query incidents

We can query the incidents for a detection configuration.

```py
import datetime
from azure.ai.metricsadvisor import MetricsAdvisorKeyCredential, MetricsAdvisorClient

service_endpoint = os.getenv("ENDPOINT")
subscription_key = os.getenv("SUBSCRIPTION_KEY")
api_key = os.getenv("API_KEY")
anomaly_detection_configuration_id = os.getenv("DETECTION_CONFIGURATION_ID")

client = MetricsAdvisorClient(service_endpoint,
    MetricsAdvisorKeyCredential(subscription_key, api_key)
)

results = client.list_incidents(
            detection_configuration_id=anomaly_detection_configuration_id,
            start_time=datetime.datetime(2020, 1, 1),
            end_time=datetime.datetime(2020, 9, 9),
        )
for result in results:
    print("Metric id: {}".format(result.metric_id))
    print("Incident ID: {}".format(result.id))
    print("Severity: {}".format(result.severity))
    print("Status: {}".format(result.status))
```

### Query root causes

We can also query the root causes of an incident

```py
from azure.ai.metricsadvisor import MetricsAdvisorKeyCredential, MetricsAdvisorClient

service_endpoint = os.getenv("ENDPOINT")
subscription_key = os.getenv("SUBSCRIPTION_KEY")
api_key = os.getenv("API_KEY")
anomaly_detection_configuration_id = os.getenv("DETECTION_CONFIGURATION_ID")
incident_id = os.getenv("INCIDENT_ID")

client = MetricsAdvisorClient(service_endpoint,
    MetricsAdvisorKeyCredential(subscription_key, api_key)
)

results = client.list_incident_root_causes(
            detection_configuration_id=anomaly_detection_configuration_id,
            incident_id=incident_id,
        )
for result in results:
    print("Score: {}".format(result.score))
    print("Description: {}".format(result.description))

```


### Add hooks for receiving anomaly alerts

We can add some hooks so when an alert is triggered, we can get call back.

```py
from azure.ai.metricsadvisor import MetricsAdvisorKeyCredential, MetricsAdvisorAdministrationClient
from azure.ai.metricsadvisor.models import EmailNotificationHook

service_endpoint = os.getenv("ENDPOINT")
subscription_key = os.getenv("SUBSCRIPTION_KEY")
api_key = os.getenv("API_KEY")

client = MetricsAdvisorAdministrationClient(service_endpoint,
    MetricsAdvisorKeyCredential(subscription_key, api_key))

hook = client.create_hook(
    hook=EmailNotificationHook(
        name="email hook",
        description="my email hook",
        emails_to_alert=["alertme@alertme.com"],
        external_link="https://docs.microsoft.com/en-us/azure/cognitive-services/metrics-advisor/how-tos/alerts"
    )
)
```

### Async APIs

This library includes a complete async API supported on Python 3.5+. To use it, you must
first install an async transport, such as [aiohttp](https://pypi.org/project/aiohttp/).
See
[azure-core documentation][azure_core_docs]
for more information.


```py
from azure.ai.metricsadvisor import MetricsAdvisorKeyCredential
from azure.ai.metricsadvisor.aio import MetricsAdvisorClient, MetricsAdvisorAdministrationClient

client = MetricsAdvisorClient(
    service_endpoint,
    MetricsAdvisorKeyCredential(subscription_key, api_key)
)

admin_client = MetricsAdvisorAdministrationClient(
    service_endpoint,
    MetricsAdvisorKeyCredential(subscription_key, api_key)
)
```

## Troubleshooting

### General

The Azure Metrics Advisor clients will raise exceptions defined in [Azure Core][azure_core].

### Logging
This library uses the standard
[logging][python_logging] library for logging.

Basic information about HTTP sessions (URLs, headers, etc.) is logged at `INFO` level.

Detailed `DEBUG` level logging, including request/response bodies and **unredacted**
headers, can be enabled on the client or per-operation with the `logging_enable` keyword argument.

See full SDK logging documentation with examples [here][sdk_logging_docs].

## Next steps

### More sample code

 For more details see the [samples README][samples_readme].

## Contributing

This project welcomes contributions and suggestions.  Most contributions require
you to agree to a Contributor License Agreement (CLA) declaring that you have
the right to, and actually do, grant us the rights to use your contribution. For
details, visit [cla.microsoft.com][cla].

This project has adopted the [Microsoft Open Source Code of Conduct][code_of_conduct].
For more information see the [Code of Conduct FAQ][coc_faq]
or contact [opencode@microsoft.com][coc_contact] with any
additional questions or comments.

<!-- LINKS -->
[src_code]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/metricsadvisor/azure-ai-metricsadvisor
[reference_documentation]: https://aka.ms/azsdk/python/metricsadvisor/docs
[ma_docs]: https://docs.microsoft.com/azure/cognitive-services/metrics-advisor/overview
[azure_cli]: https://docs.microsoft.com/cli/azure
[azure_sub]: https://azure.microsoft.com/free/
[package]: https://aka.ms/azsdk/python/metricsadvisor/pypi
[ma_service]: https://go.microsoft.com/fwlink/?linkid=2142156
[python_logging]: https://docs.python.org/3.5/library/logging.html
[azure_core]: https://aka.ms/azsdk/python/core/docs#module-azure.core.exceptions
[azure_core_docs]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/core/azure-core/README.md#transport
[sdk_logging_docs]: https://docs.microsoft.com/azure/developer/python/azure-sdk-logging
[samples_readme]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/metricsadvisor/azure-ai-metricsadvisor/samples/README.md

[cla]: https://cla.microsoft.com
[code_of_conduct]: https://opensource.microsoft.com/codeofconduct/
[coc_faq]: https://opensource.microsoft.com/codeofconduct/faq/
[coc_contact]: mailto:opencode@microsoft.com
