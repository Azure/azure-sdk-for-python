This file claims the rules how Python decide next version number for package.

The package version contains two part:
1. the package is preview or stable?
2. version number

# How to judge preview or stable?
Python SDK is generated with [swagger](https://github.com/Azure/azure-rest-api-specs), so if swagger content is preview, 
the package is preview; if swagger content is stable, the package is stable.

(1) For single api package(for example: [datadog](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/datadog)),
 as long as the current tag is preview, the package version should be preview

(2) For multi api package(for example: [network](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/network/azure-mgmt-network)), 
there will be `DEFAULT_API_VERSION`(for example: [`DEFAULT_API_VERSION` of network](https://github.com/Azure/azure-sdk-for-python/blob/59709af16b7cd29a51d562137bc5bbfdf53f9327/sdk/network/azure-mgmt-network/azure/mgmt/network/_network_management_client.py#L60)). 
As long as it is preview, then the package version is preview.

(note1: If the name of tag contains 'preview' or the tag contains files of 'preview' folder, then the tag is preview tag. 
For exampe: [preview tag](https://github.com/Azure/azure-rest-api-specs/tree/main/specification/compute/resource-manager#tag-package-2021-06-01-preview))

(note2: If the api-version contains 'preview', then it is preview api-version. for example: [preview api-version](https://github.com/Azure/azure-rest-api-specs/blob/69eacf00a36d565d3220d5dd6f4a5293664f1ae9/specification/network/resource-manager/Microsoft.Network/preview/2015-05-01-preview/network.json#L6))

(note3: The difference about single api and multi api, please see the detailed file)

(note4: preview package version contains `b`, for example: `1.0.0b1`)

# How to decide next version number
1\. If current version is preview version, the new tag is preview tag, then next version is `x.x.xbx+1`

2\. If current version is stable version, the new tag is stable tag, then :
 * if there is breaking change, next version is `x+1.x.x`
 * if there is new feature but no breaking change, next version is `x.x+1.x`
 * if there is only bugfix, next version is `x.x.x+1`

3\. If current version is stable version, the new tag is preview tag, calculate version number according to `2` 
and then append `b1` in the result


According to the up rules, we could summarize all the possibilities in the following table:

![img.png](version_summary.png)

(`-` means that this item doesn't influence result)
 