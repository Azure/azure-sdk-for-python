# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Mapping


class OverrideDefinition(dict):
    """Definition of a overridable field of a component job."""


def get_override_definition_from_schema(
    schema: str,  # pylint: disable=unused-argument
) -> Mapping[str, OverrideDefinition]:
    """Ger override definition from a json schema.

    :param schema: Json schema of component job.
    :return: A dictionary from a override definition name to a override definition.
    """
    # TODO: gen override definition
    return None
