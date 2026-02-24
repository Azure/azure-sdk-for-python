# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import unittest
from unittest.mock import Mock, patch
from devtools_testutils import recorded_by_proxy
from preparers import app_config_decorator_aad
from testcase import AppConfigTestCase
from azure.appconfiguration import SecretReferenceConfigurationSetting
from azure.keyvault.secrets import SecretClient
from azure.appconfiguration.provider._key_vault._secret_provider import SecretProvider

TEST_SECRET_ID = "https://myvault.vault.azure.net/secrets/my_secret"

TEST_SECRET_ID_VERSION = TEST_SECRET_ID + "/12345"


class TestSecretProvider(AppConfigTestCase, unittest.TestCase):

    def test_init_with_defaults(self):
        """Test initialization of SecretProvider with default parameters."""
        secret_provider = SecretProvider()

        # Verify initialization with defaults
        self.assertEqual(len(secret_provider._secret_clients), 0)
        self.assertIsNone(secret_provider._keyvault_credential)
        self.assertIsNone(secret_provider._secret_resolver)
        self.assertEqual(secret_provider._keyvault_client_configs, {})
        self.assertFalse(secret_provider.uses_key_vault)
        self.assertIsNone(secret_provider.secret_refresh_timer)
        self.assertEqual(len(secret_provider._secret_cache), 0)

    def test_init_with_keyvault_credential(self):
        """Test initialization with a Key Vault credential."""
        mock_credential = Mock()
        secret_provider = SecretProvider(keyvault_credential=mock_credential)

        # Verify initialization with a Key Vault credential
        self.assertEqual(len(secret_provider._secret_clients), 0)
        self.assertEqual(secret_provider._keyvault_credential, mock_credential)
        self.assertIsNone(secret_provider._secret_resolver)
        self.assertEqual(secret_provider._keyvault_client_configs, {})
        self.assertTrue(secret_provider.uses_key_vault)

    def test_init_with_secret_resolver(self):
        """Test initialization with a secret resolver."""
        mock_resolver = Mock()
        secret_provider = SecretProvider(secret_resolver=mock_resolver)

        # Verify initialization with a secret resolver
        self.assertEqual(len(secret_provider._secret_clients), 0)
        self.assertIsNone(secret_provider._keyvault_credential)
        self.assertEqual(secret_provider._secret_resolver, mock_resolver)
        self.assertEqual(secret_provider._keyvault_client_configs, {})
        self.assertTrue(secret_provider.uses_key_vault)

    def test_init_with_keyvault_client_configs(self):
        """Test initialization with Key Vault client configurations."""
        client_configs = {"https://myvault.vault.azure.net/": {"retry_total": 3}}
        secret_provider = SecretProvider(keyvault_client_configs=client_configs)

        # Verify initialization with Key Vault client configurations
        self.assertEqual(len(secret_provider._secret_clients), 0)
        self.assertIsNone(secret_provider._keyvault_credential)
        self.assertIsNone(secret_provider._secret_resolver)
        self.assertEqual(secret_provider._keyvault_client_configs, client_configs)
        self.assertTrue(secret_provider.uses_key_vault)

    def test_init_with_secret_refresh_interval(self):
        """Test initialization with a secret refresh interval."""
        mock_credential = Mock()
        refresh_interval = 30
        secret_provider = SecretProvider(keyvault_credential=mock_credential, secret_refresh_interval=refresh_interval)

        # Verify initialization with a secret refresh interval
        self.assertIsNotNone(secret_provider.secret_refresh_timer)
        self.assertTrue(secret_provider.uses_key_vault)

    def test_resolve_keyvault_reference_with_cached_secret(self):
        """Test resolving a Key Vault reference when the secret is in the cache."""
        # Create a mock Key Vault reference
        config = SecretReferenceConfigurationSetting(key="test-key", secret_id=TEST_SECRET_ID)

        # Create a SecretProvider with a mock credential
        secret_provider = SecretProvider(keyvault_credential=Mock())
        key_vault_identifier, _ = secret_provider.resolve_keyvault_reference_base(config)

        # Add to cache
        secret_provider._secret_cache[key_vault_identifier.source_id] = (
            key_vault_identifier,
            "test-key",
            "cached-secret-value",
        )

        # This should return the cached value without calling SecretClient
        result = secret_provider.resolve_keyvault_reference(config)

        # Verify the result
        self.assertEqual(result, "cached-secret-value")

    def test_resolve_keyvault_reference_with_cached_secret_version(self):
        """Test resolving a Key Vault reference when the secret is in the cache."""
        # Create a mock Key Vault reference
        config = SecretReferenceConfigurationSetting(key="test-key", secret_id=TEST_SECRET_ID_VERSION)

        # Create a SecretProvider with a mock credential
        secret_provider = SecretProvider(keyvault_credential=Mock())
        key_vault_identifier, _ = secret_provider.resolve_keyvault_reference_base(config)

        # Add to cache
        secret_provider._secret_cache[key_vault_identifier.source_id] = (
            key_vault_identifier,
            "test-key",
            "cached-secret-value",
        )

        # This should return the cached value without calling SecretClient
        result = secret_provider.resolve_keyvault_reference(config)

        # Verify the result
        self.assertEqual(result, "cached-secret-value")

    def test_resolve_keyvault_reference_with_existing_client(self):
        """Test resolving a Key Vault reference with an existing client."""
        # Create a mock Key Vault reference
        config = SecretReferenceConfigurationSetting(key="test-key", secret_id=TEST_SECRET_ID_VERSION)

        # Create a SecretProvider with a mock credential
        mock_credential = Mock()
        secret_provider = SecretProvider(keyvault_credential=mock_credential)

        # Create a mock SecretClient
        mock_client = Mock()
        mock_secret = Mock()
        mock_secret.value = "secret-value"
        mock_client.get_secret.return_value = mock_secret

        # Add the mock client to the secret_clients dictionary
        vault_url = "https://myvault.vault.azure.net/"
        secret_provider._secret_clients[vault_url] = mock_client

        # Setup key vault identifier mock
        with patch("azure.keyvault.secrets.KeyVaultSecretIdentifier") as mock_kv_id:
            mock_id_instance = Mock()
            mock_id_instance._resource_id = TEST_SECRET_ID_VERSION
            mock_id_instance.source_id = TEST_SECRET_ID_VERSION
            mock_id_instance.name = "my_secret"
            mock_id_instance.version = "12345"
            mock_id_instance.vault_url = "https://myvault.vault.azure.net"
            mock_kv_id.return_value = mock_id_instance

            # Call resolve_keyvault_reference
            with patch.object(secret_provider, "resolve_keyvault_reference_base") as mock_base:
                mock_base.return_value = (mock_id_instance, vault_url)

                result = secret_provider.resolve_keyvault_reference(config)

                # Verify the result
                self.assertEqual(result, "secret-value")
                mock_client.get_secret.assert_called_once_with(mock_id_instance.name, version=mock_id_instance.version)
                # Verify the secret was cached
                _, _, value = secret_provider._secret_cache[TEST_SECRET_ID_VERSION]
                self.assertEqual(value, "secret-value")

    def test_resolve_keyvault_reference_with_new_client(self):
        """Test resolving a Key Vault reference by creating a new client."""
        # Create a mock Key Vault reference
        config = SecretReferenceConfigurationSetting(key="test-key", secret_id=TEST_SECRET_ID_VERSION)

        # Create a SecretProvider with a mock credential
        mock_credential = Mock()
        secret_provider = SecretProvider(keyvault_credential=mock_credential)

        # Setup key vault identifier mock
        with patch("azure.keyvault.secrets.KeyVaultSecretIdentifier") as mock_kv_id:
            mock_id_instance = Mock()
            mock_id_instance._resource_id = TEST_SECRET_ID_VERSION
            mock_id_instance.source_id = TEST_SECRET_ID_VERSION
            mock_id_instance.name = "my_secret"
            mock_id_instance.version = "12345"
            mock_id_instance.vault_url = "https://myvault.vault.azure.net"
            mock_kv_id.return_value = mock_id_instance

            # Mock SecretClient creation and get_secret method
            with patch("azure.appconfiguration.provider._key_vault._secret_provider.SecretClient") as mock_client_class:
                mock_client = Mock()
                mock_secret = Mock()
                mock_secret.value = "new-secret-value"
                mock_client.get_secret.return_value = mock_secret
                mock_client_class.return_value = mock_client

                # Call resolve_keyvault_reference
                with patch.object(secret_provider, "resolve_keyvault_reference_base") as mock_base:
                    vault_url = "https://myvault.vault.azure.net/"
                    mock_base.return_value = (mock_id_instance, vault_url)

                    result = secret_provider.resolve_keyvault_reference(config)

                    # Verify the result
                    self.assertEqual(result, "new-secret-value")
                    mock_client_class.assert_called_once_with(vault_url=vault_url, credential=mock_credential)
                    mock_client.get_secret.assert_called_once_with(
                        mock_id_instance.name, version=mock_id_instance.version
                    )
                    # Verify the client was cached
                    self.assertEqual(secret_provider._secret_clients[vault_url], mock_client)
                    # Verify the secret was cached
                    _, _, value = secret_provider._secret_cache[TEST_SECRET_ID_VERSION]
                    self.assertEqual(value, "new-secret-value")

    def test_resolve_keyvault_reference_with_secret_resolver(self):
        """Test resolving a Key Vault reference using a secret resolver."""
        # Create a mock Key Vault reference
        config = SecretReferenceConfigurationSetting(key="test-key", secret_id=TEST_SECRET_ID_VERSION)

        # Create a mock secret resolver
        mock_resolver = Mock(return_value="resolved-secret-value")

        # Create a SecretProvider with the mock resolver
        secret_provider = SecretProvider(secret_resolver=mock_resolver)

        # Setup key vault identifier mock
        with patch("azure.keyvault.secrets.KeyVaultSecretIdentifier") as mock_kv_id:
            mock_id_instance = Mock()
            mock_id_instance._resource_id = TEST_SECRET_ID_VERSION
            mock_id_instance.source_id = TEST_SECRET_ID_VERSION
            mock_id_instance.name = "my_secret"
            mock_id_instance.version = "12345"
            mock_id_instance.vault_url = "https://myvault.vault.azure.net"
            mock_kv_id.return_value = mock_id_instance

            # Call resolve_keyvault_reference
            with patch.object(secret_provider, "resolve_keyvault_reference_base") as mock_base:
                vault_url = "https://myvault.vault.azure.net/"
                mock_base.return_value = (mock_id_instance, vault_url)

                result = secret_provider.resolve_keyvault_reference(config)

                # Verify the result
                self.assertEqual(result, "resolved-secret-value")
                mock_resolver.assert_called_once_with(TEST_SECRET_ID_VERSION)
                # Verify the secret was cached
                _, _, value = secret_provider._secret_cache[TEST_SECRET_ID_VERSION]
                self.assertEqual(value, "resolved-secret-value")

    def test_resolve_keyvault_reference_with_client_and_resolver_fallback(self):
        """Test falling back to a secret resolver if the client fails to get the secret."""
        # Create a mock Key Vault reference
        config = SecretReferenceConfigurationSetting(key="test-key", secret_id=TEST_SECRET_ID_VERSION)

        # Create a mock credential and secret resolver
        mock_credential = Mock()
        mock_resolver = Mock(return_value="fallback-secret-value")

        # Create a SecretProvider with both credential and resolver
        secret_provider = SecretProvider(keyvault_credential=mock_credential, secret_resolver=mock_resolver)

        # Create a mock SecretClient that returns None for get_secret
        mock_client = Mock()
        mock_client.get_secret.return_value.value = None

        # Add the mock client to the secret_clients dictionary
        vault_url = "https://myvault.vault.azure.net/"
        secret_provider._secret_clients[vault_url] = mock_client

        # Setup key vault identifier mock
        with patch("azure.keyvault.secrets.KeyVaultSecretIdentifier") as mock_kv_id:
            mock_id_instance = Mock()
            mock_id_instance._resource_id = TEST_SECRET_ID_VERSION
            mock_id_instance.source_id = TEST_SECRET_ID_VERSION
            mock_id_instance.name = "my_secret"
            mock_id_instance.version = "12345"
            mock_id_instance.vault_url = "https://myvault.vault.azure.net"
            mock_kv_id.return_value = mock_id_instance

            # Call resolve_keyvault_reference
            with patch.object(secret_provider, "resolve_keyvault_reference_base") as mock_base:
                mock_base.return_value = (mock_id_instance, vault_url)

                result = secret_provider.resolve_keyvault_reference(config)

                # Verify the result
                self.assertEqual(result, "fallback-secret-value")
                mock_client.get_secret.assert_called_once_with(mock_id_instance.name, version=mock_id_instance.version)
                mock_resolver.assert_called_once_with(TEST_SECRET_ID_VERSION)
                # Verify the secret was cached
                _, _, value = secret_provider._secret_cache[TEST_SECRET_ID_VERSION]
                self.assertEqual(value, "fallback-secret-value")

    def test_resolve_keyvault_reference_no_client_no_resolver(self):
        """Test that an error is raised when no client or resolver can resolve the reference."""
        # Create a mock Key Vault reference
        config = SecretReferenceConfigurationSetting(key="test-key", secret_id=TEST_SECRET_ID_VERSION)

        # Create a SecretProvider with a credential but no clients or resolvers
        mock_credential = Mock()
        secret_provider = SecretProvider(keyvault_credential=mock_credential)

        # Setup key vault identifier mock
        with patch("azure.keyvault.secrets.KeyVaultSecretIdentifier") as mock_kv_id:
            mock_id_instance = Mock()
            mock_id_instance._resource_id = TEST_SECRET_ID_VERSION
            mock_id_instance.source_id = TEST_SECRET_ID_VERSION
            mock_id_instance.name = "my_secret"
            mock_id_instance.version = "12345"
            mock_id_instance.vault_url = "https://myvault.vault.azure.net"
            mock_kv_id.return_value = mock_id_instance

            # Call resolve_keyvault_reference
            with patch.object(secret_provider, "resolve_keyvault_reference_base") as mock_base:
                mock_base.return_value = (mock_id_instance, "https://othervault.vault.azure.net/")

                # This should raise an error since we have no client for this vault URL
                with self.assertRaises(ValueError):
                    secret_provider.resolve_keyvault_reference(config)

    def test_close(self):
        """Test closing the SecretProvider."""
        # Create a SecretProvider with mock clients
        secret_provider = SecretProvider()

        # Create mock clients
        mock_client1 = Mock()
        mock_client2 = Mock()

        # Add the mock clients to the secret_clients dictionary
        secret_provider._secret_clients = {
            "https://vault1.vault.azure.net/": mock_client1,
            "https://vault2.vault.azure.net/": mock_client2,
        }

        # Call close
        secret_provider.close()

        # Verify both clients were closed
        mock_client1.close.assert_called_once()
        mock_client2.close.assert_called_once()

    def test_client_config_specific_credential(self):
        """Test that client configuration can specify a specific credential."""
        # Create a mock Key Vault reference
        config = SecretReferenceConfigurationSetting(key="test-key", secret_id=TEST_SECRET_ID_VERSION)

        # Create mock credentials
        mock_default_credential = Mock(name="default_credential")
        mock_specific_credential = Mock(name="specific_credential")

        # Create client configs with a specific credential
        client_configs = {
            "https://myvault.vault.azure.net/": {"credential": mock_specific_credential, "retry_total": 3}
        }

        # Create a SecretProvider with default credential and client configs
        secret_provider = SecretProvider(
            keyvault_credential=mock_default_credential, keyvault_client_configs=client_configs
        )

        # Setup key vault identifier mock
        with patch("azure.keyvault.secrets.KeyVaultSecretIdentifier") as mock_kv_id:
            mock_id_instance = Mock()
            mock_id_instance._resource_id = TEST_SECRET_ID_VERSION
            mock_id_instance.source_id = TEST_SECRET_ID_VERSION
            mock_id_instance.name = "my_secret"
            mock_id_instance.version = "12345"
            mock_id_instance.vault_url = "https://myvault.vault.azure.net"
            mock_kv_id.return_value = mock_id_instance

            # Mock SecretClient creation and get_secret method
            with patch("azure.appconfiguration.provider._key_vault._secret_provider.SecretClient") as mock_client_class:
                mock_client = Mock()
                mock_secret = Mock()
                mock_secret.value = "secret-value"
                mock_client.get_secret.return_value = mock_secret
                mock_client_class.return_value = mock_client

                # Call resolve_keyvault_reference
                with patch.object(secret_provider, "resolve_keyvault_reference_base") as mock_base:
                    vault_url = "https://myvault.vault.azure.net/"
                    mock_base.return_value = (mock_id_instance, vault_url)

                    result = secret_provider.resolve_keyvault_reference(config)

                    # Verify the specific credential was used instead of the default
                    mock_client_class.assert_called_once_with(
                        vault_url=vault_url, credential=mock_specific_credential, retry_total=3
                    )
                    # Verify the result
                    self.assertEqual(result, "secret-value")

    @recorded_by_proxy
    @app_config_decorator_aad
    def test_integration_with_keyvault(self, appconfiguration_endpoint_string, appconfiguration_keyvault_secret_url):
        """Test integration with Key Vault."""
        if not appconfiguration_keyvault_secret_url:
            self.skipTest("No Key Vault secret URL provided")

        # Get a credential
        credential = self.get_credential(SecretClient)

        # Create a SecretProvider with the credential
        secret_provider = SecretProvider(keyvault_credential=credential)

        # Create a Key Vault reference
        config = SecretReferenceConfigurationSetting(key="test-key", secret_id=appconfiguration_keyvault_secret_url)

        # Resolve the reference
        secret_value = secret_provider.resolve_keyvault_reference(config)

        # Verify a value was returned (we can't know the exact value)
        self.assertIsNotNone(secret_value)
        self.assertTrue(isinstance(secret_value, str))

        # Verify the secret was cached
        self.assertIn(appconfiguration_keyvault_secret_url, secret_provider._secret_cache)


if __name__ == "__main__":
    unittest.main()
