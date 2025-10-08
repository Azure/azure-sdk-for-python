import os
import pytest
import json

from ci_tools.conda.CondaConfiguration import CondaConfiguration


def test_conda_config_retrieve():
    raw_json = """
    {
        "name": "azure-core",
        "common_root": "azure",
        "service": "core",
        "in_batch": true,
        "checkout": [
            {
                "package": "azure-core",
                "version": "1.32.0"
            },
            {
                "package": "azure-mgmt-core",
                "version": "1.5.0"
            },
            {
                "package": "azure-common",
                "version": "1.1.28"
            }
        ]
    }
    """

    CondaConfiguration.from_json(json.loads(raw_json))
