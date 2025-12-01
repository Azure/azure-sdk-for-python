# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------

import json
from typing import Optional
from azure.appconfiguration import ConfigurationSetting  # type: ignore
from ._constants import SNAPSHOT_NAME_FIELD


class SnapshotReferenceParser:
    """
    Parser for snapshot reference configuration settings.
    """

    @staticmethod
    def parse(setting: Optional[ConfigurationSetting]) -> str:
        """
        Parse a snapshot reference from a configuration setting containing snapshot reference JSON.

        :param Optional[ConfigurationSetting] setting: The configuration setting containing the snapshot reference JSON
        :return: The snapshot name extracted from the reference
        :rtype: str
        :raises ValueError: When the setting is None
        :raises ValueError: When the setting contains invalid JSON, invalid snapshot reference format,
                           or empty/whitespace snapshot name
        """
        if setting is None:
            raise ValueError("Setting cannot be None")

        if not setting.value or setting.value.strip() == "":
            raise ValueError(
                f"Invalid snapshot reference format for key '{setting.key}' "
                f"(label: '{setting.label}'). Value cannot be empty."
            )

        try:
            # Parse the JSON content
            json_content = json.loads(setting.value)

            if not isinstance(json_content, dict):
                raise ValueError(
                    f"Invalid snapshot reference format for key '{setting.key}' "
                    f"(label: '{setting.label}'). Expected JSON object."
                )

            # Extract the snapshot name
            snapshot_name = json_content.get(SNAPSHOT_NAME_FIELD)

            if snapshot_name is None:
                raise ValueError(
                    f"Invalid snapshot reference format for key '{setting.key}' "
                    f"(label: '{setting.label}'). The '{SNAPSHOT_NAME_FIELD}' "
                    f"property is required."
                )

            if not isinstance(snapshot_name, str):
                raise ValueError(
                    f"Invalid snapshot reference format for key '{setting.key}' "
                    f"(label: '{setting.label}'). The '{SNAPSHOT_NAME_FIELD}' "
                    f"property must be a string value, but found {type(snapshot_name).__name__}."
                )

            if not snapshot_name.strip():
                raise ValueError(
                    f"Invalid snapshot reference format for key '{setting.key}' "
                    f"(label: '{setting.label}'). Snapshot name cannot be empty or whitespace."
                )

            return snapshot_name.strip()

        except json.JSONDecodeError as json_ex:
            raise ValueError(
                f"Invalid snapshot reference format for key '{setting.key}' "
                f"(label: '{setting.label}'). Invalid JSON format."
            ) from json_ex
