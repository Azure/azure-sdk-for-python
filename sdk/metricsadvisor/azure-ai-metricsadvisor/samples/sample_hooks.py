# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_hooks.py

DESCRIPTION:
    This sample demonstrates how to create, get, list, update, and delete hooks
    under your Metrics Advisor account. EmailNotificationHook is used as an example in this sample.

USAGE:
    python sample_hooks.py

    Set the environment variables with your own values before running the sample:
    1) METRICS_ADVISOR_ENDPOINT - the endpoint of your Azure Metrics Advisor service
    2) METRICS_ADVISOR_SUBSCRIPTION_KEY - Metrics Advisor service subscription key
    3) METRICS_ADVISOR_API_KEY - Metrics Advisor service API key
"""

import os


def sample_create_hook():
    # [START create_hook]
    from azure.ai.metricsadvisor import MetricsAdvisorKeyCredential, MetricsAdvisorAdministrationClient
    from azure.ai.metricsadvisor.models import EmailNotificationHook

    service_endpoint = os.getenv("METRICS_ADVISOR_ENDPOINT")
    subscription_key = os.getenv("METRICS_ADVISOR_SUBSCRIPTION_KEY")
    api_key = os.getenv("METRICS_ADVISOR_API_KEY")

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

    return hook
    # [END create_hook]


def sample_get_hook(hook_id):
    # [START get_hook]
    from azure.ai.metricsadvisor import MetricsAdvisorKeyCredential, MetricsAdvisorAdministrationClient

    service_endpoint = os.getenv("METRICS_ADVISOR_ENDPOINT")
    subscription_key = os.getenv("METRICS_ADVISOR_SUBSCRIPTION_KEY")
    api_key = os.getenv("METRICS_ADVISOR_API_KEY")

    client = MetricsAdvisorAdministrationClient(service_endpoint,
                                  MetricsAdvisorKeyCredential(subscription_key, api_key))

    hook = client.get_hook(hook_id)

    print("Hook name: {}".format(hook.name))
    print("Description: {}".format(hook.description))
    print("Emails to alert: {}".format(hook.emails_to_alert))
    print("External link: {}".format(hook.external_link))
    print("Admins: {}".format(hook.admin_emails))

    # [END get_hook]


def sample_list_hooks():
    # [START list_hooks]
    from azure.ai.metricsadvisor import MetricsAdvisorKeyCredential, MetricsAdvisorAdministrationClient

    service_endpoint = os.getenv("METRICS_ADVISOR_ENDPOINT")
    subscription_key = os.getenv("METRICS_ADVISOR_SUBSCRIPTION_KEY")
    api_key = os.getenv("METRICS_ADVISOR_API_KEY")

    client = MetricsAdvisorAdministrationClient(service_endpoint,
                                  MetricsAdvisorKeyCredential(subscription_key, api_key))

    hooks = client.list_hooks()
    for hook in hooks:
        print("Hook type: {}".format(hook.hook_type))
        print("Hook name: {}".format(hook.name))
        print("Description: {}\n".format(hook.description))

    # [END list_hooks]


def sample_update_hook(hook):
    # [START update_hook]
    from azure.ai.metricsadvisor import MetricsAdvisorKeyCredential, MetricsAdvisorAdministrationClient

    service_endpoint = os.getenv("METRICS_ADVISOR_ENDPOINT")
    subscription_key = os.getenv("METRICS_ADVISOR_SUBSCRIPTION_KEY")
    api_key = os.getenv("METRICS_ADVISOR_API_KEY")

    client = MetricsAdvisorAdministrationClient(service_endpoint,
                                  MetricsAdvisorKeyCredential(subscription_key, api_key))

    hook.name = "updated hook name"
    hook.description = "updated hook description"

    client.update_hook(
        hook,
        emails_to_alert=["newemail@alertme.com"]
    )
    updated = client.get_hook(hook.id)
    print("Updated name: {}".format(updated.name))
    print("Updated description: {}".format(updated.description))
    print("Updated emails: {}".format(updated.emails_to_alert))
    # [END update_hook]


def sample_delete_hook(hook_id):
    # [START delete_hook]
    from azure.core.exceptions import ResourceNotFoundError
    from azure.ai.metricsadvisor import MetricsAdvisorKeyCredential, MetricsAdvisorAdministrationClient

    service_endpoint = os.getenv("METRICS_ADVISOR_ENDPOINT")
    subscription_key = os.getenv("METRICS_ADVISOR_SUBSCRIPTION_KEY")
    api_key = os.getenv("METRICS_ADVISOR_API_KEY")

    client = MetricsAdvisorAdministrationClient(service_endpoint,
                                  MetricsAdvisorKeyCredential(subscription_key, api_key))

    client.delete_hook(hook_id)

    try:
        client.get_hook(hook_id)
    except ResourceNotFoundError:
        print("Hook successfully deleted.")
    # [END delete_hook]


if __name__ == '__main__':
    print("---Creating hook...")
    hook = sample_create_hook()
    print("Hook successfully created...")
    print("\n---Get a hook...")
    sample_get_hook(hook.id)
    print("\n---List hooks...")
    sample_list_hooks()
    print("\n---Update a hook...")
    sample_update_hook(hook)
    print("\n---Delete a hook...")
    sample_delete_hook(hook.id)
