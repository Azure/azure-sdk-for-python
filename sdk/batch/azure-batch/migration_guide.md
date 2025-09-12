# (WIP) Azure Batch Data Plane Migration Guide from <= v14.x to v15.x

This guide assists you in the migration from [azure-batch](https://pypi.org/project/azure-batch/) v14.x to [azure-batch](https://pypi.org/project/azure-batch/15.0.0b1/) v15.x. Side-by-side comparisons are provided for similar operations between the two packages.

Familiarity with the `azure-batch` v14.x package is assumed. If you're new to the Azure Batch client library for Python, see the [README for `azure-batch`](https://learn.microsoft.com/python/api/overview/azure/batch?view=azure-python) and samples instead of this guide.

## Table of Contents

- [Overview](#overview)
    - [Migration Benefits](#migration-benefits)
    - [Package Differences](#package-differences)
- [Additional Samples](#additional-samples)

## Overview

### Migration Benefits

> Note: `azure-batch` `<= v14.x` have been deprecated. Please upgrade to `azure-batch` `v15.x` for continued support.

A natural question to ask when considering whether to adopt a new version or library is what the benefits of doing so would be. As Azure has matured and been embraced by a more diverse group of developers, we've focused on learning the patterns and practices to best support developer productivity and to understand the gaps that the Python client libraries have.

Several areas of consistent feedback were expressed across the Azure client library ecosystem. One of the most important is that the client libraries for different Azure services haven't had a consistent approach to organization, naming, and API structure. Additionally, many developers have felt that the learning curve was too steep. The APIs didn't offer an approachable and consistent onboarding story for those learning Azure or exploring a specific Azure service.

To improve the development experience across Azure services, a set of uniform [design guidelines](https://azure.github.io/azure-sdk/general_introduction.html) was created for all languages to drive a consistent experience with established API patterns for all services. A set of [Python-specific guidelines](https://azure.github.io/azure-sdk/python/guidelines/index.html) was also introduced to ensure that Python clients have a natural and idiomatic feel with respect to the Python ecosystem. Further details are available in the guidelines.

The new Batch version `v15.x` provides the ability to share in some of the cross-service improvements made to the Azure development experience, such as using the new Azure.Identity library to share a single authentication between clients and a unified diagnostics pipeline offering a common view of the activities across each of the client libraries.

We strongly encourage moving to `azure-batch` `v15.x`. It is important to be aware that any version `<= v14.x` is officially deprecated. Though they will continue to be supported with critical security and bug fixes, they are no longer under active development and will not receive new features or minor fixes. There is no guarantee of feature parity between versions below `v14.x` and `v15.x`.

### Package Differences


## Additional Samples

For more samples, see