# ESRP Release Process

Up until [this PR](https://github.com/Azure/azure-sdk-for-python/pull/29004) the azure-sdk-for-python team released packages to `PyPI` using our own PyPI account. After that PR, our releases will be handled by the central ESRP team.

This process change should not affect the release process whatsoever. There will be no change in release experience. Owners will still queue an `internal` build for their service, then approve each individual package for release as necessary.

The primary visible effect of these release changes is that these packages will be published by the `Microsoft` pypi account, _not_  `azure-sdk` account that has been used until now.

Further details on ESRP release methods is available at [docs.opensource.microsoft.com](https://docs.opensource.microsoft.com/releasing/publish-binaries/python/).

## Break Glass - Yanking/Deleting

For low priority yank requests, directly contact the `python` team via email @ `python@microsoft.com`. Ensure that the `package name`, the `version`, and the `yank reason` are readily available in the yank request email.

If an urgent yank or deletion request remains unanswered by email, follow the [ESRP escalation process](https://dev.azure.com/azure-sdk/internal/_wiki/wikis/internal.wiki/1035/ESRP-Release-Task?anchor=escalating-to-esrp) to file an ICM at severity 3, or severity 2 only if the request addresses a serious security issue.
