# # coding=utf-8
# # ------------------------------------
# # Copyright (c) Microsoft Corporation.
# # Licensed under the MIT License.
# # ------------------------------------
# import functools
# import os
# import pytest
# import six

# from devtools_testutils import AzureTestCase, PowerShellPreparer

# from azure.containerregistry import (
#     ContainerRegistryClient,
#     ContainerRepositoryClient,
#     DeletedRepositoryResult,
#     ACRExchangeClient
# )
# from azure.core.exceptions import ResourceNotFoundError
# from azure.core.paging import ItemPaged
# from azure.identity import DefaultAzureCredential

# from testcase import ContainerRegistryTestClass


# acr_preparer = functools.partial(
#     PowerShellPreparer,
#     "containerregistry",
#     containerregistry_baseurl="fake_url.azurecr.io",
# )


# class TestExchangeClient(ContainerRegistryTestClass):

#     def create_exchange_client(self, endpoint):
#         return self.create_client_from_credential(
#             ACRExchangeClient,
#             credential=self.get_credential(),
#             endpoint=endpoint,
#         )

#     @pytest.mark.skip("not needed")
#     @acr_preparer()
#     def test_exchange_client(self, containerregistry_baseurl):
#         client = self.create_exchange_client(containerregistry_baseurl)

#         service = "seankane.azurecr.io"
#         scope = "repository:hello-world:metadata_read"

#         refresh_token = client.exchange_aad_token_for_refresh_token(service, scope)
#         assert refresh_token is not None
#         assert len(refresh_token) > 100
#         print(refresh_token)


#         access_token = client.exchange_refresh_token_for_access_token(service, scope, refresh_token)
#         assert access_token is not None
#         assert len(access_token) > 100
#         print(access_token)