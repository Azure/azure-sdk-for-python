# pylint: disable=line-too-long,useless-suppression
# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# Code generated by Microsoft (R) AutoRest Code Generator.
# Changes may cause incorrect behavior and will be lost if the code is regenerated.
# --------------------------------------------------------------------------

from azure.identity import DefaultAzureCredential

from azure.mgmt.monitor import MonitorManagementClient

"""
# PREREQUISITES
    pip install azure-identity
    pip install azure-mgmt-monitor
# USAGE
    python create_or_update_scheduled_query_rule_log_to_metric_action.py

    Before run the sample, please set the values of the client ID, tenant ID and client secret
    of the AAD application as environment variables: AZURE_CLIENT_ID, AZURE_TENANT_ID,
    AZURE_CLIENT_SECRET. For more info about how to get the value, please see:
    https://docs.microsoft.com/azure/active-directory/develop/howto-create-service-principal-portal
"""


def main():
    client = MonitorManagementClient(
        credential=DefaultAzureCredential(),
        subscription_id="af52d502-a447-4bc6-8cb7-4780fbb00490",
    )

    response = client.scheduled_query_rules.create_or_update(
        resource_group_name="alertsweu",
        rule_name="logtometricfoo",
        parameters={
            "location": "West Europe",
            "properties": {
                "action": {
                    "criteria": [{"dimensions": [], "metricName": "Average_% Idle Time"}],
                    "odata.type": "Microsoft.WindowsAzure.Management.Monitoring.Alerts.Models.Microsoft.AppInsights.Nexus.DataContracts.Resources.ScheduledQueryRules.LogToMetricAction",
                },
                "description": "log to metric description",
                "enabled": "true",
                "source": {
                    "dataSourceId": "/subscriptions/af52d502-a447-4bc6-8cb7-4780fbb00490/resourceGroups/alertsweu/providers/Microsoft.OperationalInsights/workspaces/alertsweu"
                },
            },
            "tags": {},
        },
    )
    print(response)


# x-ms-original-file: specification/monitor/resource-manager/Microsoft.Insights/stable/2018-04-16/examples/createOrUpdateScheduledQueryRule-LogToMetricAction.json
if __name__ == "__main__":
    main()
