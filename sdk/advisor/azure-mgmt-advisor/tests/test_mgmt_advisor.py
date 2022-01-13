# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import azure.mgmt.advisor
import datetime
import re
import unittest

from azure.mgmt.advisor.models import (
    ConfigData
)

from devtools_testutils import (
    AzureMgmtRecordedTestCase, ResourceGroupPreparer, recorded_by_proxy
)

# the goal of these tests is to validate AutoRest generation of the Python wrapper
# and NOT to validate the behavior of the API. so the tests will primarily attempt
# to verify that all operations are possible using the generated client and that
# the operations can accept valid input and produce valid output.

class TestMgmtAdvisor(AzureMgmtRecordedTestCase):

    def setup_method(self, method):
        self.client = self.create_mgmt_client(
            azure.mgmt.advisor.AdvisorManagementClient
        )

    @recorded_by_proxy
    def test_generate_recommendations(self):

        def call(response, *args, **kwargs):
            return response.http_response

        # trigger generate recommendations
        response = self.client.recommendations.generate(cls=call)

        # we should get a valid Location header back
        assert 'Location' in response.headers
        location = response.headers['Location']

        # extract the operation ID from the Location header
        operation_id = re.findall("[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", location)

        # the operation ID should be a valid GUID
        assert operation_id != None
        assert len(operation_id), 1

        # we should be able to get generation status for this operation ID
        response = self.client.recommendations.get_generate_status(
            cls=call,
            operation_id = operation_id[0]
        )
        status_code = response.status_code

        # and the status should be 202 or 204
        assert status_code == 202 or status_code == 204

    @unittest.skip("unavailable")
    @recorded_by_proxy
    def test_suppressions(self):

        # first, get all recommendations
        response = list(self.client.recommendations.list())

        # we should have at least one recommendation
        assert len(response) != 0
        recommendation = None

        # the recommendation should have all relevant properties populated
        for rec in response:
            assert rec.id != None
            assert rec.name != None
            assert rec.type != None
            assert rec.category != None
            assert rec.impact != None
            # assert rec.risk != None
            assert rec.short_description != None
            assert rec.short_description.problem != None
            assert rec.short_description.solution != None
            if (rec.impacted_value != None):
                recommendation = rec

        # construct the properties needed for further operations
        resourceUri = recommendation.id[:recommendation.id.find("/providers/Microsoft.Advisor/recommendations")]
        recommendationName = recommendation.name
        suppressionName = "Python_SDK_Test"
        timeToLive = "00:01:00:00"

        # get the individual recommendation
        output = self.client.recommendations.get(
            resource_uri = resourceUri,
            recommendation_id = recommendationName
        )

        # it should be identical to what we got from list
        assert output.id == rec.id
        assert output.name == rec.name

        # create a new suppression
        suppression = self.client.suppressions.create(
            resource_uri = resourceUri,
            recommendation_id = recommendationName,
            name = suppressionName,
            ttl = timeToLive
        )

        # it should get created successfully
        assert suppression.ttl == "01:00:00"

        # get the suppression
        sup = self.client.suppressions.get(
            resource_uri = resourceUri,
            recommendation_id = recommendationName,
            name = suppressionName
        )

        # it should be identical to what we just added
        assert sup.name == suppressionName
        assert sup.id == resourceUri + "/providers/Microsoft.Advisor/recommendations/" + recommendationName + "/suppressions/" + suppressionName

        # delete the suppression
        self.client.suppressions.delete(
            resource_uri = resourceUri,
            recommendation_id = recommendationName,
            name = suppressionName
        )

        # the suppression should be gone
        #response = list(self.client.suppressions.list())
        #for sup in response:
        #    assert sup.Name != suppressionName

    @unittest.skip("unavailable")
    @recorded_by_proxy
    def test_configurations_subscription(self):

        # create a new configuration to update low CPU threshold to 20
        input = ConfigData()
        input.low_cpu_threshold=20

        # update the configuration
        response = self.client.configurations.create_in_subscription(input)

        # retrieve the configurations
        output = list(self.client.configurations.list_by_subscription())[0]

        # it should be identical to what we just set
        assert output.low_cpu_threshold == "20"

        # restore the default configuration
        input.low_cpu_threshold=5
        response = self.client.configurations.create_in_subscription(input)

        # retrieve the configurations
        output = list(self.client.configurations.list_by_subscription())[0]

        # it should be identical to what we just set
        assert output.low_cpu_threshold == "5"

    @ResourceGroupPreparer()
    @recorded_by_proxy
    def test_configurations_resourcegroup(self, resource_group):
        resourceGroupName = resource_group.name
        configurationName = "default"

        # create a new configuration to update exclude to True
        input = ConfigData()
        input.exclude=True

        # update the configuration
        self.client.configurations.create_in_resource_group(
            configuration_name=configurationName,
            resource_group=resourceGroupName,
            config_contract=input
        )

        # retrieve the configurations
        output = list(self.client.configurations.list_by_resource_group(resource_group = resourceGroupName))[0]

        # it should be identical to what we just set
        assert output.exclude == True

        # restore the default configuration
        input.exclude=False
        self.client.configurations.create_in_resource_group(
            configuration_name=configurationName,
            resource_group=resourceGroupName,
            config_contract=input
        )

        # retrieve the configurations
        output = list(self.client.configurations.list_by_resource_group(resource_group = resourceGroupName))[0]

        # it should be identical to what we just set
        assert output.exclude == False

#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
