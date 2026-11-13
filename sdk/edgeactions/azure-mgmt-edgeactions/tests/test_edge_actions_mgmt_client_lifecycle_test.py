# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Recordable service scenarios adapted from the Azure PowerShell EdgeAction tests."""

import base64
import io
import zipfile
from contextlib import contextmanager
from urllib.parse import parse_qsl, urlsplit

import pytest
from azure.core.exceptions import HttpResponseError, ResourceNotFoundError
from azure.core.rest import HttpRequest
from azure.mgmt.edgeactions import EdgeActionsMgmtClient, models
from devtools_testutils import AzureMgmtRecordedTestCase, RandomNameResourceGroupPreparer, recorded_by_proxy

from edgeactions_test_settings import RESOURCE_GROUP_OPTIONS
from spec_validation import response_spec

pytestmark = pytest.mark.usefixtures("add_sanitizers")

HANDLER = b"function handler(event) { return event; }"


def response_url_key(url):
    parsed = urlsplit(url)
    # The playback proxy rewrites hosts, but preserves ARM paths and query parameters.
    return parsed.path.lower(), sorted(parse_qsl(parsed.query))


def complete_lro(client, operation, *args, result_type, **kwargs):
    responses = []
    poller = operation(*args, raw_response_hook=responses.append, **kwargs)
    result = poller.result()
    assert poller.done()
    assert poller.status() == "Succeeded"
    assert responses, "The operation must expose its HTTP responses"
    initial = responses[0].http_response
    request = responses[0].http_request
    final = responses[-1].http_response
    final_schema_validated = False
    if initial.status_code in (201, 202):
        spec = response_spec()
        if initial.status_code == 202:
            spec.validate_response(
                spec.operation(request.method, request.url),
                initial.status_code,
                initial.json() if initial.content else None,
                initial.headers,
                body_present=bool(initial.content),
            )
        status_url = initial.headers.get("Azure-AsyncOperation")
        location = initial.headers.get("Location")
        if initial.status_code == 202:
            assert status_url or location, "An accepted operation must provide a polling header"
        for header, url in (("Azure-AsyncOperation", status_url), ("Location", location)):
            if url:
                assert urlsplit(url).scheme == "https" and urlsplit(url).netloc, f"{header} must be an HTTPS URL"
        status_responses = []
        if status_url:
            if location:
                assert response_url_key(status_url) != response_url_key(location)
            status_responses = [
                (index, item.http_response)
                for index, item in enumerate(responses[1:], start=1)
                if response_url_key(item.http_request.url) == response_url_key(status_url)
            ]
            if initial.status_code == 202:
                assert status_responses, "The Azure-AsyncOperation endpoint must be polled"
            statuses = [
                spec.validate_status_response(item.status_code, item.json() if item.content else None)
                for _, item in status_responses
            ]
            assert all(status not in ("Succeeded", "Failed", "Canceled") for status in statuses[:-1])
            if statuses:
                assert statuses[-1] == "Succeeded"
        # PUT's 201 Location identifies the created resource, not a declared final-result endpoint.
        if initial.status_code == 202 and location:
            location_responses = [
                (index, item.http_response)
                for index, item in enumerate(responses[1:], start=1)
                if response_url_key(item.http_request.url) == response_url_key(location)
            ]
            if location_responses and status_responses:
                assert (
                    location_responses[-1][0] > status_responses[-1][0]
                ), "Location must be read after the operation reports Succeeded"
            # ARM polling may return the original resource for PATCH or skip the final GET for DELETE.
            # Validate the advertised final endpoint even when the SDK does not consume its body.
            final = (
                location_responses[-1][1] if location_responses else client.send_request(HttpRequest("GET", location))
            )
            spec.validate_location(
                request.method,
                request.url,
                location,
                final.status_code,
                final.json() if final.content else None,
                final.headers,
                body_present=bool(final.content),
                allow_known_swap_default_response=True,
            )
            final_schema_validated = True

    if result_type is None:
        assert result is None
        if initial.status_code != 202:
            assert final.status_code in (200, 204)
            assert not final.content, "A synchronous no-content operation must not return a response body"
    else:
        assert isinstance(result, result_type)
        body = final.json() if final.content else None
        if not final_schema_validated:
            spec = response_spec()
            spec.validate_response(
                spec.operation(request.method, request.url),
                final.status_code,
                body,
                final.headers,
                body_present=bool(final.content),
                allow_known_null_validation_status=True,
            )
        required = (
            {"name", "content"}
            if result_type is models.VersionCode
            else {"id", "name", "type", "location", "properties"}
        )
        assert (
            isinstance(body, dict) and required <= body.keys()
        ), "The final response must contain the expected result, not an operation-status document"
        assert result.as_dict() == result_type(body).as_dict()
    return result


def assert_resource_result(result, model, resource_group_name, resource_path):
    resource_types = {
        models.EdgeAction: "Microsoft.Cdn/edgeActions",
        models.EdgeActionVersion: "Microsoft.Cdn/edgeActions/versions",
        models.EdgeActionExecutionFilter: "Microsoft.Cdn/edgeActions/executionFilters",
    }
    assert isinstance(result, model)
    expected_path = f"/resourceGroups/{resource_group_name}/providers/Microsoft.Cdn/edgeActions/{resource_path}"
    assert result.id.lower().endswith(expected_path.lower())
    assert result.name == resource_path.rsplit("/", 1)[-1]
    assert result.type.lower() == resource_types[model].lower()
    assert result.location == "global"
    assert result.properties.provisioning_state == "Succeeded"


def version_code(deployment_type):
    content = HANDLER
    if deployment_type == "zip":
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w") as archive:
            info = zipfile.ZipInfo("handler.js", date_time=(1980, 1, 1, 0, 0, 0))
            # Match the recorded Windows creator metadata on every platform.
            info.create_system = 0
            archive.writestr(info, HANDLER)
        content = buffer.getvalue()
    return base64.b64encode(content).decode()


def cleanup_edge_action(client, resource_group_name, name):
    try:
        client.edge_actions.get(resource_group_name, name)
    except ResourceNotFoundError:
        return
    filters = client.edge_action_execution_filters
    for item in filters.list_by_edge_action(resource_group_name, name):
        complete_lro(client, filters.begin_delete, resource_group_name, name, item.name, result_type=None)
    versions = list(client.edge_action_versions.list_by_edge_action(resource_group_name, name))
    assert all(version.properties.is_default_version in ("True", "False") for version in versions)
    assert sum(version.properties.is_default_version == "True" for version in versions) <= 1
    # A default version can be deleted only after the other versions.
    for version in sorted(versions, key=lambda item: item.properties.is_default_version == "True"):
        complete_lro(
            client, client.edge_action_versions.begin_delete, resource_group_name, name, version.name, result_type=None
        )
    complete_lro(client, client.edge_actions.begin_delete, resource_group_name, name, result_type=None)


class TestEdgeActionsLifecycle(AzureMgmtRecordedTestCase):
    @contextmanager
    def edge_action(self, resource_group_name):
        name = self.get_resource_name("eapython")
        with self.create_mgmt_client(EdgeActionsMgmtClient) as client:
            try:
                client.edge_actions.get(resource_group_name, name)
            except ResourceNotFoundError:
                pass
            else:
                pytest.fail(f"Refusing to overwrite existing EdgeAction {resource_group_name}/{name}")
            try:
                created = complete_lro(
                    client,
                    client.edge_actions.begin_create,
                    resource_group_name,
                    name,
                    models.EdgeAction(
                        location="global",
                        sku=models.SkuType(name="Standard", tier="Standard"),
                        tags={"purpose": "initial", "remove-me": "initial"},
                    ),
                    result_type=models.EdgeAction,
                )
                assert_resource_result(created, models.EdgeAction, resource_group_name, name)
                assert created.sku == models.SkuType(name="Standard", tier="Standard")
                assert created.tags == {"purpose": "initial", "remove-me": "initial"}
                assert created.properties.attachments == []
                yield client, name
            finally:
                cleanup_edge_action(client, resource_group_name, name)

    @RandomNameResourceGroupPreparer(**RESOURCE_GROUP_OPTIONS)
    @recorded_by_proxy
    def test_edge_action_tag_updates(self, resource_group):
        rg = resource_group.name
        with self.edge_action(rg) as (client, name):
            before = client.edge_actions.get(rg, name)
            assert before.location == "global"
            assert before.tags == {"purpose": "initial", "remove-me": "initial"}
            assert name in [action.name for action in client.edge_actions.list_by_resource_group(rg)]

            with pytest.raises(
                HttpResponseError, match="PATCH request body must contain at least one property"
            ) as error:
                client.edge_actions.begin_update(rg, name, models.EdgeActionUpdate()).result()
            assert error.value.status_code == 400
            assert client.edge_actions.get(rg, name).tags == before.tags

            for tags in ({"purpose": "updated"}, {}):
                result = complete_lro(
                    client,
                    client.edge_actions.begin_update,
                    rg,
                    name,
                    models.EdgeActionUpdate(tags=tags),
                    result_type=models.EdgeAction,
                )
                assert_resource_result(result, models.EdgeAction, rg, name)
                assert result.tags == tags
                assert result.sku == before.sku
                updated = client.edge_actions.get(rg, name)
                assert result == updated
                assert updated.tags == tags
                assert updated.location == before.location
                assert updated.sku == before.sku

            for invalid_update in (
                {"tags": None},
                {"sku": None},
                {"sku": {"name": before.sku.name, "tier": before.sku.tier}},
            ):
                with pytest.raises(HttpResponseError) as error:
                    client.edge_actions.begin_update(rg, name, invalid_update).result()
                assert error.value.status_code == 400
            assert client.edge_actions.get(rg, name).tags == {}

        with pytest.raises(ResourceNotFoundError):
            with self.create_mgmt_client(EdgeActionsMgmtClient) as client:
                client.edge_actions.get(rg, name)

    @RandomNameResourceGroupPreparer(**RESOURCE_GROUP_OPTIONS)
    @recorded_by_proxy
    def test_file_versions_and_execution_filters(self, resource_group):
        self.versions_and_execution_filters(resource_group, "file")

    @RandomNameResourceGroupPreparer(**RESOURCE_GROUP_OPTIONS)
    @recorded_by_proxy
    def test_zip_versions_and_execution_filters(self, resource_group):
        self.versions_and_execution_filters(resource_group, "zip")

    def versions_and_execution_filters(self, resource_group, deployment_type):
        rg = resource_group.name
        with self.edge_action(rg) as (client, name):
            versions = client.edge_action_versions
            for version in ("v1", "v2"):
                created = complete_lro(
                    client,
                    versions.begin_create,
                    rg,
                    name,
                    version,
                    models.EdgeActionVersion(
                        location="global",
                        properties=models.EdgeActionVersionProperties(
                            deployment_type=deployment_type, is_default_version="False"
                        ),
                    ),
                    result_type=models.EdgeActionVersion,
                )
                assert_resource_result(created, models.EdgeActionVersion, rg, f"{name}/versions/{version}")
                assert created.properties.deployment_type == deployment_type
                assert created.properties.is_default_version == ("True" if version == "v1" else "False")
                result = complete_lro(
                    client,
                    versions.begin_deploy_version_code,
                    rg,
                    name,
                    version,
                    models.VersionCode(name=version, content=version_code(deployment_type)),
                    result_type=models.EdgeActionVersion,
                )
                assert_resource_result(result, models.EdgeActionVersion, rg, f"{name}/versions/{version}")
                assert result.properties.deployment_type == deployment_type
                assert result.properties.validation_status == "Succeeded"
                assert result.properties.is_default_version == created.properties.is_default_version
                deployed = versions.get(rg, name, version)
                assert result == deployed
                assert deployed.properties.provisioning_state == "Succeeded"
                assert deployed.properties.validation_status == "Succeeded"
                assert deployed.properties.deployment_type == deployment_type

            first = versions.get(rg, name, "v1")
            second = versions.get(rg, name, "v2")
            assert first.properties.is_default_version == "True"
            assert second.properties.is_default_version == "False"
            assert {version.name for version in versions.list_by_edge_action(rg, name)} == {"v1", "v2"}

            code = complete_lro(client, versions.begin_get_version_code, rg, name, "v1", result_type=models.VersionCode)
            assert isinstance(code.name, str) and code.name
            assert isinstance(code.content, str) and code.content
            decoded = base64.b64decode(code.content)
            # The service may return a ZIP package even for a file deployment.
            if zipfile.is_zipfile(io.BytesIO(decoded)):
                with zipfile.ZipFile(io.BytesIO(decoded)) as archive:
                    assert HANDLER in [archive.read(item) for item in archive.infolist() if not item.is_dir()]
            else:
                assert decoded == HANDLER

            result = complete_lro(
                client,
                versions.begin_update,
                rg,
                name,
                "v1",
                models.EdgeActionVersionUpdate(tags={"purpose": "updated"}),
                result_type=models.EdgeActionVersion,
            )
            assert_resource_result(result, models.EdgeActionVersion, rg, f"{name}/versions/v1")
            assert result.tags == {"purpose": "updated"}
            assert result.properties.deployment_type == deployment_type
            assert result.properties.is_default_version == "True"
            updated = versions.get(rg, name, "v1")
            assert result == updated
            assert updated.tags == {"purpose": "updated"}
            assert updated.properties.deployment_type == first.properties.deployment_type
            assert updated.properties.is_default_version == first.properties.is_default_version

            result = complete_lro(
                client,
                versions.begin_update,
                rg,
                name,
                "v1",
                models.EdgeActionVersionUpdate(
                    properties=models.EdgeActionVersionUpdateProperties(
                        deployment_type=deployment_type, is_default_version="True"
                    )
                ),
                result_type=models.EdgeActionVersion,
            )
            assert_resource_result(result, models.EdgeActionVersion, rg, f"{name}/versions/v1")
            assert result == updated
            for properties in (
                {"isDefaultVersion": "False"},
                {"deploymentType": "zip" if deployment_type == "file" else "file"},
            ):
                with pytest.raises(HttpResponseError) as error:
                    versions.begin_update(rg, name, "v1", {"properties": properties}).result()
                assert error.value.status_code == 400

            assert complete_lro(client, versions.begin_swap_default, rg, name, "v2", result_type=None) is None
            assert versions.get(rg, name, "v1").properties.is_default_version == "False"
            assert versions.get(rg, name, "v2").properties.is_default_version == "True"

            filters = client.edge_action_execution_filters
            result = complete_lro(
                client,
                filters.begin_create,
                rg,
                name,
                "sdkfilter",
                models.EdgeActionExecutionFilter(
                    location="global",
                    properties=models.EdgeActionExecutionFilterProperties(
                        version_id=first.id,
                        execution_filter_identifier_header_name="x-sdk-test",
                        execution_filter_identifier_header_value="initial",
                    ),
                ),
                result_type=models.EdgeActionExecutionFilter,
            )
            assert_resource_result(result, models.EdgeActionExecutionFilter, rg, f"{name}/executionFilters/sdkfilter")
            assert result.properties.version_id.lower() == first.id.lower()
            assert result.properties.execution_filter_identifier_header_name == "x-sdk-test"
            assert result.properties.execution_filter_identifier_header_value == "initial"
            initial_filter = filters.get(rg, name, "sdkfilter")
            assert result == initial_filter
            assert initial_filter.properties.version_id.lower() == first.id.lower()
            assert {item.name for item in filters.list_by_edge_action(rg, name)} == {"sdkfilter"}

            result = complete_lro(
                client,
                filters.begin_update,
                rg,
                name,
                "sdkfilter",
                models.EdgeActionExecutionFilterUpdate(
                    tags={"purpose": "updated"},
                    properties=models.EdgeActionExecutionFilterUpdateProperties(
                        version_id=second.id,
                        execution_filter_identifier_header_name="x-sdk-test-updated",
                        execution_filter_identifier_header_value="updated",
                    ),
                ),
                result_type=models.EdgeActionExecutionFilter,
            )
            assert_resource_result(result, models.EdgeActionExecutionFilter, rg, f"{name}/executionFilters/sdkfilter")
            assert result.tags == {"purpose": "updated"}
            assert result.properties.version_id.lower() == second.id.lower()
            assert result.properties.execution_filter_identifier_header_name == "x-sdk-test-updated"
            assert result.properties.execution_filter_identifier_header_value == "updated"
            updated_filter = filters.get(rg, name, "sdkfilter")
            assert result == updated_filter
            assert updated_filter.tags == {"purpose": "updated"}
            assert updated_filter.properties.version_id.lower() == second.id.lower()
            assert updated_filter.properties.execution_filter_identifier_header_name == "x-sdk-test-updated"
            assert updated_filter.properties.execution_filter_identifier_header_value == "updated"

            assert complete_lro(client, filters.begin_delete, rg, name, "sdkfilter", result_type=None) is None
            assert list(filters.list_by_edge_action(rg, name)) == []
            for version in ("v1", "v2"):
                assert complete_lro(client, versions.begin_delete, rg, name, version, result_type=None) is None
            assert list(versions.list_by_edge_action(rg, name)) == []
