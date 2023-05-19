import json
import re

import pytest
from azure.core.exceptions import HttpResponseError
from conftest import (
    REPROVISION_MIGRATE,
    REPROVISION_NEVER,
    REPROVISION_RESET,
    mock_dps_target,
)
from utility.common import generate_enrollment_group

endpoint = mock_dps_target["endpoint"]
enrollment_group_endpoint = "{}/enrollmentGroups".format(endpoint)

enrollment_group_url = re.compile("{}/.+".format(enrollment_group_endpoint))
query_url = "{}/query?".format(enrollment_group_endpoint)
enrollment_group_id = "test_enrollment_group_id"
attestation_url = "{}/{}/attestationmechanism".format(
    enrollment_group_endpoint, enrollment_group_id
)


enrollment_group_list = [
    (generate_enrollment_group(attestation_type="tpm", endorsement_key="mykey")),
    (
        generate_enrollment_group(
            attestation_type="tpm",
            endorsement_key="mykey",
            iot_hub_host_name="myHub",
            provisioning_status="disabled",
        )
    ),
    (
        generate_enrollment_group(
            attestation_type="tpm",
            endorsement_key="mykey",
            provisioning_status="enabled",
            initial_twin_properties={"key": "value"},
        )
    ),
    (generate_enrollment_group(attestation_type="x509", primary_cert="myCert")),
    (generate_enrollment_group(attestation_type="x509", secondary_cert="myCert2")),
    (
        generate_enrollment_group(
            attestation_type="x509",
            primary_cert="myCert",
            iot_hub_host_name="myHub",
            provisioning_status="disabled",
        )
    ),
    (
        generate_enrollment_group(
            attestation_type="x509",
            primary_cert="myCert",
            provisioning_status="enabled",
            initial_twin_properties={"key": "value"},
        )
    ),
    (generate_enrollment_group(attestation_type="symmetricKey")),
    (
        generate_enrollment_group(
            attestation_type="symmetricKey",
            primary_key="primarykey",
            secondary_key="secondarykey",
        )
    ),
    (
        generate_enrollment_group(
            attestation_type="tpm",
            endorsement_key="mykey",
            reprovision_policy=REPROVISION_MIGRATE,
        )
    ),
    (
        generate_enrollment_group(
            attestation_type="x509",
            primary_cert="myCert",
            reprovision_policy=REPROVISION_RESET,
        )
    ),
    (
        generate_enrollment_group(
            attestation_type="symmetricKey",
            primary_key="primarykey",
            secondary_key="secondarykey",
            reprovision_policy=REPROVISION_NEVER,
        )
    ),
    (
        generate_enrollment_group(
            attestation_type="symmetricKey",
            primary_key="primarykey",
            secondary_key="secondarykey",
            reprovision_policy=REPROVISION_NEVER,
            allocation_policy="static",
            iot_hubs=["hub1"],
        )
    ),
    (
        generate_enrollment_group(
            attestation_type="symmetricKey",
            primary_key="primarykey",
            secondary_key="secondarykey",
            reprovision_policy=REPROVISION_NEVER,
            allocation_policy="hashed",
            iot_hubs=["hub1", "hub2"],
        )
    ),
    (
        generate_enrollment_group(
            attestation_type="symmetricKey",
            primary_key="primarykey",
            secondary_key="secondarykey",
            reprovision_policy=REPROVISION_NEVER,
            allocation_policy="geoLatency",
        )
    ),
    (
        generate_enrollment_group(
            attestation_type="symmetricKey",
            primary_key="primarykey",
            secondary_key="secondarykey",
            reprovision_policy=REPROVISION_NEVER,
            allocation_policy="custom",
            webhook_url="https://www.test.test",
            api_version="2019-03-31",
        )
    ),
    (
        generate_enrollment_group(
            attestation_type="symmetricKey",
            primary_key="primarykey",
            secondary_key="secondarykey",
        )
    ),
    (
        generate_enrollment_group(
            attestation_type="symmetricKey",
            primary_key="primarykey",
            secondary_key="secondarykey",
            initial_twin_properties={"key": ["value1", "value2"]},
        )
    ),
    (
        generate_enrollment_group(
            attestation_type="tpm",
            endorsement_key="mykey",
            provisioning_status="enabled",
            initial_twin_properties={"key": ["value1", "value2"]},
        )
    ),
]


class TestGroupEnrollmentGet(object):
    @pytest.fixture()
    def service_client_get(self, mocked_response):
        mocked_response.get(
            url=enrollment_group_url,
            body=json.dumps({"registrationId": "enrollment1"}),
            status=200,
            content_type="application/json",
            match_querystring=False,
        )

    @pytest.fixture(params=[404, 500])
    def service_client_get_error(self, mocked_response, request):
        mocked_response.get(
            url=enrollment_group_url,
            body="{}",
            status=request.param,
            content_type="application/json",
            match_querystring=False,
        )

    @pytest.mark.parametrize(
        "id, expected", [(enrollment_group_id, {"registrationId": enrollment_group_id})]
    )
    def test_group_enrollment_get(self, service_client_get, sdk_client, id, expected):
        sdk_client.enrollment_group.get(id=id)

    def test_group_enrollment_get_error(self, service_client_get_error, sdk_client):
        with pytest.raises(HttpResponseError):
            sdk_client.enrollment_group.get(id=enrollment_group_id)


class TestGroupEnrollmentCreate(object):
    @pytest.fixture()
    def service_client(self, mocked_response):
        mocked_response.put(
            url=enrollment_group_url,
            body="{}",
            status=200,
            content_type="application/json",
            match_querystring=False,
        )
        yield mocked_response

    @pytest.fixture(params=[400, 401, 500])
    def service_client_generic_error(self, mocked_response, request):
        mocked_response.put(
            url=enrollment_group_url,
            body="{}",
            status=request.param,
            content_type="application/json",
            match_querystring=False,
        )
        yield mocked_response

    @pytest.mark.parametrize("enrollment_group", enrollment_group_list)
    def test_group_enrollment_create_or_update(
        self, service_client, sdk_client, enrollment_group
    ):
        sdk_client.enrollment_group.create_or_update(
            id=enrollment_group_id, enrollment_group=enrollment_group
        )

    @pytest.mark.parametrize("enrollment_group", enrollment_group_list[:3])
    def test_group_enrollment_create_or_update_error(
        self, service_client_generic_error, sdk_client, enrollment_group
    ):
        with pytest.raises(HttpResponseError):
            sdk_client.enrollment_group.create_or_update(
                id=enrollment_group_id, enrollment_group=enrollment_group
            )


class TestGroupEnrollmentDelete(object):
    @pytest.fixture()
    def service_client(self, mocked_response):
        mocked_response.delete(
            url=enrollment_group_url,
            body="{}",
            status=204,
            content_type="application/json",
            match_querystring=False,
        )
        yield mocked_response

    @pytest.fixture(params=[400, 404, 500])
    def service_client_error(self, mocked_response, request):
        mocked_response.delete(
            url=enrollment_group_url,
            body="{}",
            status=request.param,
            content_type="application/json",
            match_querystring=False,
        )
        yield mocked_response

    def test_group_enrollment_delete(self, service_client, sdk_client):
        sdk_client.enrollment_group.delete(id=enrollment_group_id)

    def test_group_enrollment_delete_error(self, service_client_error, sdk_client):
        with pytest.raises(HttpResponseError):
            sdk_client.enrollment_group.delete(id=enrollment_group_id)


class TestGroupEnrollmentQuery(object):
    @pytest.fixture()
    def service_client(self, mocked_response):
        mocked_response.post(
            url=query_url,
            body=json.dumps([{"registration_id": enrollment_group_id}]),
            status=200,
            content_type="application/json",
            match_querystring=False,
        )
        yield mocked_response

    @pytest.fixture(params=[400, 401, 500])
    def service_client_generic_error(self, mocked_response, request):
        mocked_response.post(
            url=query_url,
            body=json.dumps([{"registration_id": enrollment_group_id}]),
            status=request.param,
            content_type="application/json",
            match_querystring=False,
        )
        yield mocked_response

    @pytest.mark.parametrize("query", "select *")
    def test_group_enrollment_query(self, service_client, sdk_client, query):
        query = sdk_client.enrollment_group.query(query_specification=query)
        assert [enrollment for enrollment in query]

    def test_group_enrollment_query_error(
        self, service_client_generic_error, sdk_client
    ):
        with pytest.raises(HttpResponseError):
            query = sdk_client.enrollment_group.query(query_specification="select *")
            assert [enrollment for enrollment in query]


class TestGroupEnrollmentAttestation(object):
    @pytest.fixture()
    def service_client(self, mocked_response):
        mocked_response.post(
            url=attestation_url,
            body="{}",
            status=200,
            content_type="application/json",
            match_querystring=False,
        )
        yield mocked_response

    @pytest.fixture(params=[400, 401, 500])
    def service_client_generic_error(self, mocked_response, request):
        mocked_response.post(
            url=attestation_url,
            body="{}",
            status=request.param,
            content_type="application/json",
            match_querystring=False,
        )
        yield mocked_response

    def test_group_enrollment_get_attestation_mechanism(
        self, service_client, sdk_client
    ):
        sdk_client.enrollment_group.get_attestation_mechanism(id=enrollment_group_id)

    def test_group_enrollment_get_attestation_mechanism_error(
        self, service_client_generic_error, sdk_client
    ):
        with pytest.raises(HttpResponseError):
            sdk_client.enrollment_group.get_attestation_mechanism(
                id=enrollment_group_id
            )


class TestGroupEnrollmentBulk(object):
    @pytest.fixture()
    def service_client(self, mocked_response):
        mocked_response.post(
            url=enrollment_group_endpoint,
            body="{}",
            status=200,
            content_type="application/json",
            match_querystring=False,
        )
        yield mocked_response

    @pytest.fixture(params=[400, 401, 500])
    def service_client_generic_error(self, mocked_response, request):
        mocked_response.post(
            url=enrollment_group_endpoint,
            body="",
            status=request.param,
            content_type="application/json",
            match_querystring=False,
        )
        yield mocked_response

    @pytest.mark.parametrize(
        "groups, mode",
        [
            (enrollment_group_list, "create"),
            (
                enrollment_group_list,
                "update",
            ),
            (
                enrollment_group_list,
                "updateIfMatchETag",
            ),
            (enrollment_group_list, "delete"),
        ],
    )
    def test_group_enrollment_run_bulk_operation(
        self, service_client, groups, mode, sdk_client
    ):
        sdk_client.enrollment_group.run_bulk_operation(
            bulk_operation={"enrollment_groups": groups, "mode": mode}
        )

    @pytest.mark.parametrize(
        "groups, mode",
        [
            (enrollment_group_list, "create"),
            (
                enrollment_group_list,
                "update",
            ),
            (
                enrollment_group_list,
                "updateIfMatchETag",
            ),
            (enrollment_group_list, "delete"),
        ],
    )
    def test_group_enrollment_run_bulk_operation_error(
        self, service_client_generic_error, sdk_client, groups, mode
    ):
        with pytest.raises(HttpResponseError):
            sdk_client.enrollment_group.run_bulk_operation(
                bulk_operation={"enrollment_groups": groups, "mode": mode}
            )
