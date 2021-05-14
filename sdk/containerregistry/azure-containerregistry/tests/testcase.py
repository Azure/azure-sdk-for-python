# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import copy
from datetime import datetime
import json
import logging
import os
from azure_devtools.scenario_tests.recording_processors import SubscriptionRecordingProcessor
import pytest
import re
import six
import time

from azure.containerregistry import (
    ContainerRepository,
    ContainerRegistryClient,
    ArtifactTagProperties,
    ContentProperties,
    ArtifactManifestProperties,
)

from azure.core.credentials import AccessToken
from azure.mgmt.containerregistry import ContainerRegistryManagementClient
from azure.mgmt.containerregistry.models import (
    ImportImageParameters,
    ImportSource,
    ImportMode
)
from azure.identity import DefaultAzureCredential

from devtools_testutils import AzureTestCase, is_live
from azure_devtools.scenario_tests import (
    GeneralNameReplacer,
    RequestUrlNormalizer,
    AuthenticationMetadataFilter,
    RecordingProcessor,
)
from azure_devtools.scenario_tests import (
    GeneralNameReplacer,
    RequestUrlNormalizer,
    AuthenticationMetadataFilter,
    RecordingProcessor,
)


REDACTED = "REDACTED"


class OAuthRequestResponsesFilterACR(RecordingProcessor):
    """Remove oauth authentication requests and responses from recording."""

    def process_request(self, request):
        # filter request like:
        # GET https://login.microsoftonline.com/72f988bf-86f1-41af-91ab-2d7cd011db47/oauth2/token
        # POST https://login.microsoftonline.com/72f988bf-86f1-41af-91ab-2d7cd011db47/oauth2/v2.0/token
        # But we want to leave Azure Container Registry challenge auth requests alone
        import re

        if not re.search("/oauth2(?:/v2.0)?/token", request.uri) or "azurecr.io" in request.uri:
            return request
        return None


class ManagementRequestReplacer(RecordingProcessor):
    """Remove oauth authentication requests and responses from recording."""

    # Don't need to save the import image requests

    def process_request(self, request):
        if "management.azure.com" not in request.uri:
            return request
        return None


class AcrBodyReplacer(RecordingProcessor):
    """Replace request body for oauth2 exchanges"""

    def __init__(self, replacement="redacted"):
        self._replacement = replacement
        self._401_replacement = 'Bearer realm="https://fake_url.azurecr.io/oauth2/token",service="fake_url.azurecr.io",scope="fake_scope",error="invalid_token"'
        self._redacted_service = "https://fakeurl.azurecr.io"
        self._regex = r"(https://)[a-zA-Z0-9]+(\.azurecr.io)"

    def _scrub_body(self, body):
        # type: (bytes) -> bytes
        if isinstance(body, dict):
            return self._scrub_body_dict(body)
        if not isinstance(body, six.binary_type):
            return body
        s = body.decode("utf-8")
        if "access_token" not in s and "refresh_token" not in s:
            return body
        s = s.split("&")
        for idx, pair in enumerate(s):
            [k, v] = pair.split("=")
            if k == "access_token" or k == "refresh_token":
                v = REDACTED
            if k == "service":
                v = "fake_url.azurecr.io"
            s[idx] = "=".join([k, v])
        s = "&".join(s)
        return s.encode("utf-8")

    def _scrub_body_dict(self, body):
        new_body = copy.deepcopy(body)
        for k in ["access_token", "refresh_token"]:
            if k in new_body.keys():
                new_body[k] = REDACTED
        if "service" in new_body.keys():
            new_body["service"] = "fake_url.azurecr.io"
        return new_body

    def process_request(self, request):
        if request.body:
            request.body = self._scrub_body(request.body)

        if "seankane.azurecr.io" in request.uri:
            request.uri = request.uri.replace("seankane.azurecr.io", "fake_url.azurecr.io")
        if "seankane.azurecr.io" in request.url:
            request.url = request.url.replace("seankane.azurecr.io", "fake_url.azurecr.io")

        if "seankaneanon.azurecr.io" in request.uri:
            request.uri = request.uri.replace("seankaneanon.azurecr.io", "fake_url.azurecr.io")
        if "seankaneanon.azurecr.io" in request.url:
            request.url = request.url.replace("seankaneanon.azurecr.io", "fake_url.azurecr.io")

        return request

    def process_response(self, response):
        try:
            self.process_url(response)
            headers = response["headers"]

            if "www-authenticate" in headers:
                headers["www-authenticate"] = (
                    [self._401_replacement] if isinstance(headers["www-authenticate"], list) else self._401_replacement
                )

            body = response["body"]
            try:
                if body["string"] == b"" or body["string"] == "null":
                    return response

                if "seankane.azurecr.io" in body["string"]:
                    body["string"] = body["string"].replace("seankane.azurecr.io", "fake_url.azurecr.io")

                if "seankaneanon.azurecr.io" in body["string"]:
                    body["string"] = body["string"].replace("seankaneanon.azurecr.io", "fake_url.azurecr.io")

                refresh = json.loads(body["string"])
                if "refresh_token" in refresh.keys():
                    refresh["refresh_token"] = REDACTED
                if "access_token" in refresh.keys():
                    refresh["access_token"] = REDACTED
                if "service" in refresh.keys():
                    s = refresh["service"].split(".")
                    s[0] = "fake_url"
                    refresh["service"] = ".".join(s)
                body["string"] = json.dumps(refresh)
            except ValueError:
                # Python 2.7 doesn't have the below error
                pass
            except json.decoder.JSONDecodeError:
                pass

            return response
        except (KeyError, ValueError):
            return response

    def process_url(self, response):
        try:
            response["url"] = re.sub(self._regex, r"\1{}\2".format("fake_url"), response["url"])
        except KeyError:
            pass


class FakeTokenCredential(object):
    """Protocol for classes able to provide OAuth tokens.
    :param str scopes: Lets you specify the type of access needed.
    """

    def __init__(self):
        self.token = AccessToken("YOU SHALL NOT PASS", 0)

    def get_token(self, *args):
        return self.token


class ContainerRegistryTestClass(AzureTestCase):
    def __init__(self, method_name):
        super(ContainerRegistryTestClass, self).__init__(
            method_name,
            recording_processors=[
                GeneralNameReplacer(),
                OAuthRequestResponsesFilterACR(),
                AuthenticationMetadataFilter(),
                RequestUrlNormalizer(),
                AcrBodyReplacer(),
                ManagementRequestReplacer(),
            ],
        )
        self.repository = "library/busybox"

    def sleep(self, t):
        if self.is_live:
            time.sleep(t)

    def import_image(self, repository, tags):
        # repository must be a docker hub repository
        # tags is a List of repository/tag combos in the format <repository>:<tag>
        if not self.is_live:
            return

        import_image(repository, tags)

    def _clean_up(self, endpoint):
        if not self.is_live:
            return

        reg_client = self.create_registry_client(endpoint)
        for repo in reg_client.list_repository_names():
            if repo.startswith("repo"):
                repo_client = self.create_container_repository(endpoint, repo)
                for tag in repo_client.list_tags():

                    try:
                        p = tag.writeable_properties
                        p.can_delete = True
                        repo_client.set_tag_properties(tag.digest, p)
                    except:
                        pass

                for manifest in repo_client.list_manifests():
                    try:
                        p = manifest.writeable_properties
                        p.can_delete = True
                        repo_client.set_manifest_properties(tag.digest, p)
                    except:
                        pass

        for repo in reg_client.list_repository_names():
            try:
                reg_client.delete_repository(repo)
            except:
                pass

    def get_credential(self):
        if self.is_live:
            return DefaultAzureCredential()
        return FakeTokenCredential()

    def create_registry_client(self, endpoint, **kwargs):
        return ContainerRegistryClient(endpoint=endpoint, credential=self.get_credential(), **kwargs)

    def create_container_repository(self, endpoint, name, **kwargs):
        return ContainerRepository(endpoint=endpoint, name=name, credential=self.get_credential(), **kwargs)

    def create_anon_client(self, endpoint, **kwargs):
        return ContainerRegistryClient(endpoint=endpoint, credential=None, **kwargs)

    def assert_content_permission(self, content_perm, content_perm2):
        assert isinstance(content_perm, ContentProperties)
        assert isinstance(content_perm2, ContentProperties)
        assert content_perm.can_delete == content_perm2.can_delete
        assert content_perm.can_list == content_perm2.can_list
        assert content_perm.can_read == content_perm2.can_read
        assert content_perm.can_write == content_perm2.can_write

    def assert_tag(
        self,
        tag,
        created_on=None,
        digest=None,
        last_updated_on=None,
        content_permission=None,
        name=None,
        registry=None,
        repository=None,
    ):
        assert isinstance(tag, ArtifactTagProperties)
        assert isinstance(tag.writeable_permissions, ContentProperties)
        assert isinstance(tag.created_on, datetime)
        assert isinstance(tag.last_updated_on, datetime)
        if content_permission:
            self.assert_content_permission(tag.content_permission, content_permission)
        if created_on:
            assert tag.created_on == created_on
        if last_updated_on:
            assert tag.last_updated_on == last_updated_on
        if name:
            assert tag.name == name
        if registry:
            assert tag.registry == registry
        if repository:
            assert tag.repository == repository


# Moving this out of testcase so the fixture and individual tests can use it
def import_image(repository, tags):
    mgmt_client = ContainerRegistryManagementClient(
        DefaultAzureCredential(), os.environ["CONTAINERREGISTRY_SUBSCRIPTION_ID"]
    )
    registry_uri = "registry.hub.docker.com"
    rg_name = os.environ["CONTAINERREGISTRY_RESOURCE_GROUP"]
    registry_name = os.environ["CONTAINERREGISTRY_REGISTRY_NAME"]

    import_source = ImportSource(source_image=repository, registry_uri=registry_uri)

    import_params = ImportImageParameters(mode=ImportMode.Force, source=import_source, target_tags=tags)

    result = mgmt_client.registries.begin_import_image(
        rg_name,
        registry_name,
        parameters=import_params,
    )

    while not result.done():
        pass

    # Do the same for anonymous
    mgmt_client = ContainerRegistryManagementClient(
        DefaultAzureCredential(), os.environ["CONTAINERREGISTRY_SUBSCRIPTION_ID"]
    )
    registry_uri = "registry.hub.docker.com"
    rg_name = os.environ["CONTAINERREGISTRY_RESOURCE_GROUP"]
    registry_name = os.environ["CONTAINERREGISTRY_ANONREGISTRY_NAME"]

    import_source = ImportSource(source_image=repository, registry_uri=registry_uri)

    import_params = ImportImageParameters(mode=ImportMode.Force, source=import_source, target_tags=tags)

    result = mgmt_client.registries.begin_import_image(
        rg_name,
        registry_name,
        parameters=import_params,
    )

    while not result.done():
        pass


@pytest.fixture(scope="session")
def load_registry():
    if not is_live():
        return
    repos = [
        "library/hello-world",
        "library/alpine",
        "library/busybox",
    ]
    tags = [
        [
            "library/hello-world:latest",
            "library/hello-world:v1",
            "library/hello-world:v2",
            "library/hello-world:v3",
            "library/hello-world:v4",
        ],
        ["library/alpine"],
        ["library/busybox"],
    ]
    for repo, tag in zip(repos, tags):
        try:
            import_image(repo, tag)
        except Exception as e:
            print(e)
