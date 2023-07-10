# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------


from typing import Dict, List, Optional

from azure.core.credentials import TokenCredential

from .._vendor.azure_resources import ResourceManagementClient


def get_resources_from_subscriptions(
    strQuery: str, credential: TokenCredential, subscription_list: Optional[List[str]] = None
):
    # If a subscription list is passed in, use it. Otherwise, get all subscriptions
    subsList = []
    if subscription_list is not None:
        subsList = subscription_list
    else:
        try:
            from azure.mgmt.resource import SubscriptionClient  # pylint: disable=import-error
        except ImportError as e:
            raise ImportError("azure-mgmt-resource is required to get all accessible subscriptions") from e

        subsClient = SubscriptionClient(credential)
        for sub in subsClient.subscriptions.list():
            subsList.append(sub.as_dict().get("subscription_id"))

    try:
        import azure.mgmt.resourcegraph as arg  # pylint: disable=import-error
    except ImportError as e:
        raise ImportError("azure-mgmt-resourcegraph is required query resources from subscriptions") from e

    # Create Azure Resource Graph client and set options
    argClient = arg.ResourceGraphClient(credential)
    argQueryOptions = arg.models.QueryRequestOptions(result_format="objectArray")

    # Create query
    argQuery = arg.models.QueryRequest(subscriptions=subsList, query=strQuery, options=argQueryOptions)

    # Allowing API version to be set is yet to be released by azure-mgmt-resourcegraph,
    # hence the commented out code below. This is the API version Studio UX is using.
    # return argClient.resources(argQuery, api_version="2021-03-01")

    return argClient.resources(argQuery)


def get_virtual_clusters_from_subscriptions(
    credential: TokenCredential, subscription_list: Optional[List[str]] = None
) -> List[Dict]:
    # cspell:ignore tolower
    strQuery = """resources
    | where type == 'microsoft.machinelearningservices/virtualclusters'
    | order by tolower(name) asc
    | project id, subscriptionId, resourceGroup, name, location, tags, type"""

    return get_resources_from_subscriptions(strQuery, credential, subscription_list).data


def get_generic_resource_by_id(
    arm_id: str, credential: TokenCredential, subscription_id: str, api_version: Optional[str] = None
) -> Dict:
    resource_client = ResourceManagementClient(credential, subscription_id)
    generic_resource = resource_client.resources.get_by_id(arm_id, api_version)

    return generic_resource.as_dict()


def get_virtual_cluster_by_name(
    name: str, resource_group: str, subscription_id: str, credential: TokenCredential
) -> Dict:
    arm_id = (
        f"/subscriptions/{subscription_id}/resourceGroups/{resource_group}"
        f"/providers/Microsoft.MachineLearningServices/virtualClusters/{name}"
    )

    # This is the API version Studio UX is using.
    return get_generic_resource_by_id(arm_id, credential, subscription_id, api_version="2021-03-01-preview")
