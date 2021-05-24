# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from azure.iot.modelsrepository import dtmi_conventions


def sample_is_valid_dtmi():
    """Check if a DTMI is valid or not using the .is_valid_dtmi() function"""
    # Returns True - this is a valid DTMI
    dtmi_conventions.is_valid_dtmi("dtmi:com:example:Thermostat;1")

    # Returns False - this is NOT a valid DTMI
    dtmi_conventions.is_valid_dtmi("dtmi:com:example:Thermostat")


def sample_get_model_uri():
    """Get a URI for a model in a Models Repository using the .get_model_uri() function"""
    dtmi = "dtmi:com:example:Thermostat;1"

    # Local repository example
    repo_uri = "file:///path/to/repository"
    print(dtmi_conventions.get_model_uri(dtmi, repo_uri))
    # Prints: "file:///path/to/repository/dtmi/com/example/thermostat-1.json"
    print(dtmi_conventions.get_model_uri(dtmi, repo_uri, expanded=True))
    # Prints: "file:///path/to/repository/dtmi/com/example/thermostat-1.expanded.json"

    # Remote repository example
    repo_uri = "https://contoso.com/models/"
    print(dtmi_conventions.get_model_uri(dtmi, repo_uri))
    # Prints: "https://contoso/com/models/dtmi/com/example/thermostat-1.json"
    print(dtmi_conventions.get_model_uri(dtmi, repo_uri, expanded=True))
    # Prints: "https://contoso/com/models/dtmi/com/example/thermostat-1.expanded.json"
