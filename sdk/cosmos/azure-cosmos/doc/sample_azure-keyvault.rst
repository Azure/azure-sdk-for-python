KeyVault
========

For general information on resource management, see :doc:`Resource Management<resourcemanagement>`.

Create the client
-----------------

The following code creates an instance of the client.

See :doc:`Resource Management Authentication <quickstart_authentication>`
for details on handling Azure Active Directory authentication with the Python SDK, and creating a ``Credentials`` instance.

.. important:: You must specify `resource="https://vault.azure.net"` while authenticating to get a valid token

.. code:: python

    from azure.keyvault import KeyVaultClient
    from azure.common.credentials import UserPassCredentials
    
    # See above for details on creating different types of AAD credentials
    credentials = UserPassCredentials(
        'user@domain.com',  # Your user
        'my_password',      # Your password
        resource='https://vault.azure.net'
    )

    client = KeyVaultClient(
        credentials
    )

Access policies
---------------

Some operations require the correct access policies for your credentials.

If you get an "Unauthorized" error, please add the correct access policies 
to this credentials using the Azure Portal, the Azure CLI or the :doc:`Key Vault Management SDK itself <sample_azure-mgmt-keyvault>`

Example
-------

``KEY_VAULT_URI`` is the base url of your keyvault. Eg. `https://myvault.vault.azure.net`

.. code:: python


    # Create a key
    key_bundle = client.create_key(KEY_VAULT_URI, 'FirstKey', 'RSA')
    key_id = KeyVaultId.parse_key_id(key_bundle.key.kid)

    # Update a key without version
    client.update_key(key_id.vault, key_id.name, key_id.version_none, key_attributes={'enabled': False})

    # Update a key with version
    client.update_key(key_id.vault, key_id.name, key_id.version, key_attributes={'enabled': False})

    # Print a list of versions for a key
    versions = client.get_key_versions(KEY_VAULT_URI, 'FirstKey')
    for version in versions:
        print(version.kid)  # https://myvault.vault.azure.net/keys/FirstKey/000102030405060708090a0b0c0d0e0f

    # Read a key without version
    client.get_key(key_id.vault, key_id.name, key_id.version_none)

    # Read a key with version
    client.get_key(key_id.vault, key_id.name, key_id.version)

    # Delete a key
    client.delete_key(KEY_VAULT_URI, 'FirstKey')


    # Create a secret
    secret_bundle = client.set_secret(KEY_VAULT_URI, 'FirstSecret', 'Hush, that is secret!!')
    secret_id = KeyVaultId.parse_secret_id(secret_bundle.id)

    # Update a secret without version
    client.update_secret(secret_id.vault, secret_id.name, secret_id.version_none, secret_attributes={'enabled': False})

    # Update a secret with version
    client.update_key(secret_id.vault, secret_id.name, secret_id.version, secret_attributes={'enabled': False})

    # Print a list of versions for a secret
    versions = client.get_secret_versions(KEY_VAULT_URI, 'FirstSecret')
    for version in versions:
        print(version.id)  # https://myvault.vault.azure.net/secrets/FirstSecret/000102030405060708090a0b0c0d0e0f

    # Read a secret without version
    client.get_secret(secret_id.vault, secret_id.name, secret_id.version_none)

    # Read a secret with version
    client.get_secret(secret_id.vault, secret_id.name, secret_id.version)

    # Delete a secret
    client.delete_secret(KEY_VAULT_URI, 'FirstSecret')
