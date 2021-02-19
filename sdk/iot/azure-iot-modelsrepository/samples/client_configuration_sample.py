# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from azure.iot.modelsrepository import ModelsRepositoryClient
from azure.core.pipeline.transport import RequestsTransport
from azure.core.pipeline.policies import UserAgentPolicy, RetryPolicy


def default_client():
    # By default, this client will be configured for the Azure Device Models Repository
    # i.e. https://devicemodels.azure.com/
    client = ModelsRepositoryClient()


def use_remote_repository():
    # You can specify a custom remote endpoint where your Models Repository is located
    client = ModelsRepositoryClient(repository_location="https://fake.myrepository.com/")


def use_local_repository():
    # You can also specify a custom local filesystem path where your Models Repository is located.
    # Paths can be specified as relative or absolute, as well as in URI format
    client = ModelsRepositoryClient(repository_location="file://home/fake/myrepository")


def custom_policies():
    # You can customize policies for remote operations in the client by passing through kwargs.
    # Please refer to documentation for the azure.core libraries for reference on all the possible
    # policy options.
    user_agent_policy = UserAgentPolicy("myuseragent")
    retry_policy = RetryPolicy(retry_total=10)
    client = ModelsRepositoryClient(user_agent_policy=user_agent_policy, retry_policy=retry_policy)


def custom_transport():
    # You can supply your own transport for remote operations in the client by passing through
    # kwargs. Please refer to documentation for the azure.core libraries for reference on the
    # possible transport options.
    transport = RequestsTransport(use_env_settings=False)
    client = ModelsRepositoryClient(transport=transport)
