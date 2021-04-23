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
from azure.core.exceptions import (
    ResourceNotFoundError,
    ServiceRequestError,
    ServiceResponseError,
    HttpResponseError,
)
import pprint

dtmi = "dtmi:com:example:TemperatureController;1"
dtmi2 = "dtmi:com:example:TemperatureController;2"

# By default the clients in this sample will use the Azure Device Models Repository endpoint
# i.e. https://devicemodels.azure.com/
# See client_configuration_sample.py for examples of alternate configurations


def get_model():
    # This API call will return a dictionary mapping DTMI to its corresponding model from
    # a DTDL document at the specified endpoint
    # i.e. https://devicemodels.azure.com/dtmi/com/example/temperaturecontroller-1.json
    with ModelsRepositoryClient() as client:
        model_map = client.get_models(dtmi)
        pprint.pprint(model_map)


def get_models():
    # This API call will return a dictionary mapping DTMIs to corresponding models for from the
    # DTDL documents at the specified endpoint
    # i.e. https://devicemodels.azure.com/dtmi/com/example/temperaturecontroller-1.json
    # i.e. https://devicemodels.azure.com/dtmi/com/example/temperaturecontroller-2.json
    with ModelsRepositoryClient() as client:
        model_map = client.get_models([dtmi, dtmi2])
        pprint.pprint(model_map)


def get_model_expanded_dtdl():
    # This API call will return a dictionary mapping DTMIs to corresponding models for all elements
    # of an expanded DTDL document at the specified endpoint
    # i.e. https://devicemodels.azure.com/dtmi/com/example/temperaturecontroller-1.expanded.json
    with ModelsRepositoryClient() as client:
        model_map = client.get_models(
            dtmis=[dtmi], dependency_resolution=DEPENDENCY_MODE_TRY_FROM_EXPANDED
        )
        pprint.pprint(model_map)


def get_model_and_dependencies():
    # This API call will return a dictionary mapping the specified DTMI to its corresponding model,
    # from a DTDL document at the specified endpoint, as well as the DTMIs and models for all
    # dependencies on components and interfaces
    # i.e. https://devicemodels.azure.com/dtmi/com/example/temperaturecontroller-1.json
    with ModelsRepositoryClient() as client:
        model_map = client.get_models(dtmis=[dtmi], dependency_resolution=DEPENDENCY_MODE_ENABLED)
        pprint.pprint(model_map)


def get_model_error_handling():
    # Various errors that can be raised when fetching models
    try:
        with ModelsRepositoryClient() as client:
            model_map = client.get_models(dtmi)
            pprint.pprint(model_map)
    except ResourceNotFoundError as e:
        print("The model could not be found")
        print("{}".format(e.message))
    except ServiceRequestError as e:
        print("There was an error sending the request")
        print("{}".format(e.message))
    except ServiceResponseError as e:
        print("No response was received")
        print("{}".format(e.message))
    except HttpResponseError as e:
        print("HTTP Error Response received")
        print("{}".format(e.message))
