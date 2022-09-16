# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_hooks_async.py

DESCRIPTION:
    This sample demonstrates how to create, get, list, update, and delete hooks
    under your Metrics Advisor account. EmailNotificationHook is used as an example in this sample.

USAGE:
    python sample_hooks_async.py

    Set the environment variables with your own values before running the sample:
    1) METRICS_ADVISOR_ENDPOINT - the endpoint of your Azure Metrics Advisor service
    2) METRICS_ADVISOR_SUBSCRIPTION_KEY - Metrics Advisor service subscription key
    3) METRICS_ADVISOR_API_KEY - Metrics Advisor service API key
"""

import os
import asyncio


async def sample_create_hook_async():
    # [START create_hook_async]
    from azure.ai.metricsadvisor import MetricsAdvisorKeyCredential
    from azure.ai.metricsadvisor.aio import MetricsAdvisorAdministrationClient
    from azure.ai.metricsadvisor.models import EmailNotificationHook

    service_endpoint = os.getenv("METRICS_ADVISOR_ENDPOINT")
    subscription_key = os.getenv("METRICS_ADVISOR_SUBSCRIPTION_KEY")
    api_key = os.getenv("METRICS_ADVISOR_API_KEY")

    client = MetricsAdvisorAdministrationClient(service_endpoint,
                                  MetricsAdvisorKeyCredential(subscription_key, api_key))

    async with client:
        hook = await client.create_hook(
            hook=EmailNotificationHook(
                name="email hook",
                description="my email hook",
                emails_to_alert=["alertme@alertme.com"],
                external_link="https://docs.microsoft.com/en-us/azure/cognitive-services/metrics-advisor/how-tos/alerts"
            )
        )

        return hook
    # [END create_hook_async]


async def sample_get_hook_async(hook_id):
    # [START get_hook_async]
    from azure.ai.metricsadvisor import MetricsAdvisorKeyCredential
    from azure.ai.metricsadvisor.aio import MetricsAdvisorAdministrationClient

    service_endpoint = os.getenv("METRICS_ADVISOR_ENDPOINT")
    subscription_key = os.getenv("METRICS_ADVISOR_SUBSCRIPTION_KEY")
    api_key = os.getenv("METRICS_ADVISOR_API_KEY")

    client = MetricsAdvisorAdministrationClient(service_endpoint,
                                  MetricsAdvisorKeyCredential(subscription_key, api_key))
    async with client:
        hook = await client.get_hook(hook_id)

        print("Hook name: {}".format(hook.name))
        print("Description: {}".format(hook.description))
        print("Emails to alert: {}".format(hook.emails_to_alert))
        print("External link: {}".format(hook.external_link))
        print("Admins: {}".format(hook.admins))

    # [END get_hook_async]


async def sample_list_hooks_async():
    # [START list_hooks_async]
    from azure.ai.metricsadvisor import MetricsAdvisorKeyCredential
    from azure.ai.metricsadvisor.aio import MetricsAdvisorAdministrationClient

    service_endpoint = os.getenv("METRICS_ADVISOR_ENDPOINT")
    subscription_key = os.getenv("METRICS_ADVISOR_SUBSCRIPTION_KEY")
    api_key = os.getenv("METRICS_ADVISOR_API_KEY")

    client = MetricsAdvisorAdministrationClient(service_endpoint,
                                  MetricsAdvisorKeyCredential(subscription_key, api_key))

    async with client:
        hooks = client.list_hooks()
        async for hook in hooks:
            print("Hook type: {}".format(hook.hook_type))
            print("Hook name: {}".format(hook.name))
            print("Description: {}\n".format(hook.description))

    # [END list_hooks_async]


async def sample_update_hook_async(hook):
    # [START update_hook_async]
    from azure.ai.metricsadvisor import MetricsAdvisorKeyCredential
    from azure.ai.metricsadvisor.aio import MetricsAdvisorAdministrationClient

    service_endpoint = os.getenv("METRICS_ADVISOR_ENDPOINT")
    subscription_key = os.getenv("METRICS_ADVISOR_SUBSCRIPTION_KEY")
    api_key = os.getenv("METRICS_ADVISOR_API_KEY")

    client = MetricsAdvisorAdministrationClient(service_endpoint,
                                  MetricsAdvisorKeyCredential(subscription_key, api_key))

    hook.name = "updated hook name"
    hook.description = "updated hook description"

    async with client:
        updated = await client.update_hook(
            hook,
            emails_to_alert=["newemail@alertme.com"]
        )
        print("Updated name: {}".format(updated.name))
        print("Updated description: {}".format(updated.description))
        print("Updated emails: {}".format(updated.emails_to_alert))
    # [END update_hook_async]


async def sample_delete_hook_async(hook_id):
    # [START delete_hook_async]
    from azure.core.exceptions import ResourceNotFoundError
    from azure.ai.metricsadvisor import MetricsAdvisorKeyCredential
    from azure.ai.metricsadvisor.aio import MetricsAdvisorAdministrationClient

    service_endpoint = os.getenv("METRICS_ADVISOR_ENDPOINT")
    subscription_key = os.getenv("METRICS_ADVISOR_SUBSCRIPTION_KEY")
    api_key = os.getenv("METRICS_ADVISOR_API_KEY")

    client = MetricsAdvisorAdministrationClient(service_endpoint,
                                  MetricsAdvisorKeyCredential(subscription_key, api_key))

    async with client:
        await client.delete_hook(hook_id)

        try:
            await client.get_hook(hook_id)
        except ResourceNotFoundError:
            print("Hook successfully deleted.")
    # [END delete_hook_async]


async def main():
    print("---Creating hook...")
    hook = await sample_create_hook_async()
    print("Hook successfully created...")
    print("\n---Get a hook...")
    await sample_get_hook_async(hook.id)
    print("\n---List hooks...")
    await sample_list_hooks_async()
    print("\n---Update a hook...")
    await sample_update_hook_async(hook)
    print("\n---Delete a hook...")
    await sample_delete_hook_async(hook.id)


if __name__ == '__main__':
    asyncio.run(main())
