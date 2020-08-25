# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from ._shared import parse_key_vault_identifier, ParsedId


def parse_certificate_id(original_id):
    # type: (str) -> ParsedId
    """Parses a full certificate's ID into a class.

    :param str original_id: the full original identifier of a certificate
    :returns: Returns a parsed certificate id
    :rtype: ~azure.keyvault.certificates.ParsedId
    :raises: ValueError

    Example:
        .. literalinclude:: ../tests/test_parse_id.py
            :start-after: [START parse_certificate_id]
            :end-before: [END parse_certificate_id]
            :language: python
            :caption: Parse a certificate's ID
            :dedent: 8
    """
    parsed_id = parse_key_vault_identifier(original_id)

    valid_collections = ["certificates", "deletedcertificates"]

    if parsed_id.collection not in valid_collections:
        raise ValueError(
            "Collection '{}' is not a valid certificate collection. ".format(parsed_id.collection),
            "Valid collections are: {}".format(", ".join(valid_collections))
        )
    return ParsedId(
        collection=parsed_id.collection,
        name=parsed_id.name,
        original_id=parsed_id.original_id,
        vault_url=parsed_id.vault_url,
        version=parsed_id.version
    )
