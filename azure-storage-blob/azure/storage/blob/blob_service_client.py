# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------


class BlobServiceClient(object):

    def __init__(self, url, credentials=None, configuration=None):
        pass

    @staticmethod
    def create_configuration(**kwargs):
        pass

    def make_url(self, protocol=None, sas_token=None):
        pass

    def generate_shared_access_signature(self, resource_types, permission, expiry,
            start=None, ip=None, protocol=None):
        pass

    def get_account_information(self, timeout=None):
        """
        :returns: A dict of account information (SKU and account type).
        """
        pass

    def get_service_stats(self, timeout=None):
        """
        :returns ServiceStats.
        """
        pass

    def get_service_properties(self, timeout=None):
        """
        :returns: A dict of service properties.
        """
        pass

    def set_service_properties(self, logging=None, hour_metrics=None, minute_metrics=None,
            cors=None, target_version=None, timeout=None, delete_retention_policy=None,
            static_website=None):
        """
        :returns: None
        """
        pass

    def list_container_properties(self, prefix=None, num_results=None, include_metadata=False,
            marker=None, timeout=None):
        """
        :returns: An iterable (auto-paging) of ContainerProperties.
        """
        pass

    def get_container_client(self, container):
        """
        :returns: A ContainerClient.
        """
        pass