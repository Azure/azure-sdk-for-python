# Release History

## 1.0.0b1 (2022-10-13)

New Azure App Configuration Provider

Provides additional support above the Azure App Configuration SDK. Enables:
* Connecting to an Azure App Configuration store
* Selecting multiple keys using Setting Selector
* Resolve Key Vault References when supplied AzureAppConfigurationKeyVaultOptions

The Azure App Configuration Provider once loaded returns a dictionary of key/value pairs to use in configuration.

```python
endpoint = "https://<your-store>.azconfig.io"
default_credential = DefaultAzureCredential()
config = AzureAppConfigurationProvider.load(
    endpoint=endpoint, credential=default_credential)
print(config["message"])
```