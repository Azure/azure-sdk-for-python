# ESRP Release Process

Up untill [this PR](https://github.com/Azure/azure-sdk-for-python/pull/29004) the azure-sdk-for-python team released packages to `PyPI` using our own PyPI account. After that PR, our releases will be handled by the central ESRP team.

This process change should not affect the release process whatsoever. There will be no change in release experience. Owners will still queue an `internal` build for their service, then approve each individual package for release as necessary.

The primary visible effect of these release changes is that these packages will be published by the `Microsoft` pypi account, _not_  `azure-sdk` account that has been used till now.

## Break Glass - Yanking/Deleting

Contact the `python` team via email, teams, or ICM: `python@microsoft.com`.
