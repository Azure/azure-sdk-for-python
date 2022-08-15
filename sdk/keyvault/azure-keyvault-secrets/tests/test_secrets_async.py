# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import asyncio
import functools
import json
import logging

import pytest
from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError
from azure.core.pipeline.policies import SansIOHTTPPolicy
from azure.keyvault.secrets.aio import SecretClient
from dateutil import parser as date_parse
from devtools_testutils import AzureRecordedTestCase
from devtools_testutils.aio import recorded_by_proxy_async

from _async_test_case import AsyncSecretsClientPreparer
from _shared.test_case_async import KeyVaultTestCase
from _test_case import get_decorator

all_api_versions = get_decorator()
list_test_size = 7


# used for logging tests
class MockHandler(logging.Handler):
    def __init__(self):
        super(MockHandler, self).__init__()
        self.messages = []

    def emit(self, record):
        self.messages.append(record)


class TestKeyVaultSecret(KeyVaultTestCase):
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

    async def _validate_secret_list(self, secrets, expected):
        async for secret in secrets:
            if secret.name in expected.keys():
                expected_secret = expected[secret.name]
                self._assert_secret_attributes_equal(expected_secret.properties, secret)
                del expected[secret.name]
        assert len(expected) == 0

    @AzureRecordedTestCase.await_prepared_test
    @pytest.mark.parametrize("api_version", all_api_versions, ids=all_api_versions)
    @AsyncSecretsClientPreparer()
    @recorded_by_proxy_async
    async def test_secret_crud_operations(self, client, **kwargs):
        secret_name = self.get_resource_name("crud-secret")
        secret_value = "crud_secret_value"

        async with client:
            # create secret
            created = await client.set_secret(secret_name, secret_value)
            self._validate_secret_bundle(created, client.vault_url, secret_name, secret_value)

            # set secret with optional arguments
            not_before = date_parse.parse("2015-02-02T08:00:00.000Z")
            enabled = True
            tags = {"foo": "created tag"}
            created = await client.set_secret(
                secret_name, secret_value, enabled=enabled, not_before=not_before, tags=tags
            )
            self._validate_secret_bundle(created, client.vault_url, secret_name, secret_value)
            assert enabled == created.properties.enabled
            assert not_before == created.properties.not_before
            assert tags == created.properties.tags

            # get secret without version
            retrieved_secret = await client.get_secret(created.name, "")
            assert created.id == retrieved_secret.id
            self._assert_secret_attributes_equal(created.properties, retrieved_secret.properties)

            # get secret with version
            secret_with_version = await client.get_secret(created.name, created.properties.version)
            assert created.id == retrieved_secret.id
            self._assert_secret_attributes_equal(created.properties, secret_with_version.properties)

            async def _update_secret(secret):
                content_type = "text/plain"
                expires = date_parse.parse("2050-02-02T08:00:00.000Z")
                tags = {"foo": "updated tag"}
                enabled = not secret.properties.enabled
                updated_secret = await client.update_secret_properties(
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

            # update secret with version
            if self.is_live:
                # wait a second to ensure the secret's update time won't equal its creation time
                await asyncio.sleep(1)

            updated = await _update_secret(created)

            # delete secret
            deleted = await client.delete_secret(updated.name)
            assert deleted is not None

    @AzureRecordedTestCase.await_prepared_test
    @pytest.mark.parametrize("api_version", all_api_versions, ids=all_api_versions)
    @AsyncSecretsClientPreparer()
    @recorded_by_proxy_async
    async def test_secret_list(self, client, **kwargs):

        max_secrets = list_test_size
        expected = {}

        # create many secrets
        for x in range(0, max_secrets):
            secret_name = self.get_resource_name("sec{}".format(x))
            secret_value = "secVal{}".format(x)
            secret = None
            while not secret:
                secret = await client.set_secret(secret_name, secret_value)
                expected[secret_name] = secret

        # list secrets
        result = client.list_properties_of_secrets(max_page_size=max_secrets - 1)
        await self._validate_secret_list(result, expected)

    @AzureRecordedTestCase.await_prepared_test
    @pytest.mark.parametrize("api_version", all_api_versions, ids=all_api_versions)
    @AsyncSecretsClientPreparer()
    @recorded_by_proxy_async
    async def test_list_deleted_secrets(self, client, **kwargs):
        expected = {}

        async with client:
            # create secrets
            for i in range(list_test_size):
                secret_name = self.get_resource_name("secret{}".format(i))
                secret_value = "value{}".format(i)
                expected[secret_name] = await client.set_secret(secret_name, secret_value)

            # delete them
            for secret_name in expected.keys():
                await client.delete_secret(secret_name)

            # validate list deleted secrets with attributes
            async for deleted_secret in client.list_deleted_secrets():
                assert deleted_secret.deleted_date is not None
                assert deleted_secret.scheduled_purge_date is not None
                assert deleted_secret.recovery_id is not None
                if deleted_secret.name in expected:
                    expected_secret = expected[deleted_secret.name]
                    self._assert_secret_attributes_equal(expected_secret.properties, deleted_secret.properties)

    @AzureRecordedTestCase.await_prepared_test
    @pytest.mark.parametrize("api_version", all_api_versions, ids=all_api_versions)
    @AsyncSecretsClientPreparer()
    @recorded_by_proxy_async
    async def test_list_versions(self, client, **kwargs):
        secret_name = self.get_resource_name("sec")
        secret_value = "secVal"

        max_secrets = list_test_size
        expected = {}

        async with client:
            # create many secret versions
            for _ in range(0, max_secrets):
                secret = None
                while not secret:
                    secret = await client.set_secret(secret_name, secret_value)
                    expected[secret.id] = secret

            # list secret versions
            result = client.list_properties_of_secret_versions(secret_name, max_page_size=max_secrets - 1)

            # validate list secret versions with attributes
            async for secret in result:
                if secret.id in expected.keys():
                    expected_secret = expected[secret.id]
                    del expected[secret.id]
                    self._assert_secret_attributes_equal(expected_secret.properties, secret)
            assert len(expected) == 0

    @AzureRecordedTestCase.await_prepared_test
    @pytest.mark.parametrize("api_version", all_api_versions, ids=all_api_versions)
    @AsyncSecretsClientPreparer()
    @recorded_by_proxy_async
    async def test_backup_restore(self, client, **kwargs):
        secret_name = self.get_resource_name("secbak")
        secret_value = "secVal"

        async with client:
            # create secret
            created_bundle = await client.set_secret(secret_name, secret_value)

            # backup secret
            secret_backup = await client.backup_secret(created_bundle.name)
            assert secret_backup is not None, "secret_backup"

            # delete secret
            await client.delete_secret(created_bundle.name)

            # purge secret
            await client.purge_deleted_secret(created_bundle.name)

            # restore secret
            restore_function = functools.partial(client.restore_secret_backup, secret_backup)
            restored_secret = await self._poll_until_no_exception(
                restore_function, expected_exception=ResourceExistsError
            )
            self._assert_secret_attributes_equal(created_bundle.properties, restored_secret)

    @AzureRecordedTestCase.await_prepared_test
    @pytest.mark.parametrize("api_version", all_api_versions, ids=all_api_versions)
    @AsyncSecretsClientPreparer()
    @recorded_by_proxy_async
    async def test_recover(self, client, **kwargs):
        secrets = {}

        async with client:
            # create secrets to recover
            for i in range(list_test_size):
                secret_name = self.get_resource_name("secret{}".format(i))
                secret_value = "value{}".format(i)
                secrets[secret_name] = await client.set_secret(secret_name, secret_value)

            # delete all secrets
            for secret_name in secrets.keys():
                await client.delete_secret(secret_name)

            # validate all our deleted secrets are returned by list_deleted_secrets
            async for deleted_secret in client.list_deleted_secrets():
                if deleted_secret.name in secrets:
                    secrets.pop(deleted_secret.name)
            assert len(secrets.keys()) == 0

            # recover select secrets
            for secret_name in secrets.keys():
                await client.recover_deleted_secret(secret_name)

            # validate the recovered secrets exist
            for secret in secrets.keys():
                get_function = functools.partial(client.get_secret, secret)
                await self._poll_until_no_exception(get_function, expected_exception=ResourceNotFoundError)

    @AzureRecordedTestCase.await_prepared_test
    @pytest.mark.parametrize("api_version", all_api_versions, ids=all_api_versions)
    @AsyncSecretsClientPreparer()
    @recorded_by_proxy_async
    async def test_purge(self, client, **kwargs):
        secrets = {}
        async with client:
            # create secrets to purge
            for i in range(list_test_size):
                secret_name = self.get_resource_name("secret{}".format(i))
                secret_value = "value{}".format(i)
                secrets[secret_name] = await client.set_secret(secret_name, secret_value)

            # delete all secrets
            for secret_name in secrets.keys():
                await client.delete_secret(secret_name)

            # validate all our deleted secrets are returned by list_deleted_secrets
            async for deleted_secret in client.list_deleted_secrets():
                if deleted_secret.name in secrets:
                    secrets.pop(deleted_secret.name)
            assert len(secrets.keys()) == 0

            # purge secrets
            for secret_name in secrets.keys():
                await client.purge_deleted_secret(secret_name)

    @AzureRecordedTestCase.await_prepared_test
    @pytest.mark.parametrize("api_version", all_api_versions, ids=all_api_versions)
    @AsyncSecretsClientPreparer(logging_enable=True)
    @recorded_by_proxy_async
    async def test_logging_enabled(self, client, **kwargs):
        mock_handler = MockHandler()
        logger = logging.getLogger("azure")
        logger.addHandler(mock_handler)
        logger.setLevel(logging.DEBUG)

        secret_name = self.get_resource_name("secret-name")

        async with client:
            await client.set_secret(secret_name, "secret-value")

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
                                return dict()
                        except (ValueError, KeyError):
                            # this means the request section is not JSON
                            pass

            mock_handler.close()
            assert False, "Expected request body wasn't logged"

    @AzureRecordedTestCase.await_prepared_test
    @pytest.mark.parametrize("api_version", all_api_versions, ids=all_api_versions)
    @AsyncSecretsClientPreparer(logging_enable=False)
    @recorded_by_proxy_async
    async def test_logging_disabled(self, client, **kwargs):
        mock_handler = MockHandler()
        logger = logging.getLogger("azure")
        logger.addHandler(mock_handler)
        logger.setLevel(logging.DEBUG)

        secret_name = self.get_resource_name("secret-name")
        async with client:
            await client.set_secret(secret_name, "secret-value")

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
