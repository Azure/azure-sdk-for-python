# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from ._shared import parse_key_vault_id, KeyVaultResourceId


def parse_key_vault_secret_id(source_id):
    # type: (str) -> KeyVaultResourceId
    """Parses a secret's full ID into a class with parsed contents as attributes.

    :param str source_id: the full original identifier of a secret
    :returns: Returns a parsed secret ID as a :class:`KeyVaultResourceId`
    :rtype: ~azure.keyvault.secrets.KeyVaultResourceId
    :raises: ValueError
    Example:
        .. literalinclude:: ../tests/test_parse_id.py
            :start-after: [START parse_key_vault_secret_id]
            :end-before: [END parse_key_vault_secret_id]
            :language: python
            :caption: Parse a secret's ID
            :dedent: 8
    """
    parsed_id = parse_key_vault_id(source_id)

    return KeyVaultResourceId(
        name=parsed_id.name, source_id=parsed_id.source_id, vault_url=parsed_id.vault_url, version=parsed_id.version
    )
