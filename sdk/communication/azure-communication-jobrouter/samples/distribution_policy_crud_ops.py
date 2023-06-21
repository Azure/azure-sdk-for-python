# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: distribution_policy_crud_ops.py
DESCRIPTION:
    These samples demonstrates how to create Distribution Policy used in ACS JobRouter.
    You need a valid connection string to an Azure Communication Service to execute the sample

USAGE:
    python distribution_policy_crud_ops.py
    Set the environment variables with your own values before running the sample:
    1) AZURE_COMMUNICATION_SERVICE_ENDPOINT - Communication Service endpoint url
"""

import os


class DistributionPolicySamples(object):
    endpoint = os.environ.get("AZURE_COMMUNICATION_SERVICE_ENDPOINT", None)
    if not endpoint:
        raise ValueError("Set AZURE_COMMUNICATION_SERVICE_ENDPOINT env before run this sample.")

    _dp_policy_id = "sample_dp_policy"

    def create_distribution_policy(self):
        connection_string = self.endpoint
        policy_id = self._dp_policy_id
        # [START create_distribution_policy]
        from azure.communication.jobrouter import (
            JobRouterAdministrationClient,
            DistributionPolicy,
            LongestIdleMode,
        )

        # set `connection_string` to an existing ACS endpoint
        router_admin_client = JobRouterAdministrationClient.from_connection_string(conn_str = connection_string)
        print("JobRouterAdministrationClient created successfully!")

        distribution_policy: DistributionPolicy = router_admin_client.create_distribution_policy(
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

        # [END create_distribution_policy]

    def update_distribution_policy(self):
        connection_string = self.endpoint
        policy_id = self._dp_policy_id
        # [START update_distribution_policy]
        from azure.communication.jobrouter import (
            JobRouterAdministrationClient,
            DistributionPolicy,
            RoundRobinMode,
        )

        # set `connection_string` to an existing ACS endpoint
        router_admin_client = JobRouterAdministrationClient.from_connection_string(conn_str = connection_string)
        print("JobRouterAdministrationClient created successfully!")

        updated_distribution_policy: DistributionPolicy = router_admin_client.update_distribution_policy(
            distribution_policy_id = policy_id,
            mode = RoundRobinMode(
                min_concurrent_offers = 1,
                max_concurrent_offers = 1
            )
        )

        print(f"Distribution policy successfully update with new distribution mode")
        # [END update_distribution_policy]

    def get_distribution_policy(self):
        connection_string = self.endpoint
        policy_id = self._dp_policy_id
        # [START get_distribution_policy]
        from azure.communication.jobrouter import JobRouterAdministrationClient

        router_admin_client = JobRouterAdministrationClient.from_connection_string(conn_str = connection_string)

        distribution_policy = router_admin_client.get_distribution_policy(distribution_policy_id = policy_id)

        print(f"Successfully fetched distribution policy with id: {distribution_policy.id}")
        # [END get_distribution_policy]

    def list_distribution_policies(self):
        connection_string = self.endpoint
        # [START list_distribution_policies]
        from azure.communication.jobrouter import JobRouterAdministrationClient

        router_admin_client = JobRouterAdministrationClient.from_connection_string(conn_str = connection_string)

        distribution_policy_iterator = router_admin_client.list_distribution_policies()

        for dp in distribution_policy_iterator:
            print(f"Retrieved distribution policy with id: {dp.distribution_policy.id}")

        print(f"Successfully completed fetching distribution policies")
        # [END list_distribution_policies]

    def list_distribution_policies_batched(self):
        connection_string = self.endpoint
        # [START list_distribution_policies_batched]
        from azure.communication.jobrouter import JobRouterAdministrationClient

        router_admin_client = JobRouterAdministrationClient.from_connection_string(conn_str = connection_string)

        distribution_policy_iterator = router_admin_client.list_distribution_policies(results_per_page = 10)

        for policy_page in distribution_policy_iterator.by_page():
            policies_in_page = list(policy_page)
            print(f"Retrieved {len(policies_in_page)} policies in current page")

            for dp in policies_in_page:
                print(f"Retrieved distribution policy with id: {dp.distribution_policy.id}")

        print(f"Successfully completed fetching distribution policies")
        # [END list_distribution_policies_batched]

    def clean_up(self):
        connection_string = self.endpoint
        policy_id = self._dp_policy_id

        # [START delete_distribution_policy]
        from azure.communication.jobrouter import JobRouterAdministrationClient

        router_admin_client = JobRouterAdministrationClient.from_connection_string(conn_str = connection_string)

        router_admin_client.delete_distribution_policy(distribution_policy_id = policy_id)

        # [END delete_distribution_policy]


if __name__ == '__main__':
    sample = DistributionPolicySamples()
    sample.create_distribution_policy()
    sample.update_distribution_policy()
    sample.get_distribution_policy()
    sample.list_distribution_policies()
    sample.list_distribution_policies_batched()
    sample.clean_up()
