# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: exception_policy_crud_ops_async.py
DESCRIPTION:
    These samples demonstrates how to create Exception Policy used in ACS JobRouter.
    You need a valid connection string to an Azure Communication Service to execute the sample

USAGE:
    python exception_policy_crud_ops_async.py
    Set the environment variables with your own values before running the sample:
    1) AZURE_COMMUNICATION_SERVICE_ENDPOINT - Communication Service endpoint url
"""

import os
import asyncio


class ExceptionPolicySamplesAsync(object):
    endpoint = os.environ.get("AZURE_COMMUNICATION_SERVICE_ENDPOINT", None)
    if not endpoint:
        raise ValueError("Set AZURE_COMMUNICATION_SERVICE_ENDPOINT env before run this sample.")

    _ep_policy_id = "sample_ep_policy"

    async def create_exception_policy(self):
        connection_string = self.endpoint
        policy_id = self._ep_policy_id
        # [START create_exception_policy_async]
        from azure.communication.jobrouter.aio import JobRouterAdministrationClient
        from azure.communication.jobrouter import (
            WaitTimeExceptionTrigger,
            QueueLengthExceptionTrigger,
            ReclassifyExceptionAction,
            ExceptionRule,
            ExceptionPolicy
        )

        # set `connection_string` to an existing ACS endpoint
        router_admin_client = JobRouterAdministrationClient.from_connection_string(conn_str = connection_string)
        print("JobRouterAdministrationClient created successfully!")

        # we are going to create 2 rules:
        # 1. EscalateJobOnQueueOverFlowTrigger: triggers when queue has more than 10 jobs already en-queued,
        #                                       then reclassifies job adding additional labels on the job.
        # 2. EscalateJobOnWaitTimeExceededTrigger: triggers when job has waited in the queue for more than 10 minutes,
        #                                          then reclassifies job adding additional labels on the job

        # define exception trigger for queue over flow
        queue_length_exception_trigger: QueueLengthExceptionTrigger = QueueLengthExceptionTrigger(threshold = 10)

        # define exception actions that needs to be executed when trigger condition is satisfied
        escalate_job_on_queue_over_flow: ReclassifyExceptionAction = ReclassifyExceptionAction(
            classification_policy_id = "escalation-on-q-over-flow",
            labels_to_upsert = {
                "EscalateJob": True,
                "EscalationReasonCode": "QueueOverFlow"
            }
        )

        # define second exception trigger for wait time
        wait_time_exception_trigger: WaitTimeExceptionTrigger = WaitTimeExceptionTrigger(threshold_seconds = 10 * 60)

        # define exception actions that needs to be executed when trigger condition is satisfied
        escalate_job_on_wait_time_exceeded: ReclassifyExceptionAction = ReclassifyExceptionAction(
            classification_policy_id = "escalation-on-wait-time-exceeded",
            labels_to_upsert = {
                "EscalateJob": True,
                "EscalationReasonCode": "WaitTimeExceeded"
            }
        )

        # define exception rule

        exception_rule = {
            "EscalateJobOnQueueOverFlowTrigger": ExceptionRule(
                trigger = queue_length_exception_trigger,
                actions = {
                    "EscalationJobActionOnQueueOverFlow": escalate_job_on_queue_over_flow
                }
            ),
            "EscalateJobOnWaitTimeExceededTrigger": ExceptionRule(
                trigger = wait_time_exception_trigger,
                actions = {
                    "EscalationJobActionOnWaitTimeExceed": escalate_job_on_wait_time_exceeded
                }
            )
        }

        # create the exception policy
        # set a unique value to `policy_id`
        async with router_admin_client:
            exception_policy = await router_admin_client.create_exception_policy(
                exception_policy_id = policy_id,
                exception_policy = ExceptionPolicy(
                    name = "TriggerJobCancellationWhenQueueLenIs10",
                    exception_rules = exception_rule
                )
            )

            print(f"Exception policy has been successfully created with id: {exception_policy.id}")
        # [END create_exception_policy_async]

    async def update_exception_policy(self):
        connection_string = self.endpoint
        policy_id = self._ep_policy_id
        # [START update_exception_policy_async]
        from azure.communication.jobrouter.aio import JobRouterAdministrationClient
        from azure.communication.jobrouter import (
            WaitTimeExceptionTrigger,
            ReclassifyExceptionAction,
            ExceptionPolicy,
            ExceptionRule,
            QueueLengthExceptionTrigger,
        )

        # set `connection_string` to an existing ACS endpoint
        router_admin_client = JobRouterAdministrationClient.from_connection_string(conn_str = connection_string)
        print("JobRouterAdministrationClient created successfully!")

        # we are going to
        # 1. Add an exception rule: EscalateJobOnWaitTimeExceededTrigger2Min: triggers when job has waited in the
        # queue for more than 2 minutes, then reclassifies job adding additional labels on the job
        # 2. Modify an existing rule: EscalateJobOnQueueOverFlowTrigger: change 'threshold' to 100
        # 3. Delete an exception rule: EscalateJobOnWaitTimeExceededTrigger to be deleted

        # let's define the new rule to be added
        # define exception trigger
        escalate_job_on_wait_time_exceed2: WaitTimeExceptionTrigger = WaitTimeExceptionTrigger(
            threshold_seconds = 2 * 60
        )

        # define exception action
        escalate_job_on_wait_time_exceeded2: ReclassifyExceptionAction = ReclassifyExceptionAction(
            classification_policy_id = "escalation-on-wait-time-exceeded",
            labels_to_upsert = {
                "EscalateJob": True,
                "EscalationReasonCode": "WaitTimeExceeded2Min"
            }
        )

        async with router_admin_client:
            updated_exception_policy: ExceptionPolicy = await router_admin_client.update_exception_policy(
                exception_policy_id = policy_id,
                exception_rules = {
                    # adding new rule
                    "EscalateJobOnWaitTimeExceededTrigger2Min": ExceptionRule(
                        trigger = escalate_job_on_wait_time_exceed2,
                        actions = {
                            "EscalationJobActionOnWaitTimeExceed": escalate_job_on_wait_time_exceeded2
                        }
                    ),
                    # modifying existing rule
                    "EscalateJobOnQueueOverFlowTrigger": ExceptionRule(
                        trigger = QueueLengthExceptionTrigger(threshold = 100),
                        actions = {
                            "EscalationJobActionOnQueueOverFlow": ReclassifyExceptionAction(
                                classification_policy_id = "escalation-on-q-over-flow",
                                labels_to_upsert = {
                                    "EscalateJob": True,
                                    "EscalationReasonCode": "QueueOverFlow"
                                }
                            )
                        }
                    ),
                    # deleting existing rule
                    "EscalateJobOnWaitTimeExceededTrigger": None
                }
            )

            print(f"Exception policy updated with rules: {[k for k,v in updated_exception_policy.exception_rules.items()]}")
            print("Exception policy has been successfully updated")

        # [END update_exception_policy_async]

    async def get_exception_policy(self):
        connection_string = self.endpoint
        policy_id = self._ep_policy_id
        # [START get_exception_policy_async]
        from azure.communication.jobrouter.aio import JobRouterAdministrationClient

        router_admin_client = JobRouterAdministrationClient.from_connection_string(conn_str = connection_string)

        async with router_admin_client:
            exception_policy = await router_admin_client.get_exception_policy(exception_policy_id = policy_id)

            print(f"Successfully fetched exception policy with id: {exception_policy.id}")
        # [END get_exception_policy_async]

    async def list_exception_policies(self):
        connection_string = self.endpoint
        # [START list_exception_policies_async]
        from azure.communication.jobrouter.aio import JobRouterAdministrationClient

        router_admin_client = JobRouterAdministrationClient.from_connection_string(conn_str = connection_string)

        async with router_admin_client:
            exception_policy_iterator = router_admin_client.list_exception_policies()

            async for ep in exception_policy_iterator:
                print(f"Retrieved exception policy with id: {ep.exception_policy.id}")

            print(f"Successfully completed fetching exception policies")
        # [END list_exception_policies_async]

    async def list_exception_policies_batched(self):
        connection_string = self.endpoint
        # [START list_exception_policies_batched_async]
        from azure.communication.jobrouter.aio import JobRouterAdministrationClient

        router_admin_client = JobRouterAdministrationClient.from_connection_string(conn_str = connection_string)

        async with router_admin_client:
            exception_policy_iterator = router_admin_client.list_exception_policies(results_per_page = 10)

            async for policy_page in exception_policy_iterator.by_page():
                policies_in_page = [i async for i in policy_page]
                print(f"Retrieved {len(policies_in_page)} policies in current page")

                for ep in policies_in_page:
                    print(f"Retrieved exception policy with id: {ep.exception_policy.id}")

            print(f"Successfully completed fetching exception policies")
        # [END list_exception_policies_batched_async]

    async def clean_up(self):
        connection_string = self.endpoint
        policy_id = self._ep_policy_id

        # [START delete_exception_policy_async]
        from azure.communication.jobrouter.aio import JobRouterAdministrationClient

        router_admin_client = JobRouterAdministrationClient.from_connection_string(conn_str = connection_string)

        async with router_admin_client:
            await router_admin_client.delete_exception_policy(exception_policy_id = policy_id)

        # [END delete_exception_policy_async]


async def main():
    sample = ExceptionPolicySamplesAsync()
    await sample.create_exception_policy()
    await sample.get_exception_policy()
    await sample.update_exception_policy()
    await sample.list_exception_policies()
    await sample.list_exception_policies_batched()
    await sample.clean_up()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
