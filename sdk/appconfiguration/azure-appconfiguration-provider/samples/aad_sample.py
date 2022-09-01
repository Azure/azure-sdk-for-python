from azure.appconfigurationprovider import (
    AzureAppConfigurationProvider,
    SettingSelector
)
from azure.identity import DefaultAzureCredential
import os

endpoint = os.environ.get("AZURE_APPCONFIG_ENDPOINT")
credential = DefaultAzureCredential()

# Connecting to Azure App Configuration using AAD
config = AzureAppConfigurationProvider.load(
    endpoint=endpoint, credential=credential)

print(config["message"])

# Connecting to Azure App Configuration using AAD and trimmed key prefixes
trimmed = {"test."}
config = AzureAppConfigurationProvider.load(
    endpoint=endpoint, credential=credential, trimmed_key_prefixes=trimmed)

print(config["message"])

# Connection to Azure App Configuration using SettingSelector
selects = {SettingSelector("message*", "\0")}
config = AzureAppConfigurationProvider.load(
    endpoint=endpoint, credential=credential, selects=selects)

print("message found: " + str(config.has_key("message")))
print("test.message found: " + str(config.has_key("config.message")))
