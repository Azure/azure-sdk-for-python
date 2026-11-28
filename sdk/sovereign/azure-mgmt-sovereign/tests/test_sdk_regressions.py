import copy
from datetime import datetime, timedelta, timezone
from io import BytesIO
import json
import pickle
import unittest
from urllib.parse import parse_qs, urlsplit

from azure.core.credentials import AccessToken
from azure.core.exceptions import DeserializationError, HttpResponseError
from azure.core.pipeline.transport import AsyncHttpResponse, AsyncHttpTransport, HttpResponse, HttpTransport
from azure.mgmt.sovereign import SovereignMgmtClient, models
from azure.mgmt.sovereign.aio import SovereignMgmtClient as AsyncSovereignMgmtClient


TIMESTAMP = "2026-11-08T20:19:50.7989851+00:00"
JOB = "3192dc72-05d7-4ef2-9111-ea715172390d"


class Credential:
    def get_token(self, *scopes, **kwargs):
        return AccessToken("unit-test", 4102444800)


class AsyncCredential:
    async def get_token(self, *scopes, **kwargs):
        return AccessToken("unit-test", 4102444800)


class Response(HttpResponse):
    def __init__(self, request, status, body, headers=None):
        super().__init__(request, None)
        self.status_code = status
        self.headers = {"content-type": "application/json", **(headers or {})}
        self.reason = "test response"
        self.content_type = "application/json"
        self._body = json.dumps(body).encode()

    def body(self):
        return self._body

    def read(self):
        return self._body

    def json(self):
        return json.loads(self._body)

    def iter_bytes(self):
        yield self._body

    def iter_raw(self):
        yield self._body


class AsyncResponse(Response, AsyncHttpResponse):
    async def read(self):
        return self._body

    async def iter_bytes(self):
        yield self._body

    async def iter_raw(self):
        yield self._body


class Transport(HttpTransport):
    def __init__(self, handler):
        self.handler = handler
        self.requests = []

    def open(self):
        pass

    def close(self):
        pass

    def __exit__(self, *args):
        self.close()

    def send(self, request, **kwargs):
        self.requests.append(request)
        status, body, headers = self.handler(request)
        return Response(request, status, body, headers)


class AsyncTransport(AsyncHttpTransport):
    def __init__(self, handler):
        self.handler = handler
        self.requests = []

    async def open(self):
        pass

    async def close(self):
        pass

    async def __aexit__(self, *args):
        await self.close()

    async def send(self, request, **kwargs):
        self.requests.append(request)
        status, body, headers = self.handler(request)
        return AsyncResponse(request, status, body, headers)


def remediation_handler(final, immediate=False):
    def handle(request):
        if request.method == "POST":
            if immediate:
                return 200, final, {}
            return 202, {"remediationId": JOB}, {
                "azure-asyncoperation": "https://management.azure.com/providers/Microsoft.Sovereign/operations/job",
                "retry-after": "0",
            }
        return 200, final, {}
    return handle


def paging_handler(request):
    if "$skiptoken" not in request.url:
        return 200, {
            "value": [{"id": "/views/one"}],
            "nextLink": "https://management.azure.com/subscriptions/sub/providers/Microsoft.Sovereign/sovereignViews?api-version=2026-10-31-preview&$skiptoken=a%2Bb%2Fc%3D",
        }, {}
    assert parse_qs(urlsplit(request.url).query)["$skiptoken"] == ["a+b/c="]
    return 502, {"error": {"code": "ProviderError", "message": "Service continuation failure"}}, {}


def identity_patch_cases():
    tags = {"sdkValidation": "identity-patch"}
    tags_only = {"tags": tags}
    yield "tags mapping", tags_only, tags_only
    yield "tags model", models.SovereignViewResourcePatch(tags=tags), tags_only
    yield "tags stream", BytesIO(json.dumps(tags_only).encode()), tags_only
    for identity_type in models.SystemAssignedServiceIdentityType:
        expected = {"tags": tags, "identity": {"type": identity_type.value}}
        yield f"{identity_type.value} mapping", copy.deepcopy(expected), expected
        yield f"{identity_type.value} stream", BytesIO(json.dumps(expected).encode()), expected
        for value in [identity_type, identity_type.value]:
            yield f"{identity_type.value} typed {type(value).__name__}", models.SovereignViewResourcePatch(
                tags=tags, identity=models.SystemAssignedServiceIdentity(type=value),
            ), expected
    yield "identity from GET", models.SovereignViewResourcePatch(
        identity=models.SystemAssignedServiceIdentity({
            "type": "SystemAssigned", "principalId": "server-principal", "tenantId": "server-tenant",
        }),
    ), {"identity": {"type": "SystemAssigned"}}


def patch_handler(request):
    return 200, {
        "id": "/subscriptions/sub/resourceGroups/rg/providers/Microsoft.Sovereign/sovereignViews/view",
        "location": "uksouth",
        "identity": {"type": "SystemAssigned", "principalId": "server-principal", "tenantId": "server-tenant"},
        "properties": {"provisioningState": "Succeeded"},
    }, {}


def failed_patch_handler(request):
    if request.method == "PATCH":
        return 202, {}, {
            "azure-asyncoperation": "https://management.azure.com/providers/Microsoft.Sovereign/operationStatuses/patch",
            "location": "https://management.azure.com/providers/Microsoft.Sovereign/operationStatuses/patch",
            "retry-after": "0",
        }
    return 200, {
        "status": "Failed",
        "error": {"code": "SovereignViewPatchManagedIdentityError", "message": "Managed identity backend failed"},
    }, {}


class SnapshotTests(unittest.TestCase):
    def test_nested_response_and_typed_request_preserve_snapshot(self):
        response = models.SovereignViewComplianceDetailsResult({
            "resources": [{"dimensionDetails": [{"evaluatedAt": TIMESTAMP}]}],
        })
        value = response.resources[0].dimension_details[0].evaluated_at
        self.assertIsInstance(value, datetime)
        self.assertEqual(value.microsecond, 798985)
        request = models.SovereignViewComplianceResourceDetailsContent(
            resource_id="/resource", dimension="DataResidency", evaluated_at=value,
        )
        self.assertEqual(request.as_dict()["evaluatedAt"], TIMESTAMP.replace("+00:00", "Z"))
        self.assertEqual(request.evaluated_at.isoformat(), TIMESTAMP.replace("+00:00", "Z").replace("Z", "+00:00"))

    def test_all_evaluation_models_and_mapping_roundtrips(self):
        for cls in [
            models.SovereignViewDimensionDetail, models.SovereignViewComplianceDetail,
            models.SovereignViewComplianceResourceDetailsContent,
            models.SovereignViewComplianceResourceDetailsResult,
        ]:
            with self.subTest(model=cls.__name__):
                result = cls({"evaluatedAt": TIMESTAMP})
                self.assertEqual(result.as_dict()["evaluatedAt"], TIMESTAMP)
                result.evaluated_at = result.evaluated_at
                self.assertEqual(result.as_dict()["evaluatedAt"], TIMESTAMP.replace("+00:00", "Z"))

    def test_precisions_and_offsets(self):
        for fraction in ["", ".1", ".123456", ".1234560", ".0000001", ".123456789"]:
            for offset in ["Z", "+05:30", "-04:00"]:
                wire = "2026-11-08T20:19:50" + fraction + offset
                with self.subTest(wire=wire):
                    value = models.SovereignViewDimensionDetail({"evaluatedAt": wire}).evaluated_at
                    result = models.SovereignViewComplianceResourceDetailsContent(evaluated_at=value).as_dict()["evaluatedAt"]
                    expected = datetime.fromisoformat(wire.replace("Z", "+00:00")).astimezone(timezone.utc)
                    self.assertEqual(datetime.fromisoformat(result.replace("Z", "+00:00")), expected)
                    if len(fraction) > 7:
                        self.assertIn(fraction, result)

    def test_copy_pickle_timezone_and_replace(self):
        value = models.SovereignViewDimensionDetail({"evaluatedAt": TIMESTAMP}).evaluated_at
        for duplicate in [copy.copy(value), copy.deepcopy(value), pickle.loads(pickle.dumps(value))]:
            self.assertEqual(duplicate.isoformat(), TIMESTAMP)
        self.assertIn(".7989851", value.astimezone(timezone(timedelta(hours=5, minutes=30))).isoformat())
        self.assertIn(".7989851", value.replace(second=1).isoformat())
        self.assertNotIn(".7989851", value.replace(microsecond=1).isoformat())
        self.assertEqual(value.isoformat(timespec="microseconds"), TIMESTAMP.replace("9851", "985"))
        self.assertIsInstance(value + timedelta(seconds=1), datetime)

    def test_standard_datetime_optional_and_invalid_values(self):
        for value in [datetime(2026, 1, 1), datetime(2026, 1, 1, tzinfo=timezone.utc)]:
            model = models.SovereignViewComplianceResourceDetailsContent(evaluated_at=value)
            self.assertEqual(model.as_dict()["evaluatedAt"], "2026-01-01T00:00:00Z")
        self.assertIsNone(models.SovereignViewComplianceDetail({}).evaluated_at)
        self.assertIsNone(models.SovereignViewComplianceDetail({"evaluatedAt": None}).evaluated_at)
        with self.assertRaises(ValueError):
            _ = models.SovereignViewDimensionDetail({"evaluatedAt": "not a timestamp"}).evaluated_at


class SyncOperationTests(unittest.TestCase):
    def client(self, final, immediate=False):
        transport = Transport(remediation_handler(final, immediate))
        return SovereignMgmtClient(Credential(), "sub", transport=transport, polling_interval=0), transport

    def test_terminal_operation_envelope(self):
        with self.client({"status": "Succeeded", "properties": {"remediationId": JOB}})[0] as client:
            result = client.sovereign_view_operations.begin_remediate("rg", "view", {}).result()
            self.assertEqual(result.remediation_id, JOB)
            self.assertEqual(result["status"], "Succeeded")

    def test_immediate_flat_response_and_custom_cls(self):
        with self.client({"remediationId": JOB}, immediate=True)[0] as client:
            result = client.sovereign_view_operations.begin_remediate(
                "rg", "view", {}, cls=lambda response, model, headers: (model.remediation_id, headers),
            ).result()
            self.assertEqual(result, (JOB, {}))

    def test_no_polling_retains_initial_id(self):
        with self.client({"status": "Succeeded", "properties": {"remediationId": JOB}})[0] as client:
            result = client.sovereign_view_operations.begin_remediate("rg", "view", {}, polling=False).result()
            self.assertEqual(result.remediation_id, JOB)

    def test_missing_and_invalid_ids_raise(self):
        for properties in [{}, {"remediationId": 123}, {"remediationId": ""}]:
            with self.subTest(properties=properties):
                with self.client({"status": "Succeeded", "properties": properties})[0] as client:
                    with self.assertRaises(DeserializationError):
                        client.sovereign_view_operations.begin_remediate("rg", "view", {}).result()

    def test_failed_service_operation_remains_an_error(self):
        with self.client({"status": "Failed", "error": {"code": "GenerationFailed", "message": "failure"}})[0] as client:
            with self.assertRaises(HttpResponseError):
                client.sovereign_view_operations.begin_remediate("rg", "view", {}).result()

    def test_continuation_does_not_resubmit(self):
        client, transport = self.client({"status": "Succeeded", "properties": {"remediationId": JOB}})
        with client:
            poller = client.sovereign_view_operations.begin_remediate("rg", "view", {})
            self.assertEqual(poller.result().remediation_id, JOB)
            resumed = client.sovereign_view_operations.begin_remediate(
                "rg", "view", {}, continuation_token=poller.continuation_token(),
            )
            self.assertEqual(resumed.result().remediation_id, JOB)
            self.assertEqual(sum(r.method == "POST" for r in transport.requests), 1)

    def test_paging_preserves_token_and_surfaces_service_failure(self):
        transport = Transport(paging_handler)
        with SovereignMgmtClient(Credential(), "sub", transport=transport, retry_total=0) as client:
            pages = client.sovereign_view_operations.list_by_subscription().by_page()
            self.assertEqual([r.id for r in next(pages)], ["/views/one"])
            with self.assertRaises(HttpResponseError) as caught:
                list(next(pages))
            self.assertEqual(caught.exception.status_code, 502)

    def test_identity_patch_wire_contract(self):
        for name, body, expected in identity_patch_cases():
            with self.subTest(case=name):
                transport = Transport(patch_handler)
                with SovereignMgmtClient(Credential(), "sub", transport=transport) as client:
                    result = client.sovereign_view_operations.begin_update("rg", "view", body).result()
                self.assertEqual(len(transport.requests), 1)
                request = transport.requests[0]
                self.assertEqual(request.method, "PATCH")
                self.assertEqual(parse_qs(urlsplit(request.url).query)["api-version"], ["2026-10-31-preview"])
                payload = request.body.read() if hasattr(request.body, "read") else request.body
                self.assertEqual(json.loads(payload), expected)
                self.assertEqual(result.identity.principal_id, "server-principal")

    def test_identity_patch_service_failure_is_not_a_success(self):
        transport = Transport(failed_patch_handler)
        with SovereignMgmtClient(Credential(), "sub", transport=transport, polling_interval=0) as client:
            with self.assertRaises(HttpResponseError) as caught:
                client.sovereign_view_operations.begin_update(
                    "rg", "view", models.SovereignViewResourcePatch(
                        identity=models.SystemAssignedServiceIdentity(type="SystemAssigned"),
                    ),
                ).result()
        self.assertIn("SovereignViewPatchManagedIdentityError", str(caught.exception))
        self.assertEqual([r.method for r in transport.requests], ["PATCH", "GET"])


class AsyncOperationTests(unittest.IsolatedAsyncioTestCase):
    def client(self, final, immediate=False):
        transport = AsyncTransport(remediation_handler(final, immediate))
        return AsyncSovereignMgmtClient(AsyncCredential(), "sub", transport=transport, polling_interval=0), transport

    async def test_terminal_operation_envelope(self):
        async with self.client({"status": "Succeeded", "properties": {"remediationId": JOB}})[0] as client:
            poller = await client.sovereign_view_operations.begin_remediate("rg", "view", {})
            result = await poller.result()
            self.assertEqual(result.remediation_id, JOB)
            self.assertEqual(result["status"], "Succeeded")

    async def test_immediate_flat_response_and_custom_cls(self):
        async with self.client({"remediationId": JOB}, immediate=True)[0] as client:
            poller = await client.sovereign_view_operations.begin_remediate(
                "rg", "view", {}, cls=lambda response, model, headers: (model.remediation_id, headers),
            )
            self.assertEqual(await poller.result(), (JOB, {}))

    async def test_no_polling_retains_initial_id(self):
        async with self.client({"status": "Succeeded", "properties": {"remediationId": JOB}})[0] as client:
            poller = await client.sovereign_view_operations.begin_remediate("rg", "view", {}, polling=False)
            self.assertEqual((await poller.result()).remediation_id, JOB)

    async def test_missing_and_invalid_ids_raise(self):
        for properties in [{}, {"remediationId": 123}, {"remediationId": ""}]:
            with self.subTest(properties=properties):
                async with self.client({"status": "Succeeded", "properties": properties})[0] as client:
                    poller = await client.sovereign_view_operations.begin_remediate("rg", "view", {})
                    with self.assertRaises(DeserializationError):
                        await poller.result()

    async def test_failed_service_operation_remains_an_error(self):
        async with self.client({"status": "Failed", "error": {"code": "GenerationFailed", "message": "failure"}})[0] as client:
            poller = await client.sovereign_view_operations.begin_remediate("rg", "view", {})
            with self.assertRaises(HttpResponseError):
                await poller.result()

    async def test_continuation_does_not_resubmit(self):
        client, transport = self.client({"status": "Succeeded", "properties": {"remediationId": JOB}})
        async with client:
            poller = await client.sovereign_view_operations.begin_remediate("rg", "view", {})
            self.assertEqual((await poller.result()).remediation_id, JOB)
            resumed = await client.sovereign_view_operations.begin_remediate(
                "rg", "view", {}, continuation_token=poller.continuation_token(),
            )
            self.assertEqual((await resumed.result()).remediation_id, JOB)
            self.assertEqual(sum(r.method == "POST" for r in transport.requests), 1)

    async def test_paging_preserves_token_and_surfaces_service_failure(self):
        transport = AsyncTransport(paging_handler)
        async with AsyncSovereignMgmtClient(AsyncCredential(), "sub", transport=transport, retry_total=0) as client:
            pages = client.sovereign_view_operations.list_by_subscription().by_page()
            first = await pages.__anext__()
            self.assertEqual([r.id async for r in first], ["/views/one"])
            with self.assertRaises(HttpResponseError) as caught:
                await pages.__anext__()
            self.assertEqual(caught.exception.status_code, 502)

    async def test_identity_patch_wire_contract(self):
        for name, body, expected in identity_patch_cases():
            with self.subTest(case=name):
                transport = AsyncTransport(patch_handler)
                async with AsyncSovereignMgmtClient(AsyncCredential(), "sub", transport=transport) as client:
                    poller = await client.sovereign_view_operations.begin_update("rg", "view", body)
                    result = await poller.result()
                self.assertEqual(len(transport.requests), 1)
                request = transport.requests[0]
                self.assertEqual(request.method, "PATCH")
                self.assertEqual(parse_qs(urlsplit(request.url).query)["api-version"], ["2026-10-31-preview"])
                payload = request.body.read() if hasattr(request.body, "read") else request.body
                self.assertEqual(json.loads(payload), expected)
                self.assertEqual(result.identity.principal_id, "server-principal")

    async def test_identity_patch_service_failure_is_not_a_success(self):
        transport = AsyncTransport(failed_patch_handler)
        async with AsyncSovereignMgmtClient(
            AsyncCredential(), "sub", transport=transport, polling_interval=0,
        ) as client:
            poller = await client.sovereign_view_operations.begin_update(
                "rg", "view", models.SovereignViewResourcePatch(
                    identity=models.SystemAssignedServiceIdentity(type="SystemAssigned"),
                ),
            )
            with self.assertRaises(HttpResponseError) as caught:
                await poller.result()
        self.assertIn("SovereignViewPatchManagedIdentityError", str(caught.exception))
        self.assertEqual([r.method for r in transport.requests], ["PATCH", "GET"])


if __name__ == "__main__":
    unittest.main()
