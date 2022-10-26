# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Dict, List
from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml._utils.utils import load_yaml
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY, TYPE
from azure.ai.ml.entities._util import load_from_dict
import json
class PrivateLinkServiceTargetResource:
    """Private LinkService Target Resource"""

    def __init__(self, *, groupId: str = None, fqdns: List[str] = None):
        """Private LinkService Target Resource for synapse spark vnet
        """
        self.groupId = groupId
        self.fqdns = fqdns

    def _to_pls_resource_rest(self):
        plsTarget = PrivateLinkServiceTargetResource(
            groupId=self.groupId,
            fqdns=self.fqdns
        )
        return plsTarget.__dict__

@experimental
class SynapseVnetPE():
    """SynapseSpark vnet private linked service resource for creation of PE on vnet for provided pls
        :param name: IsSystemResource. True when private link service is  system resource. Only synapse resource are system resource [Default is False]
        :type name: bool
        :param name: IsAutoApproval. PE created always approved by admin and can be set to true for auto approve [Default is False]
        :type name: bool
        :param name: PrivateLinkServiceResourceId. private link service resource Id. Its required field and setto None by default
        :type name: str
        :param name: PrivateLinkServiceTargetResources. List of resources and its details under private link service
        :type name: PrivateLinkServiceTargetResource
        :param name: RequestMessage. Request message when PE created and request go to admin for approval [optional]
        :type name: str
    """

    def __init__(
        self,
        *,
        IsSystemResource: bool = False,
        IsAutoApproval: bool = False,
        PrivateLinkServiceResourceId: str = None,
        PrivateLinkServiceTargetResources: List[PrivateLinkServiceTargetResource] = None,
        RequestMessage: str = "Synapse Spark Managed VNet"
    ):
        self.IsSystemResource = IsSystemResource
        self.IsAutoApproval = IsAutoApproval
        self.PrivateLinkServiceResourceId = PrivateLinkServiceResourceId
        self.PrivateLinkServiceTargetResources = PrivateLinkServiceTargetResources
        self.RequestMessage = RequestMessage

   

    def _to_rest_object(self):
        rest_resource = [obj._to_pls_resource_rest() for obj in self.PrivateLinkServiceTargetResources]
        synapsespark_vnet = SynapseVnetPE(
            IsSystemResource=str(self.IsSystemResource).lower(),
            IsAutoApproval=str(self.IsAutoApproval).lower(),
            PrivateLinkServiceResourceId=self.PrivateLinkServiceResourceId,
            PrivateLinkServiceTargetResources=rest_resource,
            RequestMessage=self.RequestMessage,
        )
        return synapsespark_vnet.__dict__
