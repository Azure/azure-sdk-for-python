# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from azure.iot.modelsrepository import (
    ModelsRepositoryClient,
    DependencyModeType,
)
from azure.core.exceptions import (
    ResourceNotFoundError,
    ServiceRequestError,
    ServiceResponseError,
    HttpResponseError,
)
from .client_configuration_sample import use_local_repository
import pprint

#Models
dtmi = "dtmi:com:example:TemperatureController;1"
dtmi2 = "dtmi:com:example:TemperatureController;2"
interaface_ouput= "DTMI(s) {0} resolved in {1} interface(s)."

# By default the remote clients in this sample will use the Azure Device Models Repository endpoint
# i.e. https://devicemodels.azure.com/
# The local clients in this sample will use the ./SampleModelRepo endpoint
# See client_configuration_sample.py for examples of alternate configurations


def get_model_from_global_repo():
    # This API call will return a dictionary mapping the specified DTMI to its corresponding model,
    # from a DTDL document at the specified endpoint, as well as the DTMIs and models for all
    # dependencies on components and interfaces
    # i.e. https://devicemodels.azure.com/dtmi/com/example/temperaturecontroller-1.json

    with ModelsRepositoryClient() as client:
        # The output of get_models() will include at least the definition for the target dtmi.
        # If the model dependency resolution configuration is not disabled, then models in which the
        # target dtmi depends on will also be included in the returned dictionary.
        model_dict = client.get_models(dtmi)

        # This call is the same as the previous call because the default parameter for dependency
        # resolution is DependencyModeType.enabled.value.
        # model_dict = client.get_models(dtmi, dependency_resolution=DependencyModeType.enabled.value)

        # In this case the above dtmi has 2 model dependencies.
        # dtmi:com:example:Thermostat;1 and dtmi:azure:DeviceManagement:DeviceInformation;1
        print(interaface_ouput.format(dtmi, len(model_dict)))

        # Print out actual contents
        pprint.pprint(model_dict)


def get_model_disabled_dependency_resolution():
    # This API call will return a dictionary mapping DTMI to its corresponding model from
    # a DTDL document at the specified endpoint
    # i.e. https://devicemodels.azure.com/dtmi/com/example/temperaturecontroller-1.json

    with ModelsRepositoryClient() as client:
        # In this example model dependency resolution is disabled by passing in
        # DependencyModeType.disabled.value as the value for the dependency_resolution parameter
        # for get_models(). By default the parameter has a value of DependencyModeType.enabled.value.
        # When model dependency resolution is disabled, only the input dtmi(s) will be processed
        # and model dependencies (if any) will be ignored.
        model_dict = client.get_models(dtmi, dependency_resolution=DependencyModeType.disabled.value)

        # In this case the above dtmi has 2 model dependencies but are not returned
        # due to disabling model dependency resolution.
        print(interaface_ouput.format(dtmi, len(model_dict)))

        # Print out actual contents
        pprint.pprint(model_dict)


def get_models_from_global_repo():
    # This API call will return a dictionary mapping DTMIs to corresponding models for from the
    # DTDL documents at the specified endpoint
    # i.e. https://devicemodels.azure.com/dtmi/com/example/temperaturecontroller-1.json
    # i.e. https://devicemodels.azure.com/dtmi/com/example/temperaturecontroller-2.json
    with ModelsRepositoryClient() as client:
        # When given a list of dtmis, the output of get_models() will include at
        # least the definitions of each dtmi in the list passed in.
        # If the model dependency resolution configuration is not disabled, then models in
        # which each dtmi depends on will also be included in the returned dictionary.
        model_dict = client.get_models([dtmi, dtmi2])

        # In this case the dtmi "dtmi:com:example:TemperatureController;1" has 2 model dependencies
        # and the dtmi "dtmi:com:example:azuresphere:sampledevice;1" has no additional dependencies.
        # The returned dictionary will include 4 models.
        print(
            interaface_ouput.format(
                ", ".join([dtmi, dtmi2]),
                len(model_dict)
            )
        )

        # Print out actual contents
        pprint.pprint(model_dict)


def get_model_from_local_repo():
    # This API call will return a dictionary mapping the specified DTMI to its corresponding model,
    # from a DTDL document at the specified local endpoint, as well as the DTMIs and models for all
    # dependencies on components and interfaces
    # i.e. ./SampleModelRepo/dtmi/com/example/temperaturecontroller-1.json

    with use_local_repository() as client:
        # The output of get_models() will include at least the definition for the target dtmi.
        # If the model dependency resolution configuration is not disabled, then models in which the
        # target dtmi depends on will also be included in the returned dictionary.
        model_dict = client.get_models(dtmi)

        # In this case the above dtmi has 2 model dependencies.
        # dtmi:com:example:Thermostat;1 and dtmi:azure:DeviceManagement:DeviceInformation;1
        print(interaface_ouput.format(dtmi, len(model_dict)))

        # Print out actual contents
        pprint.pprint(model_dict)


def get_model_not_found_error_global_repo():
    # Call to demonstrate a Resource Not Found Error that can be raised when fetching models.
    missing_model = "dtmi:com:example:NotFound;1"
    try:
        with ModelsRepositoryClient() as client:
            model_dict = client.get_models(missing_model)
            pprint.pprint(model_dict)
    except ResourceNotFoundError as e:
        print(
            "The model {} could not be found in the default public models repository".format(missing_model)
        )
        print("{}".format(e.message))


def get_model_not_found_error_local_repo():
    # Call to demonstrate a Resource Not Found Error that can be raised when fetching models.
    missing_model = "dtmi:com:example:NotFound;1"
    try:
        with use_local_repository() as client:
            model_dict = client.get_models(missing_model)
            pprint.pprint(model_dict)
    except ResourceNotFoundError as e:
        print("The model {} could not be found in the local models repository".format(missing_model))
        print("{}".format(e.message))


def get_model_invalid_dtmi():
    # Call to demonstrate an Invalid DTMI argument exeception that can be raised
    # when calling get_models().
    bad_dtmi = "dtmi:com:example:InvalidDtmi"
    try:
        with ModelsRepositoryClient() as client:
            model_dict = client.get_models(bad_dtmi)
            pprint.pprint(model_dict)
    except ValueError as e:
        print("The model dtmi format is invalid.")
        print("{}".format(e.message))


def get_model_error_handling():
    # Various other errors that can be raised when fetching models
    try:
        with ModelsRepositoryClient() as client:
            model_dict = client.get_models(dtmi)
            pprint.pprint(model_dict)
    except ServiceRequestError as e:
        print("There was an error sending the request")
        print("{}".format(e.message))
    except ServiceResponseError as e:
        print("No response was received")
        print("{}".format(e.message))
    except HttpResponseError as e:
        print("HTTP Error Response received")
        print("{}".format(e.message))
