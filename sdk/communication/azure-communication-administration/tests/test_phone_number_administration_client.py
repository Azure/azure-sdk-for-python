# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest
import os
from azure.communication.administration import (
    PhoneNumberAdministrationClient,
    PstnConfiguration,
    NumberUpdateCapabilities,
    CreateSearchOptions
)
from phone_number_helper import PhoneNumberUriReplacer
from _shared.testcase import (
    CommunicationTestCase,
    BodyReplacerProcessor
)

class PhoneNumberAdministrationClientTest(CommunicationTestCase):

    def setUp(self):
        super(PhoneNumberAdministrationClientTest, self).setUp()
        self.recording_processors.extend([
            BodyReplacerProcessor(
                keys=["id", "token", "capabilitiesUpdateId", "phoneNumber", "phonePlanIds",
                      "phoneNumberCapabilitiesUpdates",	"releaseId",
                      "phoneNumberReleaseStatusDetails", "searchId", "phoneNumbers",
                      "entities", "phonePlanGroups", "phonePlans", "phoneNumberCapabilitiesUpdate"]
            ),
            PhoneNumberUriReplacer()])
        self._phone_number_administration_client = PhoneNumberAdministrationClient.from_connection_string(
            self.connection_str)
        self.country_code = os.getenv('AZURE_COMMUNICATION_SERVICE_TNM_COUNTRY_CODE', "US")
        self.locale = os.getenv('AZURE_COMMUNICATION_SERVICE_TNM_LOCALE', "en-us")
        self.phone_plan_group_id = os.getenv('AZURE_COMMUNICATION_SERVICE_TNM_PHONE_PLAN_GROUP_ID', "phone-plan-group-id-1")
        self.phone_plan_id = os.getenv('AZURE_COMMUNICATION_SERVICE_TNM_PHONE_PLAN_ID', "phone-plan-id-1")
        self.phone_plan_id_area_codes = os.getenv('AZURE_COMMUNICATION_SERVICE_TNM_PHONE_PLAN_ID_AREA_CODES', "phone-plan-id-1")
        self.area_code_for_search = os.getenv('AZURE_COMMUNICATION_SERVICE_TNM_AREA_CODE_FOR_SEARCH', "777")
        self.search_id = os.getenv('AZURE_COMMUNICATION_SERVICE_TNM_SEARCH_ID', "search-id-1")
        self.search_id_to_purchase = os.getenv('AZURE_COMMUNICATION_SERVICE_TNM_SEARCH_ID_TO_PURCHASE', "search-id-1")
        self.search_id_to_cancel = os.getenv('AZURE_COMMUNICATION_SERVICE_TNM_SEARCH_ID_TO_CANCEL', "search-id-2")
        self.phonenumber_to_configure = os.getenv('AZURE_COMMUNICATION_SERVICE_TNM_PHONENUMBER_TO_CONFIGURE', "+17771234567")
        self.phonenumber_to_get_config = os.getenv('AZURE_COMMUNICATION_SERVICE_TNM_PHONENUMBER_TO_GET_CONFIG', "+17771234567")
        self.phonenumber_to_unconfigure = os.getenv('AZURE_COMMUNICATION_SERVICE_TNM_PHONENUMBER_TO_UNCONFIGURE', "+17771234567")
        self.phonenumber_for_capabilities = os.getenv('AZURE_COMMUNICATION_SERVICE_TNM_PHONENUMBER_FOR_CAPABILITIES', "+17771234567")
        self.capabilities_id = os.getenv('AZURE_COMMUNICATION_SERVICE_TNM_CAPABILITIES_ID', "capabilities-id-1")
        self.release_id = os.getenv('AZURE_COMMUNICATION_SERVICE_TNM_RELEASE_ID', "release_id_1")
        self.scrubber.register_name_pair(
            self.phone_plan_group_id,
            "phone_plan_group_id"
        )
        self.scrubber.register_name_pair(
            self.phone_plan_id,
            "phone_plan_id"
        )
        self.scrubber.register_name_pair(
            self.phone_plan_id_area_codes,
            "phone_plan_id_area_codes"
        )
        self.scrubber.register_name_pair(
            self.area_code_for_search,
            "area_code_for_search"
        )
        self.scrubber.register_name_pair(
            self.search_id,
            "search_id"
        )
        self.scrubber.register_name_pair(
            self.search_id_to_purchase,
            "search_id_to_purchase"
        )
        self.scrubber.register_name_pair(
            self.search_id_to_cancel,
            "search_id_to_cancel"
        )
        self.scrubber.register_name_pair(
            self.phonenumber_to_configure,
            "phonenumber_to_configure"
        )
        self.scrubber.register_name_pair(
            self.phonenumber_to_get_config,
            "phonenumber_to_get_config"
        )
        self.scrubber.register_name_pair(
            self.phonenumber_to_unconfigure,
            "phonenumber_to_unconfigure"
        )
        self.scrubber.register_name_pair(
            self.phonenumber_for_capabilities,
            "phonenumber_for_capabilities"
        )
        self.scrubber.register_name_pair(
            self.capabilities_id,
            "capabilities_id"
        )
        self.scrubber.register_name_pair(
            self.release_id,
            "release_id"
        )

    @pytest.mark.live_test_only
    def test_list_all_phone_numbers(self):
        pages = self._phone_number_administration_client.list_all_phone_numbers()
        assert pages.next() is not None

    @pytest.mark.live_test_only
    def test_get_all_area_codes(self):
        area_codes = self._phone_number_administration_client.get_all_area_codes(
            location_type="NotRequired",
            country_code=self.country_code,
            phone_plan_id=self.phone_plan_id_area_codes
        )
        assert area_codes.primary_area_codes is not None

    @pytest.mark.live_test_only
    def test_get_capabilities_update(self):
        capability_response = self._phone_number_administration_client.get_capabilities_update(
            capabilities_update_id=self.capabilities_id
        )
        assert capability_response.capabilities_update_id is not None

    @pytest.mark.live_test_only
    def test_update_capabilities(self):
        update = NumberUpdateCapabilities(add=iter(["InboundCalling"]))

        phone_number_capabilities_update = {
            self.phonenumber_for_capabilities: update
        }

        capability_response = self._phone_number_administration_client.update_capabilities(
            phone_number_capabilities_update=phone_number_capabilities_update
        )
        assert capability_response.capabilities_update_id is not None

    @pytest.mark.live_test_only
    def test_list_all_supported_countries(self):
        countries = self._phone_number_administration_client.list_all_supported_countries()
        assert countries.next().localized_name is not None

    @pytest.mark.live_test_only
    def test_get_number_configuration(self):
        phone_number_response = self._phone_number_administration_client.get_number_configuration(
            phone_number=self.phonenumber_to_unconfigure
        )
        assert phone_number_response.pstn_configuration is not None

    @pytest.mark.live_test_only
    def test_configure_number(self):
        pstnConfig = PstnConfiguration(
            callback_url="https://callbackurl",
            application_id="ApplicationId",
            azure_pstn_target_id="AzurePstnTargetId"
        )
        self._phone_number_administration_client.configure_number(
            pstn_configuration=pstnConfig,
            phone_number=self.phonenumber_to_unconfigure
        )

    @pytest.mark.live_test_only
    def test_list_phone_plan_groups(self):
        phone_plan_group_response = self._phone_number_administration_client.list_phone_plan_groups(
            country_code=self.country_code
        )
        assert phone_plan_group_response.next().phone_plan_group_id is not None

    @pytest.mark.live_test_only
    def test_list_phone_plans(self):
        phone_plan_response = self._phone_number_administration_client.list_phone_plans(
            country_code=self.country_code,
            phone_plan_group_id=self.phone_plan_group_id
        )
        assert phone_plan_response.next().phone_plan_id is not None

    @pytest.mark.live_test_only
    def test_get_phone_plan_location_options(self):
        location_options_response = self._phone_number_administration_client.get_phone_plan_location_options(
            country_code=self.country_code,
            phone_plan_group_id=self.phone_plan_group_id,
            phone_plan_id=self.phone_plan_id
        )
        assert location_options_response.location_options.label_id is not None

    @pytest.mark.live_test_only
    def test_get_release_by_id(self):
        phone_number_release_response = self._phone_number_administration_client.get_release_by_id(
            release_id=self.release_id
        )
        assert phone_number_release_response.release_id is not None

    @pytest.mark.live_test_only
    def test_list_all_releases(self):
        releases_response = self._phone_number_administration_client.list_all_releases()
        assert releases_response.next().id is not None

    @pytest.mark.live_test_only
    def test_get_search_by_id(self):
        phone_number_search_response = self._phone_number_administration_client.get_search_by_id(
            search_id=self.search_id
        )
        assert phone_number_search_response.search_id is not None

    @pytest.mark.live_test_only
    def test_create_search(self):
        searchOptions = CreateSearchOptions(
            area_code=self.area_code_for_search,
            description="testsearch20200014",
            display_name="testsearch20200014",
            phone_plan_ids=[self.phone_plan_id],
            quantity=1
        )
        search_response = self._phone_number_administration_client.create_search(
            body=searchOptions
        )
        assert search_response.search_id is not None

    @pytest.mark.live_test_only
    def test_cancel_search(self):
        self._phone_number_administration_client.cancel_search(
            search_id=self.search_id_to_cancel
        )

    @pytest.mark.live_test_only
    def test_purchase_search(self):
        self._phone_number_administration_client.purchase_search(
            search_id=self.search_id_to_purchase
        )
