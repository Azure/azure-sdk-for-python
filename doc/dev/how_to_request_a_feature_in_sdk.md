How to Request a Feature in SDK
======

This article aims to provide a guide for customers to request a feature in Azure Python SDK.

Python SDK is automatically generated based on rest API, so we generally do not recommend modifying SDK code manually. If you need a new function, but the SDK does not provide it, you need to open an issue in the [rest API](https://github.com/Azure/azure-rest-api-specs/issues) to describe clearly the feature you want.

Then, if the feature is adopted by the service team and the relevant rest API is updated, we will regenerate the SDK and release it after approved.


The overall workflow is:
1. Swagger and service ready
2. Azure Python SDK release (PyPI)


```
 ---------      ------------ 
|         |    |            | 
| Service | -> | Python SDK | 
|         |    |            |  
 ---------      ------------
```

This is the way that Azure Python SDK works with the Service team. Swagger PR should be merged before requesting azure Python SDK support.

Feel free to contact Azure CLI team at any time through any channels. We are passionate to build the world-class cloud product.
