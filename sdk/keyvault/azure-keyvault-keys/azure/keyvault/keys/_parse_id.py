# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from ._shared import parse_key_vault_id, KeyVaultResourceId


def parse_key_vault_key_id(source_id):
    # type: (str) -> KeyVaultResourceId
    """Parses a key's full ID into a class with parsed contents as attributes.

    :param str source_id: the full original identifier of a key
    :returns: Returns a parsed key ID as a :class:`KeyVaultResourceId`
    :rtype: ~azure.keyvault.keys.KeyVaultResourceId
    :raises: ValueError
    Example:
        .. literalinclude:: ../tests/test_parse_id.py
            :start-after: [START parse_key_vault_key_id]
            :end-before: [END parse_key_vault_key_id]
            :language: python
            :caption: Parse a key's ID
            :dedent: 8
    """
    parsed_id = parse_key_vault_id(source_id)

    return KeyVaultResourceId(
        name=parsed_id.name, source_id=parsed_id.source_id, vault_url=parsed_id.vault_url, version=parsed_id.version
    )
