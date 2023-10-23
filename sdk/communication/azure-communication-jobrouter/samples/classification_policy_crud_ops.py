# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: classification_policy_crud_ops.py
DESCRIPTION:
    These samples demonstrates how to create Classification Policy used in ACS JobRouter.
    You need a valid connection string to an Azure Communication Service to execute the sample

USAGE:
    python classification_policy_crud_ops.py
    Set the environment variables with your own values before running the sample:
    1) AZURE_COMMUNICATION_SERVICE_ENDPOINT - Communication Service endpoint url
"""

import os


class ClassificationPolicySamples(object):
    endpoint = os.environ.get("AZURE_COMMUNICATION_SERVICE_ENDPOINT", None)
    if not endpoint:
        raise ValueError("Set AZURE_COMMUNICATION_SERVICE_ENDPOINT env before run this sample.")

    _cp_policy_id = "sample_cp_policy"

    def create_classification_policy(self):
        connection_string = self.endpoint
        policy_id = self._cp_policy_id
        # [START create_classification_policy]
        from azure.communication.jobrouter import (
            JobRouterAdministrationClient,
            ClassificationPolicy,
            StaticRouterRule,
            ExpressionRouterRule,
            StaticQueueSelectorAttachment,
            ConditionalQueueSelectorAttachment,
            RouterQueueSelector,
            ConditionalWorkerSelectorAttachment,
            RouterWorkerSelector,
            LabelOperator
        )

        # set `connection_string` to an existing ACS endpoint
        router_admin_client = JobRouterAdministrationClient.from_connection_string(conn_str = connection_string)
        print("JobRouterAdministrationClient created successfully!")

        classification_policy: ClassificationPolicy = router_admin_client.create_classification_policy(
            classification_policy_id = policy_id,
            classification_policy = ClassificationPolicy(
                prioritization_rule = StaticRouterRule(value = 10),
                queue_selectors = [
                    StaticQueueSelectorAttachment(
                        queue_selector = RouterQueueSelector(
                            key = "Region",
                            label_operator = LabelOperator.EQUAL,
                            value = "NA"
                        )
                    ),
                    ConditionalQueueSelectorAttachment(
                        condition = ExpressionRouterRule(expression = "If(job.Product = \"O365\", true, false)"),
                        queue_selectors = [
                            RouterQueueSelector(key = "Product", label_operator = LabelOperator.EQUAL, value = "O365"),
                            RouterQueueSelector(key = "QGroup", label_operator = LabelOperator.EQUAL, value = "NA_O365")
                        ]
                    ),
                ],
                worker_selectors = [
                    ConditionalWorkerSelectorAttachment(
                        condition = ExpressionRouterRule(expression = "If(job.Product = \"O365\", true, false)"),
                        worker_selectors = [
                            RouterWorkerSelector(key = "Skill_O365", label_operator = LabelOperator.EQUAL, value = True),
                            RouterWorkerSelector(
                                key = "Skill_O365_Lvl",
                                label_operator = LabelOperator.GREATER_THAN_EQUAL,
                                value = 1
                            )
                        ]
                    ),
                    ConditionalWorkerSelectorAttachment(
                        condition = ExpressionRouterRule(expression = "If(job.HighPriority = \"true\", true, false)"),
                        worker_selectors = [
                            RouterWorkerSelector(
                                key = "Skill_O365_Lvl",
                                label_operator = LabelOperator.GREATER_THAN_EQUAL,
                                value = 10
                            )
                        ]
                    )
                ]
            )
        )

        print(f"Classification Policy successfully created with id: {classification_policy.id}")

        # [END create_classification_policy]

    def update_classification_policy(self):
        connection_string = self.endpoint
        policy_id = self._cp_policy_id
        # [START update_classification_policy]
        from azure.communication.jobrouter import (
            JobRouterAdministrationClient,
            ClassificationPolicy,
            ExpressionRouterRule,
        )

        # set `connection_string` to an existing ACS endpoint
        router_admin_client = JobRouterAdministrationClient.from_connection_string(conn_str = connection_string)
        print("JobRouterAdministrationClient created successfully!")

        updated_classification_policy: ClassificationPolicy = router_admin_client.update_classification_policy(
            classification_policy_id = policy_id,
            prioritization_rule = ExpressionRouterRule(
                expression = "If(job.HighPriority = \"true\", 50, 10)"
            )
        )

        print(f"Classification policy successfully update with new prioritization rule")
        # [END update_classification_policy]

    def get_classification_policy(self):
        connection_string = self.endpoint
        policy_id = self._cp_policy_id
        # [START get_classification_policy]
        from azure.communication.jobrouter import JobRouterAdministrationClient

        router_admin_client = JobRouterAdministrationClient.from_connection_string(conn_str = connection_string)

        classification_policy = router_admin_client.get_classification_policy(classification_policy_id = policy_id)

        print(f"Successfully fetched classification policy with id: {classification_policy.id}")
        # [END get_classification_policy]

    def list_classification_policies_batched(self):
        connection_string = self.endpoint
        # [START list_classification_policies_batched]
        from azure.communication.jobrouter import JobRouterAdministrationClient

        router_admin_client = JobRouterAdministrationClient.from_connection_string(conn_str = connection_string)

        classification_policy_iterator = router_admin_client.list_classification_policies(results_per_page = 10)

        for policy_page in classification_policy_iterator.by_page():
            policies_in_page = list(policy_page)
            print(f"Retrieved {len(policies_in_page)} policies in current page")

            for cp in policies_in_page:
                print(f"Retrieved classification policy with id: {cp.classification_policy.id}")

        print(f"Successfully completed fetching classification policies")
        # [END list_classification_policies_batched]

    def list_classification_policies(self):
        connection_string = self.endpoint
        # [START list_classification_policies]
        from azure.communication.jobrouter import JobRouterAdministrationClient

        router_admin_client = JobRouterAdministrationClient.from_connection_string(conn_str = connection_string)

        classification_policy_iterator = router_admin_client.list_classification_policies()

        for cp in classification_policy_iterator:
            print(f"Retrieved classification policy with id: {cp.classification_policy.id}")

        print(f"Successfully completed fetching classification policies")
        # [END list_classification_policies]

    def clean_up(self):
        connection_string = self.endpoint
        policy_id = self._cp_policy_id

        # [START delete_classification_policy]
        from azure.communication.jobrouter import JobRouterAdministrationClient

        router_admin_client = JobRouterAdministrationClient.from_connection_string(conn_str = connection_string)

        router_admin_client.delete_classification_policy(classification_policy_id = policy_id)

        # [END delete_classification_policy]


if __name__ == '__main__':
    sample = ClassificationPolicySamples()
    sample.create_classification_policy()
    sample.update_classification_policy()
    sample.get_classification_policy()
    sample.list_classification_policies()
    sample.list_classification_policies_batched()
    sample.clean_up()
