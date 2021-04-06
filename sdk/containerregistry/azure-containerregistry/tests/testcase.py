# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import copy
from datetime import datetime
import json
import re
import six
import subprocess
import time

from azure.containerregistry import (
    ContainerRepositoryClient,
    ContainerRegistryClient,
    TagProperties,
    ContentPermissions,
    RegistryArtifactProperties,
)

from azure.core.credentials import AccessToken
from azure.identity import DefaultAzureCredential

from azure_devtools.scenario_tests import RecordingProcessor
from devtools_testutils import AzureTestCase


REDACTED = "REDACTED"


class AcrBodyReplacer(RecordingProcessor):
    """Replace request body for oauth2 exchanges"""

    def __init__(self, replacement="redacted"):
        self._replacement = replacement
        self._401_replacement = 'Bearer realm="https://fake_url.azurecr.io/oauth2/token",service="fake_url.azurecr.io",scope="fake_scope",error="invalid_token"'

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
            s[idx] = "=".join([k, v])
        s = "&".join(s)
        return s.encode("utf-8")

    def _scrub_body_dict(self, body):
        new_body = copy.deepcopy(body)
        for k in ["access_token", "refresh_token"]:
            if k in new_body.keys():
                new_body[k] = REDACTED
        return new_body

    def process_request(self, request):
        if request.body:
            request.body = self._scrub_body(request.body)

        return request

    def process_response(self, response):
        try:
            headers = response["headers"]
            auth_header = None
            if "www-authenticate" in headers:
                response["headers"]["www-authenticate"] = self._401_replacement

            body = response["body"]
            try:
                if body["string"] == b'':
                    return response

                refresh = json.loads(body["string"])
                if "refresh_token" in refresh.keys():
                    refresh["refresh_token"] = REDACTED
                    body["string"] = json.dumps(refresh)
                if "access_token" in refresh.keys():
                    refresh["access_token"] = REDACTED
                    body["string"] = json.dumps(refresh)
            except ValueError:
                # Python 2.7 doesn't have the below error
                pass
            except json.decoder.JSONDecodeError:
                pass

            return response
        except (KeyError, ValueError):
            return response


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
        super(ContainerRegistryTestClass, self).__init__(method_name)
        self.vcr.match_on = ["path", "method", "query"]
        self.recording_processors.append(AcrBodyReplacer())
        self.repository = "hello-world"

    def sleep(self, t):
        if self.is_live:
            time.sleep(t)

    def _import_tag_to_be_deleted(self, endpoint, repository="hello-world", resource_group="fake_rg", tag=None):
        if not self.is_live:
            return

        if tag:
            repository = "{}:{}".format(repository, tag)

        registry = endpoint.split(".")[0]
        command = [
            "powershell.exe",
            "Import-AzcontainerRegistryImage",
            "-ResourceGroupName",
            "'{}'".format(resource_group),
            "-RegistryName",
            "'{}'".format(registry),
            "-SourceImage",
            "'library/hello-world'",
            "-SourceRegistryUri",
            "'registry.hub.docker.com'",
            "-TargetTag",
            "'{}'".format(repository),
            "-Mode",
            "'Force'",
        ]
        subprocess.check_call(command)

    def import_repo_to_be_deleted(self, endpoint, repository="hello-world", resource_group="fake_rg", tag=None):
        if not self.is_live:
            return

        if tag:
            repository = "{}:{}".format(repository, tag)
        registry = endpoint.split(".")[0]
        command = [
            "powershell.exe",
            "Import-AzcontainerRegistryImage",
            "-ResourceGroupName",
            "'{}'".format(resource_group),
            "-RegistryName",
            "'{}'".format(registry),
            "-SourceImage",
            "'library/hello-world'",
            "-SourceRegistryUri",
            "'registry.hub.docker.com'",
            "-TargetTag",
            "'{}'".format(repository),
            "-Mode",
            "'Force'",
        ]
        subprocess.check_call(command)

    def _clean_up(self, endpoint):
        if not self.is_live:
            return

        reg_client = self.create_registry_client(endpoint)
        for repo in reg_client.list_repositories():
            if repo.startswith("repo"):
                repo_client = self.create_repository_client(endpoint, repo)
                for tag in repo_client.list_tags():

                    try:
                        p = tag.content_permissions
                        p.can_delete = True
                        repo_client.set_tag_properties(tag.digest, p)
                    except:
                        pass

                self.sleep(10)
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

    def create_repository_client(self, endpoint, name, **kwargs):
        return ContainerRepositoryClient(endpoint=endpoint, repository=name, credential=self.get_credential(), **kwargs)

    def assert_content_permission(self, content_perm, content_perm2):
        assert isinstance(content_perm, ContentPermissions)
        assert isinstance(content_perm2, ContentPermissions)
        assert content_perm.can_delete == content_perm.can_delete
        assert content_perm.can_list == content_perm.can_list
        assert content_perm.can_read == content_perm.can_read
        assert content_perm.can_write == content_perm.can_write

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
        assert isinstance(tag, TagProperties)
        assert isinstance(tag.writeable_permissions, ContentPermissions)
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

    def assert_registry_artifact(self, tag_or_digest, expected_tag_or_digest):
        assert isinstance(tag_or_digest, RegistryArtifactProperties)
        assert tag_or_digest == expected_tag_or_digest
