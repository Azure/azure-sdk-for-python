import json
import re

import pytest
from azure.core.exceptions import HttpResponseError
from tests.conftest import (
    REPROVISION_MIGRATE,
    REPROVISION_NEVER,
    REPROVISION_RESET,
    mock_dps_target,
)
from tests.utility.common import create_random_name, generate_enrollment

endpoint = mock_dps_target["endpoint"]
enrollment_endpoint = "{}/enrollments".format(endpoint)

enrollment_url = re.compile("{}/.+".format(enrollment_endpoint))
query_url = "{}/query?".format(enrollment_endpoint)
attestation_url = re.compile("{}/.+/attestationmechanism".format(enrollment_endpoint))

enrollment_list = [
    (generate_enrollment(attestation_type="tpm", endorsement_key="mykey")),
    (
        generate_enrollment(
            attestation_type="tpm",
            endorsement_key="mykey",
            device_id="1",
            iot_hub_host_name="myHub",
            provisioning_status="disabled",
        )
    ),
    (
        generate_enrollment(
            attestation_type="tpm",
            endorsement_key="mykey",
            provisioning_status="enabled",
            initial_twin_properties={"key": "value"},
        )
    ),
    (
        generate_enrollment(
            attestation_type="x509",
            primary_cert="myCert",
        )
    ),
    (
        generate_enrollment(
            attestation_type="x509",
            secondary_cert="myCert2",
        )
    ),
    (
        generate_enrollment(
            attestation_type="x509",
            primary_cert="myCert",
            device_id="1",
            iot_hub_host_name="myHub",
            provisioning_status="disabled",
        )
    ),
    (
        generate_enrollment(
            attestation_type="x509",
            primary_cert="myCert",
            provisioning_status="enabled",
            initial_twin_properties={"key": "value"},
        )
    ),
    (generate_enrollment(attestation_type="symmetricKey")),
    (
        generate_enrollment(
            attestation_type="symmetricKey",
            primary_key="primarykey",
            secondary_key="secondarykey",
        )
    ),
    (
        generate_enrollment(
            attestation_type="tpm",
            endorsement_key="mykey",
            reprovision_policy=REPROVISION_MIGRATE,
        )
    ),
    (
        generate_enrollment(
            attestation_type="x509",
            primary_cert="myCert",
            reprovision_policy=REPROVISION_RESET,
        )
    ),
    (
        generate_enrollment(
            attestation_type="symmetricKey",
            primary_key="primarykey",
            secondary_key="secondarykey",
            reprovision_policy=REPROVISION_NEVER,
        )
    ),
    (
        generate_enrollment(
            attestation_type="symmetricKey",
            primary_key="primarykey",
            secondary_key="secondarykey",
            reprovision_policy=REPROVISION_NEVER,
            allocation_policy="static",
            iot_hubs=["hub1"],
        )
    ),
    (
        generate_enrollment(
            attestation_type="symmetricKey",
            primary_key="primarykey",
            secondary_key="secondarykey",
            reprovision_policy=REPROVISION_NEVER,
            allocation_policy="hashed",
            iot_hubs=["hub1", "hub2"],
        )
    ),
    (
        generate_enrollment(
            attestation_type="symmetricKey",
            primary_key="primarykey",
            secondary_key="secondarykey",
            reprovision_policy=REPROVISION_NEVER,
            allocation_policy="geoLatency",
        )
    ),
    (
        generate_enrollment(
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
        generate_enrollment(
            attestation_type="symmetricKey",
            primary_key="primarykey",
            secondary_key="secondarykey",
        )
    ),
    (
        generate_enrollment(
            attestation_type="symmetricKey",
            primary_key="primarykey",
            secondary_key="secondarykey",
            initial_twin_properties={"key": ["value1", "value2"]},
        )
    ),
    (
        generate_enrollment(
            attestation_type="tpm",
            endorsement_key="mykey",
            provisioning_status="enabled",
            initial_twin_properties={"key": ["value1", "value2"]},
        )
    ),
]


class TestIndividualEnrollmentGet(object):
    @pytest.fixture()
    def service_client_get(self, mocked_response):
        mocked_response.get(
            url=enrollment_url,
            body=json.dumps({"registrationId": "enrollment1"}),
            status=200,
            content_type="application/json",
            match_querystring=False,
        )

    @pytest.fixture(params=[404, 500])
    def service_client_get_error(self, mocked_response, request):
        mocked_response.get(
            url=enrollment_url,
            body="{}",
            status=request.param,
            content_type="application/json",
            match_querystring=False,
        )

    def test_individual_enrollment_get(self, service_client_get, sdk_client):
        enrollment_id = create_random_name()
        sdk_client.individual_enrollment.get(id=enrollment_id)

    def test_individual_enrollment_get_error(
        self, service_client_get_error, sdk_client
    ):
        with pytest.raises(HttpResponseError):
            sdk_client.individual_enrollment.get(id=create_random_name())


class TestIndividualEnrollmentCreate(object):
    @pytest.fixture()
    def service_client(self, mocked_response):
        mocked_response.put(
            url=enrollment_url,
            body="{}",
            status=200,
            content_type="application/json",
            match_querystring=False,
        )
        yield mocked_response

    @pytest.fixture(params=[400, 401, 500])
    def service_client_generic_error(self, mocked_response, request):
        mocked_response.put(
            url=enrollment_url,
            body="{}",
            status=request.param,
            content_type="application/json",
            match_querystring=False,
        )
        yield mocked_response

    @pytest.mark.parametrize("enrollment", enrollment_list)
    def test_individual_enrollment_create_or_update(
        self, service_client, sdk_client, enrollment
    ):
        enrollment_id = create_random_name()
        sdk_client.individual_enrollment.create_or_update(
            id=enrollment_id, enrollment=enrollment
        )

    @pytest.mark.parametrize("enrollment", enrollment_list[:3])
    def test_individual_enrollment_create_or_update_error(
        self, service_client_generic_error, sdk_client, enrollment
    ):
        enrollment_id = create_random_name()
        with pytest.raises(HttpResponseError):
            sdk_client.individual_enrollment.create_or_update(
                id=enrollment_id, enrollment=enrollment
            )


class TestIndividualEnrollmentDelete(object):
    @pytest.fixture()
    def service_client(self, mocked_response):
        mocked_response.delete(
            url=enrollment_url,
            body="{}",
            status=204,
            content_type="application/json",
            match_querystring=False,
        )
        yield mocked_response

    @pytest.fixture(params=[400, 404, 500])
    def service_client_error(self, mocked_response, request):
        mocked_response.delete(
            url=enrollment_url,
            body="{}",
            status=request.param,
            content_type="application/json",
            match_querystring=False,
        )
        yield mocked_response

    def test_individual_enrollment_delete(self, service_client, sdk_client):
        enrollment_id = create_random_name()
        sdk_client.individual_enrollment.delete(id=enrollment_id)

    def test_individual_enrollment_delete_error(self, service_client_error, sdk_client):
        enrollment_id = create_random_name()
        with pytest.raises(HttpResponseError):
            sdk_client.individual_enrollment.delete(id=enrollment_id)


class TestIndividualEnrollmentQuery(object):
    @pytest.fixture()
    def service_client(self, mocked_response):
        mocked_response.post(
            url=query_url,
            body=json.dumps([{"registration_id": create_random_name()}]),
            status=200,
            content_type="application/json",
            match_querystring=False,
        )
        yield mocked_response

    @pytest.fixture(params=[400, 401, 500])
    def service_client_generic_error(self, mocked_response, request):
        mocked_response.post(
            url=query_url,
            body=json.dumps([{"registration_id": create_random_name()}]),
            status=request.param,
            content_type="application/json",
            match_querystring=False,
        )
        yield mocked_response

    @pytest.mark.parametrize("query", "select *")
    def test_individual_enrollment_query(self, service_client, sdk_client, query):
        sdk_client.individual_enrollment.query(query_specification=query)

    def test_individual_enrollment_query_error(
        self, service_client_generic_error, sdk_client
    ):
        with pytest.raises(HttpResponseError):
            sdk_client.individual_enrollment.query(query_specification="select *")


class TestIndividualEnrollmentAttestation(object):
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

    def test_individual_enrollment_get_attestation_mechanism(
        self, service_client, sdk_client
    ):
        enrollment_id = create_random_name()
        sdk_client.individual_enrollment.get_attestation_mechanism(id=enrollment_id)

    def test_individual_enrollment_get_attestation_mechanism_error(
        self, service_client_generic_error, sdk_client
    ):
        enrollment_id = create_random_name()
        with pytest.raises(HttpResponseError):
            sdk_client.individual_enrollment.get_attestation_mechanism(id=enrollment_id)


class TestIndividualEnrollmentBulk(object):
    @pytest.fixture()
    def service_client(self, mocked_response):
        mocked_response.post(
            url=enrollment_endpoint,
            body="{}",
            status=200,
            content_type="application/json",
            match_querystring=False,
        )
        yield mocked_response

    @pytest.fixture(params=[400, 401, 500])
    def service_client_generic_error(self, mocked_response, request):
        mocked_response.post(
            url=enrollment_endpoint,
            body="",
            status=request.param,
            content_type="application/json",
            match_querystring=False,
        )
        yield mocked_response

    @pytest.mark.parametrize(
        "enrollments, mode",
        [
            (enrollment_list, "create"),
            (
                enrollment_list,
                "update",
            ),
            (enrollment_list, "updateIfMatchETag"),
            (enrollment_list, "delete"),
        ],
    )
    def test_individual_enrollment_run_bulk_operation(
        self, service_client, sdk_client, enrollments, mode
    ):
        sdk_client.individual_enrollment.run_bulk_operation(
            bulk_operation={"enrollments": enrollments, "mode": mode}
        )

    @pytest.mark.parametrize(
        "enrollments, mode",
        [
            (enrollment_list, "create"),
            (
                enrollment_list,
                "update",
            ),
            (enrollment_list, "updateIfMatchETag"),
            (enrollment_list, "delete"),
        ],
    )
    def test_individual_enrollment_run_bulk_operation_error(
        self, service_client_generic_error, sdk_client, enrollments, mode
    ):
        with pytest.raises(HttpResponseError):
            sdk_client.individual_enrollment.run_bulk_operation(
                bulk_operation={"enrollments": enrollments, "mode": mode}
            )
