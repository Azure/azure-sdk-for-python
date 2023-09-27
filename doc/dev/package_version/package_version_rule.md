This file claims the rules how Python calculate next package version number.

The package version contains two parts:

1. Package version shall be preview or stable
2. After 1 decided, how to calculate next package version

# Package version shall be preview or stable

If Python SDK contains preview api-version (like "2020-01-01-preview"), its version is preview; Otherwise, it should be stable.

(1) For single-api package(for example: [confidentialledger](https://github.com/azure-sdk/azure-sdk-for-python/blob/a56c4b44911e173a89cb051aefc588e189e42654/sdk/confidentialledger/azure-mgmt-confidentialledger/azure/mgmt/confidentialledger/_configuration.py#L39)),
 as long as it contains preview api-version, the package version should be preview

(2) For multi-api package(for example: [network](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/network/azure-mgmt-network)), 
there will be `DEFAULT_API_VERSION`(for example: [`DEFAULT_API_VERSION` of network](https://github.com/Azure/azure-sdk-for-python/blob/0b3fb9ef0bee54f23beb7a4913faaaef5be90d9b/sdk/network/azure-mgmt-network/azure/mgmt/network/_network_management_client.py#L57)). 
As long as it is preview, then the package version is preview.

(note1: For more info about multi-api package, please refer to [multiapi.md](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/mgmt/multiapi.md))

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
 