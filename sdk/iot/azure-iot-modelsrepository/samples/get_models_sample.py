# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from azure.iot.modelsrepository import (
    ModelsRepositoryClient,
    DEPENDENCY_MODE_TRY_FROM_EXPANDED,
    DEPENDENCY_MODE_ENABLED,
)
import pprint

dtmi = "dtmi:com:example:TemperatureController;1"
dtmi2 = "dtmi:com:example:TemperatureController;2"

# By default this client will use the Azure Device Models Repository endpoint
# i.e. https://devicemodels.azure.com/
# See client_configuration_sample.py for examples of alternate configurations
client = ModelsRepositoryClient()


def get_model():
    # This API call will return a dictionary mapping DTMI to its corresponding model from
    # a DTDL document at the specified endpoint
    # i.e. https://devicemodels.azure.com/dtmi/com/example/temperaturecontroller-1.json
    model_map = client.get_models([dtmi])
    pprint.pprint(model_map)


def get_models():
    # This API call will return a dictionary mapping DTMIs to corresponding models for from the
    # DTDL documents at the specified endpoint
    # i.e. https://devicemodels.azure.com/dtmi/com/example/temperaturecontroller-1.json
    # i.e. https://devicemodels.azure.com/dtmi/com/example/temperaturecontroller-2.json
    model_map = client.get_models([dtmi, dtmi2])
    pprint.pprint(model_map)


def get_model_expanded_dtdl():
    # This API call will return a dictionary mapping DTMIs to corresponding models for all elements
    # of an expanded DTDL document at the specified endpoint
    # i.e. https://devicemodels.azure.com/dtmi/com/example/temperaturecontroller-1.expanded.json
    model_map = client.get_models(
        dtmis=[dtmi], dependency_resolution=DEPENDENCY_MODE_TRY_FROM_EXPANDED
    )
    pprint.pprint(model_map)


def get_model_and_dependencies():
    # This API call will return a dictionary mapping the specified DTMI to it's corresponding model,
    # from a DTDL document at the specified endpoint, as well as the DTMIs and models for all
    # dependencies on components and interfaces
    # i.e. https://devicemodels.azure.com/dtmi/com/example/temperaturecontroller-1.json
    model_map = client.get_models(dtmis=[dtmi], dependency_resolution=DEPENDENCY_MODE_ENABLED)
    pprint.pprint(model_map)
