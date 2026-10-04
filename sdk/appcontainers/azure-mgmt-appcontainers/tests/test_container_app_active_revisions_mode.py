# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
import json

from azure.core.credentials import AccessToken
from azure.core.pipeline.transport import HttpRequest, HttpResponse, HttpTransport

from azure.mgmt.appcontainers import ContainerAppsAPIClient
from azure.mgmt.appcontainers.models import (
    ActiveRevisionsMode,
    Affinity,
    Configuration,
    Container,
    ContainerApp,
    ContainerResources,
    Ingress,
    IngressStickySessions,
    IngressTransportMethod,
    Template,
)


def _container_app_envelope():
    # the exact construction from
    # https://github.com/Azure/azure-sdk-for-python/issues/48043
    return ContainerApp(
        location="francecentral",
        managed_environment_id="/subscriptions/sub-id/resourceGroups/rg/providers/Microsoft.App/managedEnvironments/env",
        configuration=Configuration(
            active_revisions_mode=ActiveRevisionsMode.SINGLE,
            ingress=Ingress(
                external=True,
                target_port=80,
                transport=IngressTransportMethod.AUTO,
                sticky_sessions=IngressStickySessions(affinity=Affinity.STICKY),
            ),
        ),
        template=Template(
            containers=[
                Container(
                    name="testcontainer",
                    image="mcr.microsoft.com/k8se/quickstart:latest",
                    resources=ContainerResources(cpu=0.5, memory="1Gi"),
                )
            ]
        ),
    )


def test_active_revisions_mode_serialized():
    # the serialization path used by ContainerAppsOperations._create_or_update_initial
    from azure.mgmt.appcontainers._utils.model_base import SdkJSONEncoder

    body = json.dumps(_container_app_envelope(), cls=SdkJSONEncoder, exclude_readonly=True)
    configuration = json.loads(body)["properties"]["configuration"]
    assert configuration["activeRevisionsMode"] == "Single"
    assert configuration["ingress"]["stickySessions"] == {"affinity": "sticky"}


def test_active_revisions_mode_deserialization_round_trip():
    app = ContainerApp(
        {
            "location": "francecentral",
            "properties": {
                "configuration": {
                    "activeRevisionsMode": "Single",
                    "ingress": {"external": True, "targetPort": 80},
                }
            },
        }
    )
    assert app.configuration.active_revisions_mode == ActiveRevisionsMode.SINGLE
    assert app.as_dict()["properties"]["configuration"]["activeRevisionsMode"] == "Single"


def test_active_revisions_mode_in_create_or_update_request():
    captured = {}

    response_body = json.dumps({"id": "app-id", "location": "francecentral", "properties": {}}).encode("utf-8")

    class FakeHttpResponse(HttpResponse):
        def __init__(self, request: HttpRequest):
            super().__init__(request, None)
            self.status_code = 200
            self.headers = {}
            self.reason = "OK"

        def read(self):
            return response_body

        @property
        def content(self):
            return response_body

        def iter_bytes(self):
            yield response_body

        def iter_raw(self):
            yield response_body

        def json(self):
            return json.loads(response_body)

        def text(self, encoding=None):
            return response_body.decode("utf-8")

    class CaptureTransport(HttpTransport):
        def send(self, request, **kwargs):
            captured["body"] = request.body
            return FakeHttpResponse(request)

        def open(self):
            pass

        def close(self):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

    class FakeCredential:
        def get_token(self, *scopes, **kwargs):
            return AccessToken("fake-token", 9999999999)

    client = ContainerAppsAPIClient(credential=FakeCredential(), subscription_id="sub-id", transport=CaptureTransport())
    client.container_apps.begin_create_or_update(
        resource_group_name="rg",
        container_app_name="app",
        container_app_envelope=_container_app_envelope(),
        polling=False,
    ).result()

    configuration = json.loads(captured["body"])["properties"]["configuration"]
    assert configuration["activeRevisionsMode"] == "Single"
