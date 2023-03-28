import json
import re

import pytest
from azure.core.exceptions import HttpResponseError

from tests.conftest import mock_dps_target

registration_id = "test_registration_id"
enrollment_group_id = "test_enrollment_group_id"

endpoint = mock_dps_target["endpoint"]
registration_endpoint = "{}/registrations".format(endpoint)

registrations_url = re.compile("{}/.+".format(registration_endpoint))
query_url = "{}/{}/query".format(registration_endpoint, enrollment_group_id)


class TestDeviceRegistrationStateGet(object):
    @pytest.fixture()
    def service_client_get(self, mocked_response):
        mocked_response.get(
            url=registrations_url,
            body=json.dumps({"registrationId": "enrollment1"}),
            status=200,
            content_type="application/json",
            match_querystring=False,
        )

    @pytest.fixture(params=[404, 500])
    def service_client_get_error(self, mocked_response, request):
        mocked_response.get(
            url=registrations_url,
            body="{}",
            status=request.param,
            content_type="application/json",
            match_querystring=False,
        )

    def test_device_registration_state_get(self, service_client_get, sdk_client):
        sdk_client.device_registration_state.get(id=registration_id)

    def test_device_registration_state_get_error(
        self, service_client_get_error, sdk_client
    ):
        with pytest.raises(HttpResponseError):
            sdk_client.device_registration_state.get(id=registration_id)


class TestDeviceRegistrationStateDelete(object):
    @pytest.fixture()
    def service_client_delete(self, mocked_response):
        mocked_response.delete(
            url=registrations_url,
            body="{}",
            status=204,
            content_type="application/json",
            match_querystring=False,
        )

    @pytest.fixture(params=[404, 500])
    def service_client_delete_error(self, mocked_response, request):
        mocked_response.delete(
            url=registrations_url,
            body="{}",
            status=request.param,
            content_type="application/json",
            match_querystring=False,
        )

    def test_device_registration_state_delete(self, service_client_delete, sdk_client):
        result = sdk_client.device_registration_state.delete(id=registration_id)
        assert not result

    def test_device_registration_state_get_error(
        self, service_client_delete_error, sdk_client
    ):
        with pytest.raises(HttpResponseError):
            sdk_client.device_registration_state.delete(id=registration_id)


class TestDeviceRegistrationStateQuery(object):
    @pytest.fixture()
    def service_client_query(self, mocked_response):
        mocked_response.post(
            url=query_url,
            body=json.dumps([{"registration_id": registration_id}]),
            status=200,
            content_type="application/json",
            match_querystring=False,
        )

    @pytest.fixture(params=[404, 500])
    def service_client_query_error(self, mocked_response, request):
        mocked_response.post(
            url=query_url,
            body="{}",
            status=request.param,
            content_type="application/json",
            match_querystring=False,
        )

    def test_device_registration_state_query(self, service_client_query, sdk_client):
        sdk_client.device_registration_state.query(id=enrollment_group_id)

    def test_device_registration_state_query_error(
        self, service_client_query_error, sdk_client
    ):
        with pytest.raises(HttpResponseError):
            sdk_client.device_registration_state.query(id=enrollment_group_id)
