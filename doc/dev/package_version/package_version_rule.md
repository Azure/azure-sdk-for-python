This file claims the rules how Python calculate next package version number.

The package version contains two parts:

1. Package version shall be preview or stable
2. After 1 decided, how to calculate next package version

# Package version shall be preview or stable

If Python SDK contains preview api-version (like "2020-01-01-preview"), its version is preview; Otherwise, it should be stable.

(1) For single-api package(for example: [confidentialledger](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/confidentialledger/azure-mgmt-confidentialledger/azure/mgmt/confidentialledger/_configuration.py#L51)),
 as long as it contains preview api-version, the package version should be preview

(2) For multi-api package(for example: [kubernetesconfiguration](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/kubernetesconfiguration/azure-mgmt-kubernetesconfiguration)),
there will be `DEFAULT_API_VERSION`(for example: [`DEFAULT_API_VERSION` of kubernetesconfiguration](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/kubernetesconfiguration/azure-mgmt-kubernetesconfiguration/azure/mgmt/kubernetesconfiguration/_source_control_configuration_client.py#L56)).
As long as it is preview, then the package version is preview.

(note2: preview package version contains `b`, for example: `1.0.0b1`)

# How to calculate next package version
1\. If next version is preview and last version is preview: next version is `x.x.xbx+1`

2\. If next version is preview and last version is stable:
 * if there is breaking change, next version is `x+1.x.xb1`
 * if there is new feature but no breaking change, next version is `x.x+1.xb1`
 * if there is only bugfix, next version is `x.x.x+1b1`

3\. If next version is stable and last stable version exists:
 * if there is breaking change, next version is `x+1.x.x`
 * if there is new feature but no breaking change, next version is `x.x+1.x`
 * if there is only bugfix, next version is `x.x.x+1`

4\. If next version is stable and last stable version doesn't exist, then next version shall be first GA version `1.0.0`

According to the up rules, we could summarize all the possibilities in the following table:

![img.png](version_summary.png)

(`-` means that this item doesn't influence result)
