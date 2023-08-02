# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
from os import environ

from opentelemetry.sdk.resources import ResourceDetector, Resource
from opentelemetry.semconv.resource import ResourceAttributes, CloudPlatformValues, CloudProviderValues

from azure.monitor.opentelemetry.exporter._constants import (
    _CLOUD_RESOURCE_ID_RESOURCE_ATTRIBUTE,
    _REGION_NAME,
    _WEBSITE_SITE_NAME,
    _WEBSITE_HOME_STAMPNAME,
    _WEBSITE_HOSTNAME,
    _WEBSITE_INSTANCE_ID,
    _WEBSITE_OWNER_NAME,
    _WEBSITE_RESOURCE_GROUP,
    _WEBSITE_SLOT_NAME,
    _AZURE_APP_SERVICE_STAMP_RESOURCE_ATTRIBUTE,
)


_APP_SERVICE_ATTRIBUTE_ENV_VARS = {
    ResourceAttributes.CLOUD_REGION: _REGION_NAME,
    ResourceAttributes.DEPLOYMENT_ENVIRONMENT: _WEBSITE_SLOT_NAME,
    ResourceAttributes.HOST_ID: _WEBSITE_HOSTNAME,
    ResourceAttributes.SERVICE_INSTANCE_ID: _WEBSITE_INSTANCE_ID,
    _AZURE_APP_SERVICE_STAMP_RESOURCE_ATTRIBUTE: _WEBSITE_HOME_STAMPNAME,
}

class AzureAppServiceResourceDetector(ResourceDetector):
    def detect(self) -> "Resource":
        attributes = {}
        website_site_name = environ.get(_WEBSITE_SITE_NAME)
        if website_site_name:
            print(_WEBSITE_SITE_NAME)
            attributes[ResourceAttributes.SERVICE_NAME] = website_site_name
            attributes[ResourceAttributes.CLOUD_PROVIDER] = CloudProviderValues.AZURE.value
            attributes[ResourceAttributes.CLOUD_PLATFORM] = CloudPlatformValues.AZURE_APP_SERVICE.value

            azure_resource_uri = _get_azure_resource_uri(website_site_name)
            if azure_resource_uri:
                attributes[_CLOUD_RESOURCE_ID_RESOURCE_ATTRIBUTE] = azure_resource_uri
            for (key, env_var) in _APP_SERVICE_ATTRIBUTE_ENV_VARS.items():
                value = environ.get(env_var)
                if value:
                    attributes[key] = value

        print(attributes)
        return Resource(attributes)

def _get_azure_resource_uri(website_site_name):
    website_resource_group = environ.get(_WEBSITE_RESOURCE_GROUP)
    website_owner_name = environ.get(_WEBSITE_OWNER_NAME)

    subscription_id = website_owner_name
    if website_owner_name and '+' in website_owner_name:
        subscription_id = website_owner_name[0:website_owner_name.index('+')]

    if not (website_resource_group and subscription_id):
        return None

    return "/subscriptions/%s/resourceGroups/%s/providers/Microsoft.Web/sites/%s" % (
        subscription_id,
        website_resource_group,
        website_site_name,
    )
