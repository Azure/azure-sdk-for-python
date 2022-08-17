# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Dict, Mapping


class OverrideDefinition(dict):
    """Definition of a overridable field of a component job."""

    def __init__(self, schema_dict: Dict):
        super(OverrideDefinition, self).__init__(schema_dict)


def get_override_definition_from_schema(
    schema: str,
) -> Mapping[str, OverrideDefinition]:
    """Ger override definition from a json schema.

    :param schema: Json schema of component job.
    :return: A dictionary from a override definition name to a override definition.
    """
    # TODO: gen override definition
    return None
