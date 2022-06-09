# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: exception_policy_crud_ops.py
DESCRIPTION:
    These samples demonstrates how to create Exception Policy used in ACS JobRouter.
    You need a valid connection string to an Azure Communication Service to execute the sample

USAGE:
    python exception_policy_crud_ops.py
    Set the environment variables with your own values before running the sample:
    1) AZURE_COMMUNICATION_SERVICE_ENDPOINT - Communication Service endpoint url
"""

import os


class ExceptionPolicySamples(object):
    endpoint = os.environ.get("AZURE_COMMUNICATION_SERVICE_ENDPOINT", None)
    if not endpoint:
        raise ValueError("Set AZURE_COMMUNICATION_SERVICE_ENDPOINT env before run this sample.")

    _ep_policy_id = "sample_ep_policy"

    def create_exception_policy(self):
        connection_string = self.endpoint
        policy_id = self._ep_policy_id
        # [START create_exception_policy]
        from azure.communication.jobrouter import (
            RouterClient,
            WaitTimeExceptionTrigger,
            QueueLengthExceptionTrigger,
            CancelExceptionAction,
            ExceptionRule
        )

        # set `connection_string` to an existing ACS endpoint
        router_client = RouterClient.from_connection_string(conn_str = connection_string)
        print("RouterClient created successfully!")

        # define an exception trigger
        # set up a QueueLengthExceptionTrigger with a threshold of 10,
        # i.e., kick off exception if there are already 10 jobs in a queue
        exception_trigger = QueueLengthExceptionTrigger(threshold = 10)

        # define an exception action
        # this sets up what action to take when an exception trigger condition is fulfilled
        # for this scenario, we simply cancel job
        exception_action = CancelExceptionAction()

        # define the exception rule combining the trigger and action
        # you can chain multiple rules together, so it is important to give a unique
        # `id` to the exception rule. For this use-case, the exception rule will be the following

        exception_rule = {
            "CancelJobWhenQueueThresholdIs10": ExceptionRule(
                trigger = exception_trigger,
                actions = {
                    "CancelJobActionWhenQueueIsFull": exception_action
                }
            )
        }

        # create the exception policy
        # set a unique value to `policy_id`
        exception_policy = router_client.create_exception_policy(
            identifier = policy_id,
            name = "TriggerJobCancellationWhenQueueLenIs10",
            exception_rules = exception_rule
        )

        print(f"Exception policy has been successfully created with id: {exception_policy.id}")
        # [END create_exception_policy]

    def update_exception_policy(self):
        connection_string = self.endpoint
        policy_id = self._ep_policy_id
        # [START update_exception_policy]
        from azure.communication.jobrouter import (
            RouterClient,
            WaitTimeExceptionTrigger,
            CancelExceptionAction,
            ExceptionRule
        )

        # set `connection_string` to an existing ACS endpoint
        router_client = RouterClient.from_connection_string(conn_str = connection_string)
        print("RouterClient created successfully!")

        # get the exception policy
        # set `policy_id` to an existing exception policy id
        exception_policy = router_client.get_exception_policy(
            identifier = policy_id,
        )

        # add additional exception rule to policy
        new_exception_trigger = WaitTimeExceptionTrigger(threshold = "PT1H")
        # define an exception action
        # this sets up what action to take when an exception trigger condition is fulfilled
        # for this scenario, we simply cancel job
        exception_action = CancelExceptionAction()
        new_exception_rule = ExceptionRule(
            trigger = new_exception_trigger,
            actions = {
                "CancelJobActionWhenJobInQFor1Hr": exception_action
            }
        )
        exception_policy.exception_rules["CancelJobWhenInQueueFor1Hr"] = new_exception_rule

        updated_exception_policy = router_client.update_exception_policy(
            identifier = policy_id,
            exception_policy = exception_policy
        )

        print(f"Exception policy updated with rules: {[k for k,v in updated_exception_policy.exception_rules.items()]}")
        print("Exception policy has been successfully updated")

        # [END update_exception_policy]

    def get_exception_policy(self):
        connection_string = self.endpoint
        policy_id = self._ep_policy_id
        # [START get_exception_policy]
        from azure.communication.jobrouter import RouterClient

        router_client = RouterClient.from_connection_string(conn_str = connection_string)

        exception_policy = router_client.get_exception_policy(identifier = policy_id)

        print(f"Successfully fetched exception policy with id: {exception_policy.id}")
        # [END get_exception_policy]

    def list_exception_policies(self):
        connection_string = self.endpoint
        # [START list_exception_policies]
        from azure.communication.jobrouter import RouterClient

        router_client = RouterClient.from_connection_string(conn_str = connection_string)

        exception_policy_iterator = router_client.list_exception_policies(results_per_page = 10)

        for policy_page in exception_policy_iterator.by_page():
            policies_in_page = list(policy_page)
            print(f"Retrieved {len(policies_in_page)} policies in current page")

            for ep in policies_in_page:
                print(f"Retrieved exception policy with id: {ep.id}")

        print(f"Successfully completed fetching exception policies")
        # [END list_exception_policies]

    def clean_up(self):
        connection_string = self.endpoint
        policy_id = self._ep_policy_id

        # [START delete_exception_policy]
        from azure.communication.jobrouter import RouterClient

        router_client = RouterClient.from_connection_string(conn_str = connection_string)

        router_client.delete_exception_policy(identifier = policy_id)

        # [END delete_exception_policy]


if __name__ == '__main__':
    sample = ExceptionPolicySamples()
    sample.create_exception_policy()
    sample.update_exception_policy()
    sample.get_exception_policy()
    sample.list_exception_policies()
    sample.clean_up()
