# Devtools Testutils

## Objects in this package for use with Azure Testing
* [`AzureMgmtTestCase`][azure_mgmt_testcase]: Base class for Management plane test classes
* [`AzureMgmtPreparer`][azure_mgmt_preparer]: Base class for Management-plane resource preparers
* [`AzureTestCase`][azure_testcase]: Base class for data plane test classes
* [`is_live`][is_live]: Helper method for determining whether a test run is in live or playback mode
* [`get_region_override`][get_region_override]: Helper method for determining resource region
* [`FakeResource`][fake_resource]:
* [`ResourceGroupPreparer`][rg_preparer]:
* [`RandomNameResourceGroupPreparer`][random_name_rg_preparer]:
* [`CachedResourceGroupPreparer`][cached_rg_preparer]:
* [`FakeStorageAccount`][fake_storage_account]:
* [`StorageAccountPreparer`][storage_account_preparer]:
* [`CachedStorageAccountPreparer`][cached_storage_account_preparer]:
* [`KeyVaultPreparer`][kv_preparer]:
* [`EnvironmentVariableLoader`][env_loader]: Abstract preparer for delivering secrets from environment variables to individual tests
* [`RetryCounter`][retry_counter]: Object for counting retries on a request.
* [`ResponseCallback`][response_callback]: Object for mocking response callbacks.
* [`FakeCredential`][fake_credential]: Fake credential used for authenticating in playback mode.


<!-- LINKS -->
[azure_mgmt_testcase]: https://github.com/Azure/azure-sdk-for-python/blob/520ea7175e10a971eae9d3e6cd0735efd80447b1/tools/azure-sdk-tools/devtools_testutils/mgmt_testcase.py#L57
[azure_mgmt_preparer]: https://github.com/Azure/azure-sdk-for-python/blob/520ea7175e10a971eae9d3e6cd0735efd80447b1/tools/azure-sdk-tools/devtools_testutils/mgmt_testcase.py#L128
[azure_testcase]: https://github.com/Azure/azure-sdk-for-python/blob/520ea7175e10a971eae9d3e6cd0735efd80447b1/tools/azure-sdk-tools/devtools_testutils/azure_testcase.py#L104
[is_live]: https://github.com/Azure/azure-sdk-for-python/blob/520ea7175e10a971eae9d3e6cd0735efd80447b1/tools/azure-sdk-tools/devtools_testutils/azure_testcase.py#L77
[get_region_override]: https://github.com/Azure/azure-sdk-for-python/blob/520ea7175e10a971eae9d3e6cd0735efd80447b1/tools/azure-sdk-tools/devtools_testutils/azure_testcase.py#L87
[fake_resource]: https://github.com/Azure/azure-sdk-for-python/blob/master/tools/azure-sdk-tools/devtools_testutils/resource_testcase.py#L27
[rg_preparer]: https://github.com/Azure/azure-sdk-for-python/blob/520ea7175e10a971eae9d3e6cd0735efd80447b1/tools/azure-sdk-tools/devtools_testutils/resource_testcase.py#L30
[random_name_rg_preparer]: https://github.com/Azure/azure-sdk-for-python/blob/master/tools/azure-sdk-tools/devtools_testutils/resource_testcase.py#L119
[cached_rg_preparer]: https://github.com/Azure/azure-sdk-for-python/blob/master/tools/azure-sdk-tools/devtools_testutils/resource_testcase.py#L120
[fake_storage_account]: https://github.com/Azure/azure-sdk-for-python/blob/master/tools/azure-sdk-tools/devtools_testutils/storage_testcase.py#L25
[storage_account_preparer]: https://github.com/Azure/azure-sdk-for-python/blob/520ea7175e10a971eae9d3e6cd0735efd80447b1/tools/azure-sdk-tools/devtools_testutils/storage_testcase.py#L29
[cached_storage_account_preparer]: https://github.com/Azure/azure-sdk-for-python/blob/master/tools/azure-sdk-tools/devtools_testutils/storage_testcase.py#L140
[kv_preparer]: https://github.com/Azure/azure-sdk-for-python/blob/520ea7175e10a971eae9d3e6cd0735efd80447b1/tools/azure-sdk-tools/devtools_testutils/keyvault_preparer.py#L49
[env_loader]: https://github.com/Azure/azure-sdk-for-python/blob/main/tools/azure-sdk-tools/devtools_testutils/envvariable_loader.py#L15
[retry_counter]: https://github.com/Azure/azure-sdk-for-python/blob/ab7e7f1a7b2a6d7255abdc77a40e2d6a86c9de0a/tools/azure-sdk-tools/devtools_testutils/helpers.py#L6
[response_callback]: https://github.com/Azure/azure-sdk-for-python/blob/ab7e7f1a7b2a6d7255abdc77a40e2d6a86c9de0a/tools/azure-sdk-tools/devtools_testutils/helpers.py#L14
[fake_credential]: https://github.com/Azure/azure-sdk-for-python/blob/65ffc49fbdd0f4f83e68eb5c8e0c6d293f0569cd/tools/azure-sdk-tools/devtools_testutils/fake_credential.py