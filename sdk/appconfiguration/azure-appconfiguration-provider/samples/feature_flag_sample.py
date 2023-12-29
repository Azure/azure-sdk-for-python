# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------

from azure.appconfiguration.provider import load
import os
from sample_utilities import get_authority, get_audience, get_credential, get_client_modifications

endpoint = os.environ.get("APPCONFIGURATION_ENDPOINT_STRING")
authority = get_authority(endpoint)
audience = get_audience(authority)
credential = get_credential(authority)
kwargs = get_client_modifications()

# Connecting to Azure App Configuration using AAD, selects [] results in no configuration settings loading
# By default, feature flags with no label are loaded when feature_flag_enabled is set to True
config = load(endpoint=endpoint, credential=credential, selects=[], feature_flag_enabled=True, **kwargs)

print(config["FeatureManagement"]["Alpha"])
print(config["FeatureManagement"]["Beta"])
print(config["FeatureManagement"]["Targeting"])
