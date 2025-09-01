# Get Private Package

This guide is to help Python SDK users to get private package. Just follow the steps:

## 1. Confirm default tag

Make sure your target tag is defined in `readme.md` and **default tag is same with your target tag**. For example:

[azure-rest-api-specs/specification/network/resource-manager at main · Azure/azure-rest-api-specs (github.com)](https://github.com/Azure/azure-rest-api-specs/tree/main/specification/network/resource-manager#basic-information)

![](default_tag.png)

## 2.Trigger pipeline

Submit a PR or draft  PR to [Azure/azure-rest-api-specs](https://github.com/Azure/azure-rest-api-specs)

![](unreleased_package_guide_example1.png)

## 3.Get private package

Wait until pipelines finish, then there will be wheel and zip of the package. Just Click to download them.

![](unreleased_package_guide_example2.png)

If there is no link in the figure above, it may be folded. You can also find it in the `Checks`.

![img.png](unreleased_package_guide_example3.png)

## 4.Build private package locally (backup solution)

Because of security issue, maybe there is no private link to download. Since there is still auto generated PR provided, you can build the private package locally based on the PR with [guidance](https://github.com/Azure/azure-sdk-for-python/wiki/Common-issues-about-Python-SDK#build-private-package-with-pr)

![img.png](auto_gen_PR.png)

# Note

## 1.private repo

In private repo [Azure/azure-rest-api-specs-pr](https://github.com/Azure/azure-rest-api-specs-pr), pipeline can be triggered **only when the target branch is `main`**
