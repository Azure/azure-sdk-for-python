# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from azure.iot.modelsrepository import ModelsRepositoryClient
import os


def default_client():
    # By default, this client will be configured for the Azure Device Models Repository
    # i.e. https://devicemodels.azure.com/
    client = ModelsRepositoryClient()
    return client


def use_remote_repository():
    # You can specify a custom remote endpoint where your Models Repository is located
    client = ModelsRepositoryClient(repository_location="https://constoso.com/models")
    return client


def use_local_repository():
    # You can also specify a custom local filesystem path where your Models Repository is located.
    # Paths can be specified as relative or absolute, as well as in URI format
    # This local repository path points to the SampleModelsRepo provided in this sample.
    test_dir = os.path.dirname(os.path.abspath(__file__))
    local_repo = os.path.join(test_dir, "SampleModelsRepo")
    client = ModelsRepositoryClient(repository_location=local_repo)
    return client
