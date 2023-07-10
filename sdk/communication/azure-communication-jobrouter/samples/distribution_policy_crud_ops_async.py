# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: distribution_policy_crud_ops_async.py
DESCRIPTION:
    These samples demonstrates how to create Distribution Policy used in ACS JobRouter.
    You need a valid connection string to an Azure Communication Service to execute the sample

USAGE:
    python distribution_policy_crud_ops_async.py
    Set the environment variables with your own values before running the sample:
    1) AZURE_COMMUNICATION_SERVICE_ENDPOINT - Communication Service endpoint url
"""

import os
import asyncio


class DistributionPolicySamplesAsync(object):
    endpoint = os.environ.get("AZURE_COMMUNICATION_SERVICE_ENDPOINT", None)
    if not endpoint:
        raise ValueError("Set AZURE_COMMUNICATION_SERVICE_ENDPOINT env before run this sample.")

    _dp_policy_id = "sample_dp_policy"

    async def create_distribution_policy(self):
        connection_string = self.endpoint
        policy_id = self._dp_policy_id
        # [START create_distribution_policy_async]
        from azure.communication.jobrouter.aio import JobRouterAdministrationClient
        from azure.communication.jobrouter import (
            DistributionPolicy,
            LongestIdleMode,
        )

        # set `connection_string` to an existing ACS endpoint
        router_admin_client = JobRouterAdministrationClient.from_connection_string(conn_str = connection_string)
        print("JobRouterAdministrationClient created successfully!")

        async with router_admin_client:
            distribution_policy: DistributionPolicy = await router_admin_client.create_distribution_policy(
                distribution_policy_id = policy_id,
                distribution_policy = DistributionPolicy(
                    offer_expires_after_seconds = 1 * 60,
                    mode = LongestIdleMode(
                        min_concurrent_offers = 1,
                        max_concurrent_offers = 1
                    )
                )
            )

            print(f"Distribution Policy successfully created with id: {distribution_policy.id}")

        # [END create_distribution_policy_async]

    async def update_distribution_policy(self):
        connection_string = self.endpoint
        policy_id = self._dp_policy_id
        # [START update_distribution_policy_async]
        from azure.communication.jobrouter.aio import JobRouterAdministrationClient
        from azure.communication.jobrouter import (
            DistributionPolicy,
            RoundRobinMode,
        )

        # set `connection_string` to an existing ACS endpoint
        router_admin_client = JobRouterAdministrationClient.from_connection_string(conn_str = connection_string)
        print("JobRouterAdministrationClient created successfully!")

        async with router_admin_client:
            updated_distribution_policy: DistributionPolicy = await router_admin_client.update_distribution_policy(
                distribution_policy_id = policy_id,
                mode = RoundRobinMode(
                    min_concurrent_offers = 1,
                    max_concurrent_offers = 1
                )
            )

            print(f"Distribution policy successfully update with new distribution mode")
        # [END update_distribution_policy_async]

    async def get_distribution_policy(self):
        connection_string = self.endpoint
        policy_id = self._dp_policy_id
        # [START get_distribution_policy_async]
        from azure.communication.jobrouter.aio import JobRouterAdministrationClient

        router_admin_client = JobRouterAdministrationClient.from_connection_string(conn_str = connection_string)

        async with router_admin_client:
            distribution_policy = await router_admin_client.get_distribution_policy(distribution_policy_id = policy_id)

            print(f"Successfully fetched distribution policy with id: {distribution_policy.id}")
        # [END get_distribution_policy_async]

    async def list_distribution_policies(self):
        connection_string = self.endpoint
        # [START list_distribution_policies_async]
        from azure.communication.jobrouter.aio import JobRouterAdministrationClient

        router_admin_client = JobRouterAdministrationClient.from_connection_string(conn_str = connection_string)

        async with router_admin_client:
            distribution_policy_iterator = router_admin_client.list_distribution_policies()

            async for dp in distribution_policy_iterator:
                print(f"Retrieved distribution policy with id: {dp.distribution_policy.id}")

            print(f"Successfully completed fetching distribution policies")
        # [END list_distribution_policies_async]

    async def list_distribution_policies_batched(self):
        connection_string = self.endpoint
        # [START list_distribution_policies_batched_async]
        from azure.communication.jobrouter.aio import JobRouterAdministrationClient

        router_admin_client = JobRouterAdministrationClient.from_connection_string(conn_str = connection_string)

        async with router_admin_client:
            distribution_policy_iterator = router_admin_client.list_distribution_policies(results_per_page = 10)

            async for policy_page in distribution_policy_iterator.by_page():
                policies_in_page = [i async for i in policy_page]
                print(f"Retrieved {len(policies_in_page)} policies in current page")

                for dp in policies_in_page:
                    print(f"Retrieved distribution policy with id: {dp.distribution_policy.id}")

            print(f"Successfully completed fetching distribution policies")
        # [END list_distribution_policies_batched_async]

    async def clean_up(self):
        connection_string = self.endpoint
        policy_id = self._dp_policy_id

        # [START delete_distribution_policy_async]
        from azure.communication.jobrouter.aio import JobRouterAdministrationClient

        router_admin_client = JobRouterAdministrationClient.from_connection_string(conn_str = connection_string)

        async with router_admin_client:
            await router_admin_client.delete_distribution_policy(distribution_policy_id = policy_id)

        # [END delete_distribution_policy_async]


async def main():
    sample = DistributionPolicySamplesAsync()
    await sample.create_distribution_policy()
    await sample.update_distribution_policy()
    await sample.get_distribution_policy()
    await sample.list_distribution_policies()
    await sample.list_distribution_policies_batched()
    await sample.clean_up()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
