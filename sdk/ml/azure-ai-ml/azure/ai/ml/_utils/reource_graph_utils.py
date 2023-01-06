# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------


import azure.mgmt.resourcegraph as arg
from azure.mgmt.resource import SubscriptionClient
from azure.core.credentials import TokenCredential
from typing import List, Dict


def get_resources_from_all_subscriptions (strQuery: str, credential:  TokenCredential):
    subsClient = SubscriptionClient(credential)
    subsList = []
    for sub in subsClient.subscriptions.list():
        subsList.append(sub.as_dict().get('subscription_id'))

    # Create Azure Resource Graph client and set options
    argClient = arg.ResourceGraphClient(credential)
    argQueryOptions = arg.models.QueryRequestOptions(result_format="objectArray")

    # Create query
    argQuery = arg.models.QueryRequest(subscriptions=subsList, query=strQuery, options=argQueryOptions)

    # Allowing API version to be set is yet to be released by azure-mgmt-resourcegraph
    # return argClient.resources(argQuery, api_version="2021-03-01") # This is the API version Studio UX is using, but why does it matter
    return argClient.resources(argQuery)


def get_vitual_clusters_from_all_subscriptions(credential:  TokenCredential) -> List[Dict]:
    strQuery = "resources | where type == 'microsoft.machinelearningservices/virtualclusters' | order by tolower(name) asc | project id, subscriptionId, resourceGroup, name, location, tags, type"
    return get_resources_from_all_subscriptions(strQuery, credential).data
