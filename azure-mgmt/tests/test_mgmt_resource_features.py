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


class MgmtResourceFeaturesTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtResourceFeaturesTest, self).setUp()
        self.client = self.create_basic_client(
            azure.mgmt.resource.Client,
            subscription_id=self.settings.SUBSCRIPTION_ID,
        )

    @record
    def test_features(self):
        models = azure.mgmt.resource.models('2015-12-01')
        features_operations = self.client.features('2015-12-01')

        features = list(features_operations.list_all())
        self.assertGreater(len(features), 0)
        self.assertTrue(all(isinstance(v, models.FeatureResult) for v in features))


        features = list(features_operations.list('Microsoft.Compute'))
        self.assertGreater(len(features), 0)
        self.assertTrue(all(isinstance(v, models.FeatureResult) for v in features))

        one_feature = features[0]
        feature = features_operations.get(
            'Microsoft.Compute',
            one_feature.name.split('/')[1]
        )

        features_operations.register(
            'Microsoft.Compute',
            feature.name.split('/')[1]
        )


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
