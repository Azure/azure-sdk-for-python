# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import unittest

import azure.mgmt.resource
from testutils.common_recordingtestcase import record
from tests.mgmt_testcase import HttpStatusCode, AzureMgmtTestCase


class MgmtResourcePolicyTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtResourcePolicyTest, self).setUp()
        self.client = self.create_basic_client(
            azure.mgmt.resource.Client,
            subscription_id=self.settings.SUBSCRIPTION_ID,
        )

    @record
    def test_policy_definition(self):
        policy_def_operations = self.client.policy_definitions()
        policy_assignments_operations = self.client.policy_assignments()

        self.create_resource_group()
        policy_name = self.get_resource_name('pypolicy')
        policy_assignment_name = self.get_resource_name('pypolicyassignment')

        definition = policy_def_operations.create_or_update(
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

        definition = policy_def_operations.get(
            definition.name
        )

        policies = list(policy_def_operations.list())
        self.assertGreater(len(policies), 0)

        # Policy Assignement - By Name
        scope = '/subscriptions/{}/resourceGroups/{}'.format(
            self.settings.SUBSCRIPTION_ID,
            self.group_name
        )
        assignment = policy_assignments_operations.create(
            scope,
            policy_assignment_name,
            {
                'policy_definition_id': definition.id,
            }
        )

        assignment = policy_assignments_operations.get(
            assignment.scope,
            assignment.name
        )

        assignments = list(policy_assignments_operations.list())
        self.assertGreater(len(assignments), 0)

        assignments = list(policy_assignments_operations.list_for_resource_group(
            self.group_name
        ))
        self.assertEqual(len(assignments), 1)

        policy_assignments_operations.delete(
            scope,
            policy_assignment_name
        )

        # Policy Assignement - By Id
        scope = '/subscriptions/{}/resourceGroups/{}'.format(
            self.settings.SUBSCRIPTION_ID,
            self.group_name
        )
        policy_id = '{}/providers/Microsoft.Authorization/policyAssignments/{}'.format(
            scope,
            policy_assignment_name
        )
        assignment = policy_assignments_operations.create_by_id(
            policy_id,
            {
                'policy_definition_id': definition.id,
            }
        )            

        assignment = policy_assignments_operations.get_by_id(
            assignment.id,
        )

        policy_assignments_operations.delete_by_id(
            assignment.id
        )

        # Delete definitions
        policy_def_operations.delete(
            definition.name
        )


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
