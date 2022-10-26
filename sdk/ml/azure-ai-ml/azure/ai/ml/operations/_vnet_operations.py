# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

from sys import prefix
import requests
import json
from azure.core.credentials import TokenCredential
from azure.ai.ml._scope_dependent_operations import OperationConfig, OperationScope, _ScopeDependentOperations, OperationsContainer
from azure.ai.ml.constants._common import AZUREML_RESOURCE_PROVIDER, NAMED_RESOURCE_ID_FORMAT, AzureMLResourceType
from typing import TYPE_CHECKING, Any, Callable, Dict, Iterable, Optional, Union
from azure.ai.ml._utils.utils import (
    create_requests_pipeline_with_retry,
    download_text_from_url
)
from azure.ai.ml.entities import SynapseVnetPE, PrivateLinkServiceTargetResource

class VNetOperations(_ScopeDependentOperations):
    """VNetOperations.

    You should not instantiate this class directly. Instead, you should
    create an MLClient instance that instantiates it for you and
    attaches it as an attribute.
    """

    def __init__(
        self,
        operation_scope: OperationScope,
        operation_config: OperationConfig,
        credential: TokenCredential,
        all_operations: OperationsContainer,
        **kwargs: Any,
    ):
        super(VNetOperations, self).__init__(operation_scope, operation_config)
        self.kwargs = kwargs        
        self._all_operations = all_operations
        self._credential = credential
        self._api_base_url = None
        self._requests_pipeline: HttpPipeline = kwargs.pop("requests_pipeline")
    
    def CreateVnet(self):
        """Create VNet.

        This Api will associate VNet with scoped workspace in scoped subscription
        """
        path = f"http://localhost:22425/sparkvnet/v1.0/subscriptions/{self._operation_scope.subscription_id}/resourceGroups/{self._operation_scope.resource_group_name}/providers/Microsoft.MachineLearningServices/workspaces/{self._operation_scope.workspace_name}/managedvnet"
        print(path)        
        url = self._api_url("managedvnet")
        print(url)
        extra_headers= self._get_header()
        x = requests.put(url = path, headers = extra_headers)
        print(x.text)       
        print(x)

    def GetVnet(self):
        """Get VNet.

        This Api will return associated VNet with scoped workspace in scoped subscription
        """
        path = f"http://localhost:22425/sparkvnet/v1.0/subscriptions/{self._operation_scope.subscription_id}/resourceGroups/{self._operation_scope.resource_group_name}/providers/Microsoft.MachineLearningServices/workspaces/{self._operation_scope.workspace_name}/managedvnet"
        print(path)        
        url = self._api_url("managedvnet")
        print(url)
        extra_headers= self._get_header()
        x = requests.get(url = path, headers = extra_headers)
        print(x.text)       
        print(x)

    def DeleteVnet(self):
        """Delete VNet.

        This Api will disassociate VNet from scoped workspace in scoped subscription
        """
        path = f"http://localhost:22425/sparkvnet/v1.0/subscriptions/{self._operation_scope.subscription_id}/resourceGroups/{self._operation_scope.resource_group_name}/providers/Microsoft.MachineLearningServices/workspaces/{self._operation_scope.workspace_name}/managedvnet"
        print(path)        
        url = self._api_url("managedvnet")
        print(url)
        extra_headers= self._get_header()
        x = requests.delete(url = path, headers = extra_headers)
        print(x.text)       
        print(x)

    def CreatePE(self, name, plsResourceObject):
        """Create PE for managed Vnet.

        This Api will create PE for VNet associated with scoped workspace in scoped subscription
        :param name: Name of the PE
        :type name: str
        :param name: plsResourceObject is object of Private Linked Service Details
        :type name: SynapseVnetPE
        """
        path = f"http://localhost:22425/sparkvnet/v1.0/subscriptions/{self._operation_scope.subscription_id}/resourceGroups/{self._operation_scope.resource_group_name}/providers/Microsoft.MachineLearningServices/workspaces/{self._operation_scope.workspace_name}/privateEndpoints/vjPE"
        print(path)
        plsResource = plsResourceObject._to_rest_object()
        print(plsResource)
        url = self._api_url("privateEndpoints/")
        print(url+name)
        extra_headers= self._get_header()
        x = requests.put(url = path, headers = extra_headers, json = plsResource)
        print(x.text)       
        print(x)

    def GetPE(self, name):
        """Get PE with provided name associated with workspave vnet.

        This Api will get PE for VNet associated with scoped workspace in scoped subscription
        :param name: Name of the PE
        :type name: str
        """
        path = f"http://localhost:22425/sparkvnet/v1.0/subscriptions/{self._operation_scope.subscription_id}/resourceGroups/{self._operation_scope.resource_group_name}/providers/Microsoft.MachineLearningServices/workspaces/{self._operation_scope.workspace_name}/privateEndpoints/vjPE"
        print(path)
        url = self._api_url("privateEndpoints/")
        print(url+name)
        extra_headers= self._get_header()
        x = requests.get(url = path, headers = extra_headers)
        print(x.text)       
        print(x)

    def ListPE(self):
        """List PE associated with workspave vnet.

        This Api will list PE for VNet associated with scoped workspace in scoped subscription
        """
        path = f"http://localhost:22425/sparkvnet/v1.0/subscriptions/{self._operation_scope.subscription_id}/resourceGroups/{self._operation_scope.resource_group_name}/providers/Microsoft.MachineLearningServices/workspaces/{self._operation_scope.workspace_name}/privateEndpoints"
        print(path)
        url = self._api_url("privateEndpoints")
        print(url)
        extra_headers= self._get_header()
        x = requests.get(url = path, headers = extra_headers)
        print(x.text)       
        print(x)

    def DeletePE(self, name):
        """Delete PE with provided name and associated with workspave vnet.

        This Api will delete PE from VNet associated with scoped workspace in scoped subscription
        :param name: Name of the PE
        :type name: str
        """
        path = f"http://localhost:22425/sparkvnet/v1.0/subscriptions/{self._operation_scope.subscription_id}/resourceGroups/{self._operation_scope.resource_group_name}/providers/Microsoft.MachineLearningServices/workspaces/{self._operation_scope.workspace_name}/privateEndpoints/vjPE"
        print(path)
        url = self._api_url("privateEndpoints/")
        print(url+name)
        extra_headers= self._get_header()
        x = requests.delete(url = path, headers = extra_headers)
        print(x.text)       
        print(x)

    def _api_url_prefix(self):
        if not self._api_base_url:
            self._api_base_url = self._get_workspace_url(url_key='api')
        return self._api_base_url
        
    def _get_workspace_url(self, url_key="history"):
        discovery_url = (
            self._all_operations.all_operations[AzureMLResourceType.WORKSPACE]
            .get(self._operation_scope.workspace_name)
            .discovery_url
        )
        all_urls = json.loads(
            download_text_from_url(
                discovery_url, create_requests_pipeline_with_retry(requests_pipeline=self._requests_pipeline)
            )
        )
        return all_urls[url_key]

    def _api_url(self, suffix):
        prefix = self._api_url_prefix()
        resourceString = f"/sparkvnet/v1.0/subscriptions/{self._operation_scope.subscription_id}/resourceGroups/{self._operation_scope.resource_group_name}/providers/Microsoft.MachineLearningServices/workspaces/{self._operation_scope.workspace_name}/"
        url = prefix + resourceString + suffix
        return url
    
    def _get_header(self):
        aml_token = self._get_token()
        extra_headers={"Authorization": f"Bearer {aml_token}", 'content-type':'application/json'}
        return extra_headers

    def _get_token(self):
        return self._credential.get_token("https://management.core.windows.net/.default").token

       