# Release History

## 1.0.0b2 (2020-09-22)

**General breaking changes**

Learn more about migrating to the next generation of the Azure Python SDK in the [migration guide for resource management](https://github.com/Azure/azure-sdk-for-python/blob/master/doc/sphinx/python_mgmt_migration_guide.rst)

- Credential system has been completly revamped:

  - `azure.common.credentials` or `msrestazure.azure_active_directory` instances are no longer supported, use the `azure-identity` classes instead: https://pypi.org/project/azure-identity/

- An explicit ``begin_`` prefix is added for all the async APIs operations

## 1.0.0b1 (2020-09-22)

* Initial Release
