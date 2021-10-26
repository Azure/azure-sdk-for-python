# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from azure.iot.modelsrepository import ModelsRepositoryClient
import os


def default_client():
    # type: () -> ModelsRepositoryClient
    # By default, this client will be configured for the Azure Device Models Repository
    # i.e. https://devicemodels.azure.com/
    client = ModelsRepositoryClient()
    return client


def use_remote_repository():
    # type: () -> ModelsRepositoryClient
    # You can specify a custom remote endpoint where your Models Repository is located
    client = ModelsRepositoryClient(repository_location="https://constoso.com/models")
    return client


def use_local_repository():
    # type: () -> ModelsRepositoryClient
    # You can also specify a custom local filesystem path where your Models Repository is located.
    # Paths can be specified as relative or absolute, as well as in URI format
    # This local repository path points to the SampleModelsRepo provided in this sample.
    test_dir = os.path.dirname(os.path.abspath(__file__))
    local_repo = os.path.join(test_dir, "SampleModelsRepo")
    client = ModelsRepositoryClient(repository_location=local_repo)
    return client


def use_client_disabled_metadata():
    # type: () -> ModelsRepositoryClient
    # ModelsRepositoryClientOptions supports configuration for how the client consumes
    # repository metadata with the metadata_expiration and metadata_enabled keyword arguments.
    # Specifying an expiration in the metadata options will set the minimum time span for which
    # the client will consider the initial fetched metadata state as stale.
    # When the client metadata state is stale, the next service operation that can make use
    # of metadata will first fetch and refresh the client metadata state prior to executing
    # the desired service operation.
    # The time span for which the client considers fetched metadata stale can be set to 1 hour
    # or 3600 seconds.
    client = ModelsRepositoryClient(metadata_expiration=3600)

    # Fetching metadata can be disabled by setting metadata_enabled keyword argument to false.
    client = ModelsRepositoryClient(metadata_enabled=False)
    return client
