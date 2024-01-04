# ESRP Release Process

Up until [this PR](https://github.com/Azure/azure-sdk-for-python/pull/29004) the azure-sdk-for-python team released packages to `PyPI` using our own PyPI account. After that PR, our releases will be handled by the central ESRP team.

This process change should not affect the release process whatsoever. There will be no change in release experience. Owners will still queue an `internal` build for their service, then approve each individual package for release as necessary.

The primary visible effect of these release changes is that these packages will be published by the `Microsoft` pypi account, _not_  `azure-sdk` account that has been used until now.

Further details on ESRP release methods is available at [docs.opensource.microsoft.com](https://docs.opensource.microsoft.com/releasing/publish-binaries/python/).

## Break Glass - Yanking/Deleting

The quickest way to get a package yanked is to file an ICM. The process is documented [here](https://dev.azure.com/azure-sdk/internal/_wiki/wikis/internal.wiki/1035/ESRP-Release-Task?anchor=escalating-to-esrp).

If the ICM doesn't have a reaction in an hour or so, directly contact the `python` team via email @ `python@microsoft.com`.
