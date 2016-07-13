# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#--------------------------------------------------------------------------
import unittest

import azure.mgmt.resource
from testutils.common_recordingtestcase import record
from tests.mgmt_testcase import HttpStatusCode, AzureMgmtTestCase


class MgmtResourceFeaturesTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtResourceFeaturesTest, self).setUp()
        self.features_client = self.create_mgmt_client(
            azure.mgmt.resource.FeatureClient
        )

    @record
    def test_features(self):
        features = list(self.features_client.features.list_all())
        self.assertGreater(len(features), 0)
        self.assertTrue(all(isinstance(v, azure.mgmt.resource.features.models.FeatureResult) for v in features))


        features = list(self.features_client.features.list('Microsoft.Compute'))
        self.assertGreater(len(features), 0)
        self.assertTrue(all(isinstance(v, azure.mgmt.resource.features.models.FeatureResult) for v in features))

        one_feature = features[0]
        feature = self.features_client.features.get(
            'Microsoft.Compute',
            one_feature.name.split('/')[1]
        )

        self.features_client.features.register(
            'Microsoft.Compute',
            feature.name.split('/')[1]
        )


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
