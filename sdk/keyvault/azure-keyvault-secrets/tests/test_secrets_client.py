# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import functools
import json
import logging
import time


import pytest
from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError
from azure.core.pipeline.policies import SansIOHTTPPolicy
from azure.keyvault.secrets import SecretClient
from azure.keyvault.secrets._shared.client_base import DEFAULT_VERSION
from dateutil import parser as date_parse
from devtools_testutils import recorded_by_proxy


from _shared.test_case import KeyVaultTestCase
from _test_case import SecretsClientPreparer, get_decorator

all_api_versions = get_decorator()
logging_enabled = get_decorator(logging_enable=True)
logging_disabled = get_decorator(logging_enable=False)
list_test_size = 7


# used for logging tests
class MockHandler(logging.Handler):
    def __init__(self):
        super(MockHandler, self).__init__()
        self.messages = []

    def emit(self, record):
        self.messages.append(record)


class TestSecretClient(KeyVaultTestCase):
    def _assert_secret_attributes_equal(self, s1, s2):
        assert s1.name == s2.name
        assert s1.vault_url == s2.vault_url
        assert s1.content_type == s2.content_type
        assert s1.enabled == s2.enabled
        assert s1.not_before == s2.not_before
        assert s1.expires_on == s2.expires_on
        assert s1.created_on == s2.created_on
        assert s1.updated_on == s2.updated_on
        assert s1.recovery_level == s2.recovery_level
        assert s1.key_id == s2.key_id

    def _validate_secret_bundle(self, secret_attributes, vault, secret_name, secret_value):
        prefix = "/".join(s.strip("/") for s in [vault, "secrets", secret_name])
        id = secret_attributes.id
        assert id.index(prefix) == 0, f"Id should start with '{prefix}', but value is '{id}'"
        assert (
            secret_attributes.value == secret_value
        ), f"value should be '{secret_value}', but is '{secret_attributes.value}'"

        assert (
            secret_attributes.properties.created_on and secret_attributes.properties.updated_on
        ), "Missing required date attributes."

    def _validate_secret_list(self, secrets, expected):
        for secret in secrets:
            if secret.name in expected.keys():
                expected_secret = expected[secret.name]
                self._assert_secret_attributes_equal(expected_secret.properties, secret)
                del expected[secret.name]
        assert len(expected) == 0

    @pytest.mark.parametrize("api_version", all_api_versions, ids=all_api_versions)
    @SecretsClientPreparer()
    @recorded_by_proxy
    def test_secret_crud_operations(self, **kwargs):
        client = kwargs.pop("client")
        secret_name = self.get_resource_name("crud-secret")
        secret_value = "crud_secret_value"

        # create secret
        created = client.set_secret(secret_name, secret_value)
        self._validate_secret_bundle(created, client.vault_url, secret_name, secret_value)

        # set secret with optional arguments
        expires = date_parse.parse("2050-02-02T08:00:00.000Z")
        not_before = date_parse.parse("2015-02-02T08:00:00.000Z")
        content_type = "password"
        enabled = True
        tags = {"foo": "created tag"}
        created = client.set_secret(
            secret_name,
            secret_value,
            enabled=enabled,
            content_type=content_type,
            not_before=not_before,
            expires_on=expires,
            tags=tags,
        )
        self._validate_secret_bundle(created, client.vault_url, secret_name, secret_value)
        assert content_type == created.properties.content_type
        assert enabled == created.properties.enabled
        assert not_before == created.properties.not_before
        assert expires == created.properties.expires_on
        assert tags == created.properties.tags

        self._assert_secret_attributes_equal(created.properties, client.get_secret(created.name).properties)
        self._assert_secret_attributes_equal(
            created.properties, client.get_secret(created.name, created.properties.version).properties
        )

        def _update_secret(secret):
            content_type = "text/plain"
            expires = date_parse.parse("2050-01-02T08:00:00.000Z")
            tags = {"foo": "updated tag"}
            enabled = not secret.properties.enabled
            updated_secret = client.update_secret_properties(
                secret.name,
                version=secret.properties.version,
                content_type=content_type,
                expires_on=expires,
                tags=tags,
                enabled=enabled,
            )
            assert tags == updated_secret.tags
            assert secret.id == updated_secret.id
            assert content_type == updated_secret.content_type
            assert expires == updated_secret.expires_on
            assert secret.properties.enabled != updated_secret.enabled
            assert secret.properties.updated_on != updated_secret.updated_on
            return updated_secret

        if self.is_live:
            # wait to ensure the secret's update time won't equal its creation time
            time.sleep(1)

        updated = _update_secret(created)

        # delete secret
        deleted = client.begin_delete_secret(updated.name).result()
        assert deleted is not None

    @pytest.mark.parametrize("api_version", all_api_versions, ids=all_api_versions)
    @SecretsClientPreparer()
    @recorded_by_proxy
    def test_secret_list(self, **kwargs):
        client = kwargs.pop("client")
        max_secrets = list_test_size
        expected = {}

        # create many secrets
        for x in range(0, max_secrets):
            secret_name = self.get_resource_name("sec{}".format(x))
            secret_value = "secVal{}".format(x)
            secret = None
            while not secret:
                secret = client.set_secret(secret_name, secret_value)
                expected[secret.name] = secret

        # list secrets
        result = list(client.list_properties_of_secrets(max_page_size=max_secrets - 1))
        self._validate_secret_list(result, expected)

    @pytest.mark.parametrize("api_version", all_api_versions, ids=all_api_versions)
    @SecretsClientPreparer()
    @recorded_by_proxy
    def test_list_versions(self, **kwargs):
        client = kwargs.pop("client")
        
        secret_name = self.get_resource_name("secVer")
        secret_value = "secVal"

        max_secrets = list_test_size
        expected = {}

        # create many secret versions
        for _ in range(0, max_secrets):
            secret = None
            while not secret:
                secret = client.set_secret(secret_name, secret_value)
                expected[secret.id] = secret

        result = client.list_properties_of_secret_versions(secret_name, max_page_size=max_secrets - 1)

        # validate list secret versions with attributes
        for secret in result:
            if secret.id in expected.keys():
                expected_secret = expected[secret.id]
                del expected[secret.id]
                self._assert_secret_attributes_equal(expected_secret.properties, secret)
        assert len(expected) == 0

    @pytest.mark.parametrize("api_version", all_api_versions, ids=all_api_versions)
    @SecretsClientPreparer()
    @recorded_by_proxy
    def test_list_deleted_secrets(self, **kwargs):
        client = kwargs.pop("client")
        expected = {}

        # create secrets
        for i in range(list_test_size):
            secret_name = self.get_resource_name("secret{}".format(i))
            secret_value = "value{}".format(i)
            expected[secret_name] = client.set_secret(secret_name, secret_value)

        # delete them
        for secret_name in expected.keys():
            client.begin_delete_secret(secret_name).wait()

        # validate list deleted secrets with attributes
        for deleted_secret in client.list_deleted_secrets():
            assert deleted_secret.deleted_date is not None
            assert deleted_secret.scheduled_purge_date is not None
            assert deleted_secret.recovery_id is not None
            if deleted_secret.name in expected:
                expected_secret = expected[deleted_secret.name]
                self._assert_secret_attributes_equal(expected_secret.properties, deleted_secret.properties)

    @pytest.mark.parametrize("api_version", all_api_versions, ids=all_api_versions)
    @SecretsClientPreparer()
    @recorded_by_proxy
    def test_backup_restore(self, **kwargs):
        client = kwargs.pop("client")
        
        secret_name = self.get_resource_name("secbak")
        secret_value = "secVal"

        # create secret
        created_bundle = client.set_secret(secret_name, secret_value)

        # backup secret
        secret_backup = client.backup_secret(created_bundle.name)
        assert secret_backup is not None, "secret_backup"

        # delete secret
        client.begin_delete_secret(created_bundle.name).wait()

        # purge secret
        client.purge_deleted_secret(created_bundle.name)

        # restore secret
        restore_function = functools.partial(client.restore_secret_backup, secret_backup)
        restored_secret = self._poll_until_no_exception(restore_function, ResourceExistsError)
        self._assert_secret_attributes_equal(created_bundle.properties, restored_secret)

    @pytest.mark.parametrize("api_version", all_api_versions, ids=all_api_versions)
    @SecretsClientPreparer()
    @recorded_by_proxy
    def test_recover(self, **kwargs):
        client = kwargs.pop("client")
        
        secrets = {}

        # create secrets to recover
        for i in range(list_test_size):
            secret_name = self.get_resource_name("secret{}".format(i))
            secret_value = "value{}".format(i)
            secrets[secret_name] = client.set_secret(secret_name, secret_value)

        # delete all secrets
        for secret_name in secrets.keys():
            client.begin_delete_secret(secret_name).wait()

        # validate all our deleted secrets are returned by list_deleted_secrets
        deleted = [s.name for s in client.list_deleted_secrets()]
        assert all(s in deleted for s in secrets.keys())

        # recover select secrets
        for secret_name in secrets.keys():
            client.begin_recover_deleted_secret(secret_name).wait()

        # validate the recovered secrets exist
        for secret_name in secrets.keys():
            secret = client.get_secret(name=secret_name)
            self._assert_secret_attributes_equal(secret.properties, secrets[secret.name].properties)

    @pytest.mark.parametrize("api_version", all_api_versions, ids=all_api_versions)
    @SecretsClientPreparer()
    @recorded_by_proxy
    def test_purge(self, **kwargs):
        client = kwargs.pop("client")
        
        secrets = {}

        # create secrets to purge
        for i in range(list_test_size):
            secret_name = self.get_resource_name("secret{}".format(i))
            secret_value = "value{}".format(i)
            secrets[secret_name] = client.set_secret(secret_name, secret_value)

        # delete all secrets
        for secret_name in secrets.keys():
            client.begin_delete_secret(secret_name).wait()

        # validate all our deleted secrets are returned by list_deleted_secrets
        deleted = [s.name for s in client.list_deleted_secrets()]
        assert all(s in deleted for s in secrets.keys())

        # purge secrets
        for secret_name in secrets.keys():
            client.purge_deleted_secret(secret_name)
        for secret_name in secrets.keys():
            self._poll_until_exception(functools.partial(client.get_deleted_secret, secret_name), ResourceNotFoundError)

        deleted = [s.name for s in client.list_deleted_secrets()]
        assert not any(s in deleted for s in secrets.keys())

    @pytest.mark.parametrize("api_version", all_api_versions, ids=all_api_versions)
    @SecretsClientPreparer(logging_enable=True)
    @recorded_by_proxy
    def test_logging_enabled(self, **kwargs):
        client = kwargs.pop("client")
        mock_handler = MockHandler()

        logger = logging.getLogger("azure")
        logger.addHandler(mock_handler)
        logger.setLevel(logging.DEBUG)

        secret_name = self.get_resource_name("secret-name")
        client.set_secret(secret_name, "secret-value")

        for message in mock_handler.messages:
            if message.levelname == "DEBUG" and message.funcName == "on_request":
                # parts of the request are logged on new lines in a single message
                if "'/n" in message.message:
                    request_sections = message.message.split("/n")
                else:
                    request_sections = message.message.split("\n")
                for section in request_sections:
                    try:
                        # the body of the request should be JSON
                        body = json.loads(section)
                        if body["value"] == "secret-value":
                            mock_handler.close()
                            return
                    except (ValueError, KeyError):
                        # this means the request section is not JSON
                        pass

        mock_handler.close()
        assert False, "Expected request body wasn't logged"

    @pytest.mark.parametrize("api_version", all_api_versions, ids=all_api_versions)
    @SecretsClientPreparer(logging_enable=False)
    @recorded_by_proxy
    def test_logging_disabled(self, **kwargs):
        client = kwargs.pop("client")
        mock_handler = MockHandler()

        logger = logging.getLogger("azure")
        logger.addHandler(mock_handler)
        logger.setLevel(logging.DEBUG)

        secret_name = self.get_resource_name("secret-name")
        client.set_secret(secret_name, "secret-value")

        for message in mock_handler.messages:
            if message.levelname == "DEBUG" and message.funcName == "on_request":
                # parts of the request are logged on new lines in a single message
                if "'/n" in message.message:
                    request_sections = message.message.split("/n")
                else:
                    request_sections = message.message.split("\n")
                for section in request_sections:
                    try:
                        # the body of the request should be JSON
                        body = json.loads(section)
                        if body["value"] == "secret-value":
                            mock_handler.close()
                            assert False, "Client request body was logged"
                    except (ValueError, KeyError):
                        # this means the message is not JSON or has no kty property
                        pass

        mock_handler.close()


def test_service_headers_allowed_in_logs():
    service_headers = {"x-ms-keyvault-network-info", "x-ms-keyvault-region", "x-ms-keyvault-service-version"}
    client = SecretClient("...", object())
    assert service_headers.issubset(client._client._config.http_logging_policy.allowed_header_names)


def test_custom_hook_policy():
    class CustomHookPolicy(SansIOHTTPPolicy):
        pass

    client = SecretClient("...", object(), custom_hook_policy=CustomHookPolicy())
    assert isinstance(client._client._config.custom_hook_policy, CustomHookPolicy)
