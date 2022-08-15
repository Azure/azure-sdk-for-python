# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_alert_configuration.py

DESCRIPTION:
    This sample demonstrates how to create, get, list, query, update, and delete anomaly alert configurations
    under your Metrics Advisor account.

USAGE:
    python sample_alert_configuration.py

    Set the environment variables with your own values before running the sample:
    1) METRICS_ADVISOR_ENDPOINT - the endpoint of your Azure Metrics Advisor service
    2) METRICS_ADVISOR_SUBSCRIPTION_KEY - Metrics Advisor service subscription key
    3) METRICS_ADVISOR_API_KEY - Metrics Advisor service API key
    4) METRICS_ADVISOR_DETECTION_CONFIGURATION_ID - the ID of an existing detection configuration
    5) METRICS_ADVISOR_HOOK_ID - the ID of hook you would like to be associated with the alert configuration
"""

import os


def sample_create_alert_config():
    # [START create_alert_config]
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
    service_endpoint = os.getenv("METRICS_ADVISOR_ENDPOINT")
    subscription_key = os.getenv("METRICS_ADVISOR_SUBSCRIPTION_KEY")
    api_key = os.getenv("METRICS_ADVISOR_API_KEY")
    detection_configuration_id = os.getenv("METRICS_ADVISOR_DETECTION_CONFIGURATION_ID")
    hook_id = os.getenv("METRICS_ADVISOR_HOOK_ID")

    client = MetricsAdvisorAdministrationClient(service_endpoint,
                                  MetricsAdvisorKeyCredential(subscription_key, api_key))

    alert_config = client.create_alert_configuration(
        name="my alert config",
        description="alert config description",
        cross_metrics_operator="AND",
        metric_alert_configurations=[
            MetricAlertConfiguration(
                detection_configuration_id=detection_configuration_id,
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
                detection_configuration_id=detection_configuration_id,
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
    # [END create_alert_config]


def sample_get_alert_config(alert_config_id):
    # [START get_alert_config]
    from azure.ai.metricsadvisor import MetricsAdvisorKeyCredential, MetricsAdvisorAdministrationClient

    service_endpoint = os.getenv("METRICS_ADVISOR_ENDPOINT")
    subscription_key = os.getenv("METRICS_ADVISOR_SUBSCRIPTION_KEY")
    api_key = os.getenv("METRICS_ADVISOR_API_KEY")

    client = MetricsAdvisorAdministrationClient(service_endpoint,
                                  MetricsAdvisorKeyCredential(subscription_key, api_key))

    config = client.get_alert_configuration(alert_config_id)

    print("Alert config ID: {}".format(config.id))
    print("Alert config name: {}".format(config.name))
    print("Description: {}".format(config.description))
    print("Ids of hooks associated with alert: {}".format(config.hook_ids))
    print("Use {} operator for multiple alert conditions\n".format(config.cross_metrics_operator))

    print("Alert uses detection configuration ID: {}".format(
        config.metric_alert_configurations[0].detection_configuration_id
    ))
    print("Alert scope type: {}".format(config.metric_alert_configurations[0].alert_scope.scope_type))
    print("Alert severity condition: min- {}, max- {}".format(
        config.metric_alert_configurations[0].alert_conditions.severity_condition.min_alert_severity,
        config.metric_alert_configurations[0].alert_conditions.severity_condition.max_alert_severity,
    ))
    print("\nAlert uses detection configuration ID: {}".format(
        config.metric_alert_configurations[1].detection_configuration_id
    ))
    print("Alert scope type: {}".format(config.metric_alert_configurations[1].alert_scope.scope_type))
    print("Top N: {}".format(config.metric_alert_configurations[1].alert_scope.top_n_group_in_scope.top))
    print("Point count used to look back: {}".format(
        config.metric_alert_configurations[1].alert_scope.top_n_group_in_scope.period
    ))
    print("Min top count: {}".format(
        config.metric_alert_configurations[1].alert_scope.top_n_group_in_scope.min_top_count
    ))
    print("Alert metric boundary condition direction: {}, upper bound: {}".format(
        config.metric_alert_configurations[1].alert_conditions.metric_boundary_condition.direction,
        config.metric_alert_configurations[1].alert_conditions.metric_boundary_condition.upper,
    ))
    print("Alert snooze condition, snooze point count: {}".format(
        config.metric_alert_configurations[1].alert_snooze_condition.auto_snooze,
    ))
    print("Alert snooze scope: {}".format(
        config.metric_alert_configurations[1].alert_snooze_condition.snooze_scope,
    ))
    print("Snooze only for successive anomalies?: {}".format(
        config.metric_alert_configurations[1].alert_snooze_condition.only_for_successive,
    ))
    # [END get_alert_config]


def sample_list_alert_configs():
    # [START list_alert_configs]
    from azure.ai.metricsadvisor import MetricsAdvisorKeyCredential, MetricsAdvisorAdministrationClient

    service_endpoint = os.getenv("METRICS_ADVISOR_ENDPOINT")
    subscription_key = os.getenv("METRICS_ADVISOR_SUBSCRIPTION_KEY")
    api_key = os.getenv("METRICS_ADVISOR_API_KEY")
    detection_configuration_id = os.getenv("METRICS_ADVISOR_DETECTION_CONFIGURATION_ID")

    client = MetricsAdvisorAdministrationClient(service_endpoint,
                                  MetricsAdvisorKeyCredential(subscription_key, api_key))

    configs = client.list_alert_configurations(detection_configuration_id)
    for config in configs:
        print("Alert config name: {}".format(config.name))
        print("Alert description: {}".format(config.description))
        print("Ids of hooks associated with alert: {}\n".format(config.hook_ids))

    # [END list_alert_configs]


def sample_list_alerts(alert_config_id):
    # [START list_alerts]
    import datetime
    from azure.ai.metricsadvisor import MetricsAdvisorKeyCredential, MetricsAdvisorClient

    service_endpoint = os.getenv("METRICS_ADVISOR_ENDPOINT")
    subscription_key = os.getenv("METRICS_ADVISOR_SUBSCRIPTION_KEY")
    api_key = os.getenv("METRICS_ADVISOR_API_KEY")

    client = MetricsAdvisorClient(service_endpoint,
                                  MetricsAdvisorKeyCredential(subscription_key, api_key))

    results = client.list_alerts(
        alert_configuration_id=alert_config_id,
        start_time=datetime.datetime(2021, 1, 1),
        end_time=datetime.datetime(2021, 9, 9),
        time_mode="AnomalyTime",
    )

    tolist = []
    for result in results:
        tolist.append(result)
        print("Alert id: {}".format(result.id))
        print("Create time: {}".format(result.created_time))
    return tolist
    # [END list_alerts]


def sample_list_anomalies_for_alert(alert_config_id, alert_id):
    # [START list_anomalies_for_alert]
    from azure.ai.metricsadvisor import MetricsAdvisorKeyCredential, MetricsAdvisorClient

    service_endpoint = os.getenv("METRICS_ADVISOR_ENDPOINT")
    subscription_key = os.getenv("METRICS_ADVISOR_SUBSCRIPTION_KEY")
    api_key = os.getenv("METRICS_ADVISOR_API_KEY")

    client = MetricsAdvisorClient(service_endpoint,
                                  MetricsAdvisorKeyCredential(subscription_key, api_key))

    results = client.list_anomalies(
            alert_configuration_id=alert_config_id,
            alert_id=alert_id,
        )
    for result in results:
        print("Create time: {}".format(result.created_time))
        print("Severity: {}".format(result.severity))
        print("Status: {}".format(result.status))

    # [END list_anomalies_for_alert]


def sample_update_alert_config(alert_config):
    # [START update_alert_config]
    from azure.ai.metricsadvisor import MetricsAdvisorKeyCredential, MetricsAdvisorAdministrationClient
    from azure.ai.metricsadvisor.models import (
        MetricAlertConfiguration,
        MetricAnomalyAlertScope,
        MetricAnomalyAlertConditions,
        MetricBoundaryCondition
    )
    service_endpoint = os.getenv("METRICS_ADVISOR_ENDPOINT")
    subscription_key = os.getenv("METRICS_ADVISOR_SUBSCRIPTION_KEY")
    api_key = os.getenv("METRICS_ADVISOR_API_KEY")
    detection_configuration_id = os.getenv("METRICS_ADVISOR_DETECTION_CONFIGURATION_ID")

    client = MetricsAdvisorAdministrationClient(service_endpoint,
                                  MetricsAdvisorKeyCredential(subscription_key, api_key))

    alert_config.name = "updated config name"
    additional_alert = MetricAlertConfiguration(
        detection_configuration_id=detection_configuration_id,
        alert_scope=MetricAnomalyAlertScope(
            scope_type="SeriesGroup",
            series_group_in_scope={'region': 'Shenzhen'}
        ),
        alert_conditions=MetricAnomalyAlertConditions(
            metric_boundary_condition=MetricBoundaryCondition(
                direction="Down",
                lower=5
            )
        )
    )
    alert_config.metric_alert_configurations.append(additional_alert)

    updated = client.update_alert_configuration(
        alert_config,
        cross_metrics_operator="OR",
        description="updated alert config"
    )

    print("Updated alert name: {}".format(updated.name))
    print("Updated alert description: {}".format(updated.description))
    print("Updated cross metrics operator: {}".format(updated.cross_metrics_operator))
    print("Updated alert condition configuration scope type: {}".format(
        updated.metric_alert_configurations[2].alert_scope.scope_type
    ))

    # [END update_alert_config]


def sample_delete_alert_config(alert_config_id):
    # [START delete_alert_config]
    from azure.core.exceptions import ResourceNotFoundError
    from azure.ai.metricsadvisor import MetricsAdvisorKeyCredential, MetricsAdvisorAdministrationClient

    service_endpoint = os.getenv("METRICS_ADVISOR_ENDPOINT")
    subscription_key = os.getenv("METRICS_ADVISOR_SUBSCRIPTION_KEY")
    api_key = os.getenv("METRICS_ADVISOR_API_KEY")

    client = MetricsAdvisorAdministrationClient(service_endpoint,
                                  MetricsAdvisorKeyCredential(subscription_key, api_key))

    client.delete_alert_configuration(alert_config_id)

    try:
        client.get_alert_configuration(alert_config_id)
    except ResourceNotFoundError:
        print("Alert configuration successfully deleted.")
    # [END delete_alert_config]


if __name__ == '__main__':
    print("---Creating anomaly alert configuration...")
    alert_config = sample_create_alert_config()
    print("Anomaly alert configuration successfully created...")
    print("\n---Get an anomaly alert configuration...")
    sample_get_alert_config(alert_config.id)
    print("\n---List anomaly alert configurations...")
    sample_list_alert_configs()
    print("\n---Query anomaly detection results...")
    alerts = sample_list_alerts(alert_config.id)
    if len(alerts) > 0:
        print("\n---Query anomalies using alert id...")
        alert_id = alerts[0].id
        print("alert_id: " + alert_id)
        sample_list_anomalies_for_alert(alert_config.id, alert_id)
    print("\n---Update an anomaly alert configuration...")
    sample_update_alert_config(alert_config)
    print("\n---Delete an anomaly alert configuration...")
    sample_delete_alert_config(alert_config.id)
