# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import unittest

import azure.mgmt.resource
from devtools_testutils import AzureMgmtTestCase, ResourceGroupPreparer

class MgmtResourcePolicyTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtResourcePolicyTest, self).setUp()
        self.policy_client = self.create_mgmt_client(
            azure.mgmt.resource.PolicyClient
        )

    @ResourceGroupPreparer()
    def test_policy_definition(self, resource_group, location):
        policy_name = self.get_resource_name('pypolicy')
        policy_assignment_name = self.get_resource_name('pypolicyassignment')

        definition = self.policy_client.policy_definitions.create_or_update(
            policy_name,
            {
                'policy_type':'Custom',
                'description':'Don\'t create a VM anywhere',
                'policy_rule':{
                    'if':{
                      'allOf':[
                        {
                          'source':'action',
                          'equals':'Microsoft.Compute/virtualMachines/write'
                        },
                        {
                          'field':'location',
                          'in':[
                            'eastus',
                            'eastus2',
                            'centralus'
                          ]
                        }
                      ]
                    },
                    'then':{
                      'effect':'deny'
                    }
                }
            }
        )

        definition = self.policy_client.policy_definitions.get(
            definition.name
        )

        policies = list(self.policy_client.policy_definitions.list())
        assert len(policies) > 0

        # Policy Assignement - By Name
        scope = '/subscriptions/{}/resourceGroups/{}'.format(
            self.settings.SUBSCRIPTION_ID,
            resource_group.name
        )
        assignment = self.policy_client.policy_assignments.create(
            scope,
            policy_assignment_name,
            {
                'policy_definition_id': definition.id,
            }
        )

        assignment = self.policy_client.policy_assignments.get(
            assignment.scope,
            assignment.name
        )

        assignments = list(self.policy_client.policy_assignments.list())
        assert len(assignments) > 0

        assignments = list(self.policy_client.policy_assignments.list_for_resource_group(
            resource_group.name
        ))
        assert len(assignments) >= 1  # At least mine, could be more

        self.policy_client.policy_assignments.delete(
            scope,
            policy_assignment_name
        )

        # Policy Assignement - By Id
        scope = '/subscriptions/{}/resourceGroups/{}'.format(
            self.settings.SUBSCRIPTION_ID,
            resource_group.name
        )
        policy_id = '{}/providers/Microsoft.Authorization/policyAssignments/{}'.format(
            scope,
            policy_assignment_name
        )
        assignment = self.policy_client.policy_assignments.create_by_id(
            policy_id,
            {
                'policy_definition_id': definition.id,
            }
        )

        assignment = self.policy_client.policy_assignments.get_by_id(
            assignment.id,
        )

        self.policy_client.policy_assignments.delete_by_id(
            assignment.id
        )

        # Delete definitions
        self.policy_client.policy_definitions.delete(
            definition.name
        )


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
