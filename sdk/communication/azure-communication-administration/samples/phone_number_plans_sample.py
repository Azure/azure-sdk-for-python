# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: phone_number_plans_sample.py
DESCRIPTION:
    These samples demonstrate phone plan samples.

    ///listing phone plans via a connection string, country code, phone plan id and phone plan group id
USAGE:
    python phone_number_plans_sample.py
"""
import os
from azure.communication.administration import (
    PhoneNumberAdministrationClient
)

class CommunicationPhonePlansSamples(object):

    def __init__(self):
        self.connection_str = os.getenv('AZURE_COMMUNICATION_SERVICE_CONNECTION_STRING')
        self._phone_number_administration_client = PhoneNumberAdministrationClient.from_connection_string(
            self.connection_str)
        self.country_code = os.getenv('AZURE_COMMUNICATION_SERVICE_TNM_COUNTRY_CODE', "US")
        self.phone_plan_group_id = os.getenv('AZURE_COMMUNICATION_SERVICE_TNM_PHONE_PLAN_GROUP_ID', "phone-plan-group-id")
        self.phone_plan_id = os.getenv('AZURE_COMMUNICATION_SERVICE_TNM_PHONE_PLAN_ID', "phone-plan-id")

    def list_phone_plan_groups(self):
        phone_plan_groups_response = self._phone_number_administration_client.list_phone_plan_groups(
            country_code=self.country_code
        )
        print('list_phone_plan_groups:')
        for phone_plan_group in phone_plan_groups_response:
            print(phone_plan_group)

    def list_phone_plans(self):
        phone_plans_response = self._phone_number_administration_client.list_phone_plans(
            country_code=self.country_code,
            phone_plan_group_id=self.phone_plan_group_id
        )
        print('list_phone_plans:')
        for phone_plan in phone_plans_response:
            print(phone_plan)

    def get_phone_plan_location_options(self):
        location_options_response = self._phone_number_administration_client.get_phone_plan_location_options(
            country_code=self.country_code,
            phone_plan_group_id=self.phone_plan_group_id,
            phone_plan_id=self.phone_plan_id
        )
        print('get_phone_plan_location_options:')
        print(location_options_response)

if __name__ == '__main__':
    sample = CommunicationPhonePlansSamples()
    sample.list_phone_plan_groups()
    sample.list_phone_plans()
    sample.get_phone_plan_location_options()
