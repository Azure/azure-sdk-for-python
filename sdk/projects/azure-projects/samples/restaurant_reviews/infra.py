# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License in the project root for
# license information.
# --------------------------------------------------------------------------

from azure.projects import AzureInfrastructure
from azure.projects.resources.storage.tables.table import Table
from azure.projects.resources.appservice.site import AppSite


class RestaurantReviewInfra(AzureInfrastructure):
    restaurant_data: Table = Table(name="restaurants")
    review_data: Table = Table(name="reviews")


def build_infra() -> AzureInfrastructure:
    return RestaurantReviewInfra(host=AppSite())
